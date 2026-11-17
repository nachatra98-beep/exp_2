from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from habits.models import Habit, HabitLog
from datetime import date, timedelta

class Command(BaseCommand):
    help = 'Seeds demo user and habits matching the UI mockups'

    def handle(self, *args, **options):
        user, created = User.objects.get_or_create(
            username='Nachatra',
            defaults={
                'email': 'nachatra@example.com',
                'first_name': 'Nachatra'
            }
        )
        user.set_password('Password123!')
        user.save()

        # Clear existing habits for Nachatra to re-seed cleanly
        Habit.objects.filter(user=user).delete()

        today = date.today()

        habits_data = [
            {
                'name': 'Study for 1 hour',
                'description': 'Read course material and practice coding',
                'category': 'Study',
                'color': '#F59E0B',
                'icon': 'book',
                'frequency': 'Daily',
                'goal': '1 time per day',
                'completed_today': True,
                'streak_days': 7,
            },
            {
                'name': 'Drink 2L Water',
                'description': 'Keep hydrated with 8 full glasses',
                'category': 'Health',
                'color': '#3B82F6',
                'icon': 'water',
                'frequency': 'Daily',
                'goal': '1 time per day',
                'completed_today': True,
                'streak_days': 7,
            },
            {
                'name': 'Exercise',
                'description': 'Cardio, stretching or gym workout',
                'category': 'Fitness',
                'color': '#10B981',
                'icon': 'exercise',
                'frequency': 'Daily',
                'goal': '1 time per day',
                'completed_today': False,
                'streak_days': 6, # completed yesterday, pending today
            },
            {
                'name': 'Sleep Early',
                'description': 'Get into bed before 11:00 PM',
                'category': 'Health',
                'color': '#8B5CF6',
                'icon': 'moon',
                'frequency': 'Daily',
                'goal': '1 time per day',
                'completed_today': True,
                'streak_days': 7,
            },
        ]

        for h in habits_data:
            habit = Habit.objects.create(
                user=user,
                name=h['name'],
                description=h['description'],
                category=h['category'],
                color=h['color'],
                icon=h['icon'],
                frequency=h['frequency'],
                goal=h['goal']
            )

            # Create streak logs
            streak_days = h['streak_days']
            start_offset = 0 if h['completed_today'] else 1
            for day_offset in range(start_offset, streak_days + start_offset):
                log_date = today - timedelta(days=day_offset)
                HabitLog.objects.get_or_create(habit=habit, date=log_date)

        self.stdout.write(self.style.SUCCESS(f"Successfully seeded demo user 'Nachatra' (Password123!) with habits matching UI!"))
