from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Habit, HabitLog
from datetime import date, datetime

def get_app_user(request):
    if request and hasattr(request, 'user') and request.user.is_authenticated:
        return request.user
    user, _ = User.objects.get_or_create(
        username='Nachatra',
        defaults={'email': 'nachatra@example.com', 'first_name': 'Nachatra'}
    )
    return user

class HabitLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = HabitLog
        fields = ('id', 'habit', 'date', 'created_at')

class HabitSerializer(serializers.ModelSerializer):
    completed_today = serializers.SerializerMethodField()
    current_streak = serializers.SerializerMethodField()
    longest_streak = serializers.SerializerMethodField()

    class Meta:
        model = Habit
        fields = (
            'id', 'name', 'description', 'category', 'color', 'icon',
            'frequency', 'goal', 'reminder_time', 'is_active', 'created_at',
            'completed_today', 'current_streak', 'longest_streak'
        )
        read_only_fields = ('id', 'created_at', 'completed_today', 'current_streak', 'longest_streak')

    def get_reference_date(self):
        request = self.context.get('request')
        if request:
            # Check for ?date=YYYY-MM-DD or header X-Client-Date
            date_str = request.query_params.get('date') or request.headers.get('X-Client-Date')
            if date_str:
                try:
                    return datetime.strptime(date_str, '%Y-%m-%d').date()
                except ValueError:
                    pass
        return date.today()

    def get_completed_today(self, obj):
        ref_date = self.get_reference_date()
        stats = obj.calculate_streaks(ref_date)
        return stats['completed_today']

    def get_current_streak(self, obj):
        ref_date = self.get_reference_date()
        stats = obj.calculate_streaks(ref_date)
        return stats['current_streak']

    def get_longest_streak(self, obj):
        ref_date = self.get_reference_date()
        stats = obj.calculate_streaks(ref_date)
        return stats['longest_streak']

    def validate_name(self, value):
        request = self.context.get('request')
        user = get_app_user(request)
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Habit name is required.")

        # Check uniqueness per user, excluding self on update
        existing = Habit.objects.filter(user=user, name__iexact=value)
        if self.instance:
            existing = existing.exclude(id=self.instance.id)

        if existing.exists():
            raise serializers.ValidationError(f"You already have a habit named '{value}'.")
        return value

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['user'] = get_app_user(request)
        return super().create(validated_data)
