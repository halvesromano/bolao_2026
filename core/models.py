from django.db import models
from django.contrib.auth.models import User

class Team(models.Model):
    name = models.CharField(max_length=50)
    flag_code = models.CharField(max_length=10, help_text="ISO Code or Emoji", blank=True)
    logo = models.ImageField(upload_to='teams/', blank=True, null=True)

    def __str__(self):
        return self.name

class Match(models.Model):
    home_team = models.ForeignKey(Team, related_name='home_matches', on_delete=models.CASCADE)
    away_team = models.ForeignKey(Team, related_name='away_matches', on_delete=models.CASCADE)
    date = models.DateTimeField()
    round = models.IntegerField(default=1, verbose_name="Rodada")
    home_score = models.IntegerField(null=True, blank=True)
    away_score = models.IntegerField(null=True, blank=True)
    is_finished = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Matches"

    def __str__(self):
        return f"{self.home_team} vs {self.away_team} - {self.date.strftime('%d/%m %H:%M')}"

class Prediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, related_name='predictions', on_delete=models.CASCADE)
    home_score = models.IntegerField()
    away_score = models.IntegerField()
    points = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ('user', 'match')

    def __str__(self):
        return f"{self.user.username}: {self.home_score}-{self.away_score} for {self.match}"
