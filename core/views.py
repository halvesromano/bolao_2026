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
    matches = Match.objects.filter(is_finished=False).order_by('date')
    
    predictions = Prediction.objects.filter(user=request.user)
    pred_map = {p.match_id: p for p in predictions}
    
    upcoming_data = []
    for m in matches:
        deadline = m.date - timedelta(hours=1)
        is_locked = now > deadline
        upcoming_data.append({
            'match': m,
            'prediction': pred_map.get(m.id),
            'is_locked': is_locked,
            'deadline': deadline
        })
        
    past_matches = Match.objects.filter(is_finished=True).order_by('-date')
    past_data = []
    for m in past_matches:
        past_data.append({
            'match': m,
            'prediction': pred_map.get(m.id)
        })

    return render(request, 'core/dashboard.html', {
        'upcoming': upcoming_data,
        'past': past_data
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

def ranking(request):
    users = User.objects.annotate(total_points=Sum('prediction__points')).order_by('-total_points')
    results = []
    for u in users:
        results.append({
            'username': u.username,
            'points': u.total_points or 0
        })
    results.sort(key=lambda x: x['points'], reverse=True)
    return render(request, 'core/ranking.html', {'ranking': results})
