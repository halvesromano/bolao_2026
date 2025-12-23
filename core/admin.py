from django.contrib import admin
from .models import Team, Match, Prediction

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'flag_code')

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('round', 'home_team', 'away_team', 'date', 'home_score', 'away_score', 'is_finished')
    list_filter = ('is_finished', 'date', 'round')

@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ('user', 'match', 'home_score', 'away_score', 'points')
    list_filter = ('match', 'user')
