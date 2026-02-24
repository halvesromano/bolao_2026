from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.utils import timezone
from .models import Match, Prediction, Team

# ... (imports remain the same, just showing the change in the first line if I could, but I'll use separate chunks for clarity or just append the view)
# Actually, I will update the import first, then append the function.

@login_required
def championship_table(request):
    teams = Team.objects.all()
    table = []

    for team in teams:
        stats = {
            'team': team,
            'j': 0, 'v': 0, 'e': 0, 'd': 0,
            'gp': 0, 'gc': 0, 'sg': 0, 'pts': 0
        }
        
        # Get finished matches for this team
        home_matches = Match.objects.filter(home_team=team, is_finished=True)
        away_matches = Match.objects.filter(away_team=team, is_finished=True)
        
        for m in home_matches:
            stats['j'] += 1
            stats['gp'] += m.home_score
            stats['gc'] += m.away_score
            if m.home_score > m.away_score:
                stats['v'] += 1
                stats['pts'] += 3
            elif m.home_score == m.away_score:
                stats['e'] += 1
                stats['pts'] += 1
            else:
                stats['d'] += 1
                
        for m in away_matches:
            stats['j'] += 1
            stats['gp'] += m.away_score
            stats['gc'] += m.home_score
            if m.away_score > m.home_score:
                stats['v'] += 1
                stats['pts'] += 3
            elif m.away_score == m.home_score:
                stats['e'] += 1
                stats['pts'] += 1
            else:
                stats['d'] += 1
        
        stats['sg'] = stats['gp'] - stats['gc']
        table.append(stats)
        
    # Sort by Points (desc), Wins (desc), Goal Difference (desc), Goals For (desc)
    table.sort(key=lambda x: (x['pts'], x['v'], x['sg'], x['gp']), reverse=True)
    
    return render(request, 'core/championship_table.html', {'table': table})
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
    
    # Logic to find the default round
    # Priority: First round with at least one unfinished match
    first_unfinished = Match.objects.filter(is_finished=False).order_by('round', 'date').first()
    
    if first_unfinished:
        current_round_num = first_unfinished.round
    else:
        # If all matches are finished, show the last round available
        last_match = Match.objects.order_by('-round').first()
        current_round_num = last_match.round if last_match else 1

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
    
    # Logic to get all users for popover
    all_users = User.objects.filter(is_active=True).order_by('first_name', 'username')
    
    # Get set of users who predicted each match
    match_pred_users = {}
    all_preds_round = Prediction.objects.filter(match__in=matches).values('match_id', 'user_id')
    for p in all_preds_round:
        if p['match_id'] not in match_pred_users:
            match_pred_users[p['match_id']] = set()
        match_pred_users[p['match_id']].add(p['user_id'])

    upcoming_data = []
    past_data = []

    for m in matches:
        deadline = m.date - timedelta(hours=1)
        is_locked = now > deadline
        
        item = {
            'match': m,
            'prediction': pred_map.get(m.id),
            'is_locked': is_locked,
            'deadline': deadline,
            'predicted_user_ids': match_pred_users.get(m.id, set())
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
        'current_round': current_round_num,
        'all_users': all_users
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
    match_id = request.GET.get('match')

    if user_id:
        predictions = predictions.filter(user_id=user_id)
    if round_num:
        predictions = predictions.filter(match__round=round_num)
    if match_id:
        predictions = predictions.filter(match_id=match_id)

    # Context Data
    users = User.objects.all().order_by('username')
    rounds = Match.objects.exclude(round=None).values_list('round', flat=True).distinct().order_by('round')

    return render(request, 'core/all_predictions.html', {
        'predictions': predictions,
        'users': users,
        'rounds': rounds,
        'matches': viewable_matches.order_by('-date')
    })

@login_required
def prediction_status(request):
    # Fetch all users (ordered by name)
    users = User.objects.all().order_by('first_name', 'username')
    
    # Fetch all rounds that have matches
    rounds_query = Match.objects.exclude(round=None).values_list('round', flat=True).distinct().order_by('round')
    
    status_data = []
    
    for r in rounds_query:
        # Total matches in this round
        total_matches = Match.objects.filter(round=r).count()
        if total_matches == 0:
            continue
            
        round_info = {
            'round': r,
            'user_status': []
        }
        
        for u in users:
            # Count predictions for this user in this round
            pred_count = Prediction.objects.filter(user=u, match__round=r).count()
            is_complete = (pred_count == total_matches)
            
            round_info['user_status'].append({
                'user': u,
                'is_complete': is_complete,
                'progress': f"{pred_count}/{total_matches}"
            })
            
        status_data.append(round_info)
        
    return render(request, 'core/prediction_status.html', {'status_data': status_data})

@login_required
def submit_all_predictions(request):
    if request.method == 'POST':
        count = 0
        errors = 0
        
        # Iterate over all POST data to find score inputs
        # Inputs are expected to be named home_score_<match_id> and away_score_<match_id>
        for key, value in request.POST.items():
            if key.startswith('home_score_'):
                match_id = key.split('_')[2]
                home_score = value
                away_score = request.POST.get(f'away_score_{match_id}')
                
                # Skip valid empty inputs (user might intentionally not predict match X)
                if not home_score or not away_score:
                    continue
                    
                match = get_object_or_404(Match, id=match_id)
                deadline = match.date - timedelta(hours=1)
                
                # Verify deadline
                if timezone.now() > deadline:
                    errors += 1
                    continue
                
                try:
                    home = int(home_score)
                    away = int(away_score)
                    
                    Prediction.objects.update_or_create(
                        user=request.user, match=match,
                        defaults={'home_score': home, 'away_score': away}
                    )
                    count += 1
                except ValueError:
                    continue

        if count > 0:
            messages.success(request, f"{count} palpites salvos com sucesso!")
        elif errors > 0:
            messages.error(request, "Alguns jogos já encerraram o prazo para palpitar.")
        else:
            messages.info(request, "Nenhum palpite novo foi identificado.")
            
    return redirect('dashboard')

@login_required
def statistics(request):
    from django.db.models import Count, Sum, Q
    
    # 1. "Na Mosca" (Exact Scores - 10 points)
    exact_scores = User.objects.filter(prediction__points=10).annotate(
        hits=Count('prediction')
    ).order_by('-hits')[:5]

    # 2. "Zerou" (0 points in finished matches)
    # We must filter predictions for finished matches where points are 0
    zero_scores = User.objects.filter(
        prediction__match__is_finished=True, 
        prediction__points=0
    ).annotate(
        misses=Count('prediction')
    ).order_by('-misses')[:5]

    # 3. Points per round
    # We need a matrix: Rows = Users, Cols = Rounds, Cells = Total Points
    
    users = User.objects.all().order_by('first_name', 'username')
    rounds = Match.objects.exclude(round=None).values_list('round', flat=True).distinct().order_by('round')
    
    points_per_round = []
    
    for u in users:
        user_row = {'user': u, 'rounds': [], 'total': 0}
        total_points = 0
        for r in rounds:
            # Aggregate points for this user in this round
            r_points = Prediction.objects.filter(user=u, match__round=r).aggregate(s=Sum('points'))['s'] or 0
            user_row['rounds'].append({'round': r, 'points': r_points})
            total_points += r_points
        
        user_row['total'] = total_points
        points_per_round.append(user_row)
        
    # Sort by total points desc
    points_per_round.sort(key=lambda x: x['total'], reverse=True)

    return render(request, 'core/statistics.html', {
        'exact_scores': exact_scores,
        'zero_scores': zero_scores,
        'points_per_round': points_per_round,
        'rounds_list': rounds
    })
