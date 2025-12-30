from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.utils import timezone
from .models import Match, Prediction
from django.db.models import Sum
from datetime import timedelta
from django.contrib import messages

class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'core/password_change.html'
    success_url = reverse_lazy('dashboard')
    
    def form_valid(self, form):
        messages.success(self.request, "Sua senha foi alterada com sucesso!")
        return super().form_valid(form)

@login_required
def dashboard(request):
    now = timezone.now()
    
    # Logic to find the default round (closest to now)
    # We find the match with the smallest absolute time difference from now
    closest_match = None
    min_diff = None
    
    all_matches = Match.objects.all()
    # If there are no matches, default to round 1
    if not all_matches.exists():
        current_round_num = 1
    else:
        # Optimization: We could use specific DB queries, but for a small dataset iteration is okay.
        # Let's try to be efficient with DB:
        # Get the match closest in the past
        past_match = Match.objects.filter(date__lte=now).order_by('-date').first()
        # Get the match closest in the future
        future_match = Match.objects.filter(date__gt=now).order_by('date').first()
        
        candidates = []
        if past_match: candidates.append(past_match)
        if future_match: candidates.append(future_match)
        
        best_match = None
        if not candidates:
            # Should not happen if exists() was true, but fallback
            current_round_num = 1
        else:
            # Find closest
            best_match = min(candidates, key=lambda m: abs((m.date - now).total_seconds()))
            current_round_num = best_match.round

    # Allow user to override via GET parameter
    selected_round = request.GET.get('round')
    if selected_round:
        try:
            current_round_num = int(selected_round)
        except ValueError:
            pass # Keep default if invalid
            
    # Filter matches by the determined round
    matches = Match.objects.filter(round=current_round_num).order_by('date')
    
    # Get user predictions for these matches
    predictions = Prediction.objects.filter(user=request.user, match__round=current_round_num)
    pred_map = {p.match_id: p for p in predictions}
    
    upcoming_data = []
    past_data = []

    for m in matches:
        deadline = m.date - timedelta(hours=1)
        is_locked = now > deadline
        
        item = {
            'match': m,
            'prediction': pred_map.get(m.id),
            'is_locked': is_locked,
            'deadline': deadline
        }
        
        if m.is_finished:
            past_data.append(item)
        else:
            upcoming_data.append(item)
            
    # Get list of all available rounds for the dropdown
    rounds = Match.objects.exclude(round=None).values_list('round', flat=True).distinct().order_by('round')

    return render(request, 'core/dashboard.html', {
        'upcoming': upcoming_data,
        'past': past_data,
        'rounds': rounds,
        'current_round': current_round_num
    })

@login_required
def submit_prediction(request, match_id):
    if request.method == 'POST':
        match = get_object_or_404(Match, id=match_id)
        deadline = match.date - timedelta(hours=1)
        if timezone.now() > deadline:
            messages.error(request, "O tempo para palpitar neste jogo acabou!")
            return redirect('dashboard')
            
        try:
            home = int(request.POST.get('home_score'))
            away = int(request.POST.get('away_score'))
        except (ValueError, TypeError):
            messages.error(request, "Placar inválido.")
            return redirect('dashboard')
        
        Prediction.objects.update_or_create(
            user=request.user, match=match,
            defaults={'home_score': home, 'away_score': away}
        )
        messages.success(request, "Palpite salvo com sucesso!")
        
    return redirect('dashboard')

@login_required
def ranking(request):
    users = User.objects.annotate(total_points=Sum('prediction__points')).order_by('-total_points')
    results = []
    for u in users:
        results.append({
            'username': u.username,
            'full_name': u.get_full_name(),
            'points': u.total_points or 0
        })
    results.sort(key=lambda x: x['points'], reverse=True)
    return render(request, 'core/ranking.html', {'ranking': results})

@login_required
def all_predictions(request):
    # Only show predictions for matches where the deadline has passed (1 hour before match)
    now = timezone.now()
    # Logic: Match date < now + 1 hour (Wait... deadline is -1h. So if now > match.date - 1h, it is locked)
    # Locked matches: date - 1h < now  => date < now + 1h
    
    # Let's filter matches first
    # Matches that started (or are about to start in less than 1h)
    viewable_matches = Match.objects.filter(date__lte=now + timedelta(hours=1))
    
    predictions = Prediction.objects.filter(match__in=viewable_matches).select_related('match', 'user', 'match__home_team', 'match__away_team').order_by('-match__date')

    # Filters
    user_id = request.GET.get('user')
    round_num = request.GET.get('round')

    if user_id:
        predictions = predictions.filter(user_id=user_id)
    if round_num:
        predictions = predictions.filter(match__round=round_num)

    # Context Data
    users = User.objects.all().order_by('username')
    rounds = Match.objects.exclude(round=None).values_list('round', flat=True).distinct().order_by('round')

    return render(request, 'core/all_predictions.html', {
        'predictions': predictions,
        'users': users,
        'rounds': rounds
    })
