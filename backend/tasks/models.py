from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Task(models.Model):
    title = models.CharField(max_length=255)
    due_date = models.DateTimeField()
    estimated_hours = models.FloatField(validators=[MinValueValidator(0.25)])
    importance = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    dependencies = models.JSONField(default=list, blank=True)

    def __str__(self):
        return self.title
