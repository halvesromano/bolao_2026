from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Match, Prediction
from .utils import calculate_points

@receiver(post_save, sender=Match)
def update_prediction_points(sender, instance, **kwargs):
    """
    When a match is saved and marked as finished, update all related predictions.
    """
    if instance.is_finished and instance.home_score is not None and instance.away_score is not None:
        predictions = instance.predictions.all()
        for pred in predictions:
            pred.points = calculate_points(pred, instance)
            pred.save()
    else:
        # If match is not finished (or reopened), reset points to 0
        instance.predictions.all().update(points=0)
