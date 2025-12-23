from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('ranking/', views.ranking, name='ranking'),
    path('palpites/', views.all_predictions, name='all_predictions'),
    path('predict/<int:match_id>/', views.submit_prediction, name='submit_prediction'),
]
