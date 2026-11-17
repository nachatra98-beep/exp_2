from django.db import models
from django.contrib.auth.models import User
from datetime import date, timedelta

class Habit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='habits')
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255, blank=True, default='')
    category = models.CharField(max_length=50, blank=True, default='General')
    color = models.CharField(max_length=7, blank=True, default='#F59E0B')
    icon = models.CharField(max_length=50, blank=True, default='book')
    frequency = models.CharField(max_length=50, default='Daily')
    goal = models.CharField(max_length=50, default='1 time per day')
    reminder_time = models.TimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'name'], name='unique_user_habit_name')
        ]
        ordering = ['created_at']

    def __str__(self):
        return f"{self.name} ({self.user.username})"

    def calculate_streaks(self, reference_date=None):
        """
        Calculates current streak and longest streak according to SRS 4.4:
        - Current streak is count of consecutive days ending today (or yesterday if today is not completed)
        - If neither today nor yesterday has a check-in, current streak is 0.
        - Longest streak is maximum consecutive-day run across all check-ins.
        """
        if reference_date is None:
            reference_date = date.today()

        # Get sorted unique log dates
        log_dates = set(self.logs.values_list('date', flat=True))

        completed_today = reference_date in log_dates

        # Current streak calculation
        current_streak = 0
        if completed_today:
            check_date = reference_date
            while check_date in log_dates:
                current_streak += 1
                check_date -= timedelta(days=1)
        else:
            yesterday = reference_date - timedelta(days=1)
            if yesterday in log_dates:
                check_date = yesterday
                while check_date in log_dates:
                    current_streak += 1
                    check_date -= timedelta(days=1)
            else:
                current_streak = 0

        # Longest streak calculation
        longest_streak = 0
        if log_dates:
            sorted_dates = sorted(list(log_dates))
            temp_streak = 1
            longest_streak = 1
            for i in range(1, len(sorted_dates)):
                if sorted_dates[i] == sorted_dates[i - 1] + timedelta(days=1):
                    temp_streak += 1
                elif sorted_dates[i] > sorted_dates[i - 1] + timedelta(days=1):
                    temp_streak = 1
                if temp_streak > longest_streak:
                    longest_streak = temp_streak

        return {
            'completed_today': completed_today,
            'current_streak': current_streak,
            'longest_streak': longest_streak
        }


class HabitLog(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name='logs')
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['habit', 'date'], name='unique_habit_log_date')
        ]
        ordering = ['-date']

    def __str__(self):
        return f"{self.habit.name} - {self.date}"
