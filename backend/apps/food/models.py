from django.db import models
from django.contrib.auth.models import User


class Meal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meals')
    name = models.CharField(max_length=200)
    kcal = models.IntegerField()
    protein_g = models.FloatField()
    carbs_g = models.FloatField()
    fat_g = models.FloatField()
    photo = models.ImageField(upload_to='meals/', blank=True, null=True)
    logged_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-logged_at']

    def __str__(self):
        return f'{self.user.username} — {self.name} ({self.kcal} kcal)'


class UserFoodSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='food_settings')
    kcal_goal = models.IntegerField(default=2000)
    protein_goal_g = models.IntegerField(default=180)

    def __str__(self):
        return f'{self.user.username} — {self.kcal_goal} kcal goal'
