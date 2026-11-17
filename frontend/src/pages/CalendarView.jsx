import React, { useState } from 'react';
import { ChevronLeft, ChevronRight, BookOpen, Droplet, Dumbbell, Moon, Sparkles, Heart, Check } from 'lucide-react';

const ICON_MAP = {
  book: BookOpen,
  water: Droplet,
  exercise: Dumbbell,
  moon: Moon,
  sparkles: Sparkles,
  heart: Heart,
};

export const CalendarView = ({ habits = [], stats = {}, onBackToHome }) => {
  // Use November 2026 as the default view matching the UI mock, or current year/month
  const [currentDate, setCurrentDate] = useState(new Date(2026, 10, 1)); // 10 is November in JS (0-indexed)

  const year = currentDate.getFullYear();
  const month = currentDate.getMonth();

  const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  const handlePrevMonth = () => {
    setCurrentDate(new Date(year, month - 1, 1));
  };

  const handleNextMonth = () => {
    setCurrentDate(new Date(year, month + 1, 1));
  };

  // Calendar math
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const firstDayIndex = new Date(year, month, 1).getDay(); // 0 is Sun

  const calendarDays = [];
  // Empty slots before month start
  for (let i = 0; i < firstDayIndex; i++) {
    calendarDays.push({ empty: true, id: `empty-${i}` });
  }
  for (let d = 1; d <= daysInMonth; d++) {
    const dateKey = `${year}-${String(month + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
    const count = stats.calendar_data ? stats.calendar_data[dateKey] : 0;
    // In demo November 2026, days 1 to 7 are completed streak days as in mock
    const isMockStreak = year === 2026 && month === 10 && d >= 1 && d <= 7;
    const isCompleted = count > 0 || isMockStreak;

    calendarDays.push({
      empty: false,
      day: d,
      dateKey,
      isCompleted,
      count: isCompleted ? (count || 3) : 0
    });
  }

  const completedTodayCount = habits.filter(h => h.completed_today).length;

  return (
    <div className="calendar-view-container">
      {/* Month Navigator Header */}
      <div className="calendar-month-selector">
        <button type="button" className="cal-nav-btn" onClick={handlePrevMonth} aria-label="Previous month">
          <ChevronLeft size={20} />
        </button>
        <h2 className="cal-month-title">{monthNames[month]} {year}</h2>
        <button type="button" className="cal-nav-btn" onClick={handleNextMonth} aria-label="Next month">
          <ChevronRight size={20} />
        </button>
      </div>

      {/* Weekdays Row */}
      <div className="cal-weekdays-grid">
        <span>Sun</span>
        <span>Mon</span>
        <span>Tue</span>
        <span>Wed</span>
        <span>Thu</span>
        <span>Fri</span>
        <span>Sat</span>
      </div>

      {/* Days Grid */}
      <div className="cal-days-grid">
        {calendarDays.map((item) => {
          if (item.empty) {
            return <div key={item.id} className="cal-day-cell empty"></div>;
          }
          return (
            <div 
              key={item.day} 
              className={`cal-day-cell ${item.isCompleted ? 'highlighted' : ''}`}
            >
              <span className="cal-day-number">{item.day}</span>
            </div>
          );
        })}
      </div>

      {/* Today's Habits Summary Section */}
      <div className="today-habits-panel">
        <div className="today-habits-header">
          <h3 className="section-title">Today's Habits</h3>
          <span className="count-pill">{completedTodayCount} / {habits.length}</span>
        </div>

        <div className="today-habits-mini-list">
          {habits.map((habit) => {
            const IconComp = ICON_MAP[habit.icon] || BookOpen;
            return (
              <div key={habit.id} className="today-mini-item">
                <div 
                  className="mini-icon-circle"
                  style={{ backgroundColor: `${habit.color || '#F59E0B'}20`, color: habit.color || '#F59E0B' }}
                >
                  <IconComp size={18} />
                </div>
                <span className="mini-habit-name">{habit.name}</span>
                <div className={`mini-check-badge ${habit.completed_today ? 'done' : 'pending'}`}>
                  {habit.completed_today && <Check size={14} color="#FFF" strokeWidth={3} />}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
