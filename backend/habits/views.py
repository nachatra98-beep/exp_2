from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Count
from django.contrib.auth.models import User
from datetime import date, datetime, timedelta
from .models import Habit, HabitLog
from .serializers import HabitSerializer, HabitLogSerializer, get_app_user

def parse_target_date(request):
    date_str = request.data.get('date') if hasattr(request, 'data') and isinstance(request.data, dict) else None
    if not date_str:
        date_str = request.query_params.get('date') or request.headers.get('X-Client-Date')
    if date_str:
        try:
            return datetime.strptime(str(date_str).strip(), '%Y-%m-%d').date()
        except ValueError:
            pass
    return date.today()

class HabitListCreateView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        user = get_app_user(request)
        habits = Habit.objects.filter(user=user, is_active=True)
        serializer = HabitSerializer(habits, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        serializer = HabitSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            habit = serializer.save()
            return Response(HabitSerializer(habit, context={'request': request}).data, status=status.HTTP_201_CREATED)
        return Response({
            'detail': 'Validation error',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class HabitDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get_object(self, pk, user):
        return get_object_or_404(Habit, pk=pk, user=user)

    def get(self, request, pk):
        user = get_app_user(request)
        habit = self.get_object(pk, user)
        serializer = HabitSerializer(habit, context={'request': request})
        return Response(serializer.data)

    def put(self, request, pk):
        user = get_app_user(request)
        habit = self.get_object(pk, user)
        serializer = HabitSerializer(habit, data=request.data, context={'request': request})
        if serializer.is_valid():
            habit = serializer.save()
            return Response(HabitSerializer(habit, context={'request': request}).data)
        return Response({
            'detail': 'Validation error',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        user = get_app_user(request)
        habit = self.get_object(pk, user)
        serializer = HabitSerializer(habit, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            habit = serializer.save()
            return Response(HabitSerializer(habit, context={'request': request}).data)
        return Response({
            'detail': 'Validation error',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        user = get_app_user(request)
        habit = self.get_object(pk, user)
        habit.delete()
        return Response({'detail': 'Habit deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)


class HabitCheckView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, pk):
        user = get_app_user(request)
        habit = get_object_or_404(Habit, pk=pk, user=user)
        target_date = parse_target_date(request)

        log, created = HabitLog.objects.get_or_create(habit=habit, date=target_date)
        serializer = HabitSerializer(habit, context={'request': request})
        return Response({
            'message': 'Habit marked as completed for date.' if created else 'Already completed.',
            'created': created,
            'habit': serializer.data
        }, status=status.HTTP_200_OK if not created else status.HTTP_201_CREATED)

    def delete(self, request, pk):
        user = get_app_user(request)
        habit = get_object_or_404(Habit, pk=pk, user=user)
        target_date = parse_target_date(request)

        deleted_count, _ = HabitLog.objects.filter(habit=habit, date=target_date).delete()
        serializer = HabitSerializer(habit, context={'request': request})
        return Response({
            'message': 'Habit check-in undone.' if deleted_count > 0 else 'No check-in found for date.',
            'deleted': deleted_count > 0,
            'habit': serializer.data
        }, status=status.HTTP_200_OK)


class HabitStatsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        user = get_app_user(request)
        ref_date = parse_target_date(request)
        habits = list(Habit.objects.filter(user=user, is_active=True))
        total_habits = len(habits)

        # Get all logs for user's habits
        all_logs = HabitLog.objects.filter(habit__user=user, habit__is_active=True)
        total_completions = all_logs.count()

        # Calculate today's completions
        today_completed_count = all_logs.filter(date=ref_date).count()
        today_percentage = round((today_completed_count / total_habits * 100)) if total_habits > 0 else 0

        # Calculate max streak across all habits
        streaks = [h.calculate_streaks(ref_date)['current_streak'] for h in habits]
        longest_streaks = [h.calculate_streaks(ref_date)['longest_streak'] for h in habits]
        best_current_streak = max(streaks) if streaks else 0
        best_all_time_streak = max(longest_streaks) if longest_streaks else 0

        # Calendar completions map: date -> count of completed habits
        # Covering a window of past 60 days to next 30 days
        start_cal = ref_date - timedelta(days=60)
        end_cal = ref_date + timedelta(days=35)
        cal_logs = all_logs.filter(date__gte=start_cal, date__lte=end_cal).values('date').annotate(count=Count('id'))
        calendar_data = {item['date'].strftime('%Y-%m-%d'): item['count'] for item in cal_logs}

        # Weekly stats (last 7 days completion rate)
        weekly_stats = []
        for i in range(6, -1, -1):
            d = ref_date - timedelta(days=i)
            cnt = all_logs.filter(date=d).count()
            rate = round((cnt / total_habits * 100)) if total_habits > 0 else 0
            weekly_stats.append({
                'day': d.strftime('%a'),
                'date': d.strftime('%Y-%m-%d'),
                'count': cnt,
                'rate': rate
            })

        # Monthly overall success rate
        last_30_days = [ref_date - timedelta(days=i) for i in range(30)]
        expected_total = total_habits * 30
        actual_total = all_logs.filter(date__gte=ref_date - timedelta(days=29), date__lte=ref_date).count()
        monthly_success_rate = round((actual_total / expected_total * 100)) if expected_total > 0 else 0

        return Response({
            'total_habits': total_habits,
            'completed_today': today_completed_count,
            'today_percentage': today_percentage,
            'current_streak': best_current_streak,
            'longest_streak': best_all_time_streak,
            'total_completions': total_completions,
            'monthly_success_rate': monthly_success_rate or today_percentage,
            'calendar_data': calendar_data,
            'weekly_stats': weekly_stats,
            'reference_date': ref_date.strftime('%Y-%m-%d')
        })
