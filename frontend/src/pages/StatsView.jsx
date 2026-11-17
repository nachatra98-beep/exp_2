import React, { useState } from 'react';
import { Flame, CheckCircle, TrendingUp, Award, Sparkles } from 'lucide-react';

export const StatsView = ({ habits = [], stats = {}, onBackToHome }) => {
  const [activeSegment, setActiveSegment] = useState('Overview');

  const completedCount = habits.filter(h => h.completed_today).length;
  const totalCount = habits.length;
  const currentRate = totalCount > 0 ? Math.round((completedCount / totalCount) * 100) : 75;

  const streakDays = stats.current_streak || 7;
  const totalCompletions = stats.total_completions || 21;

  // Circular progress calculations for SVG
  const radius = 62;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (currentRate / 100) * circumference;

  return (
    <div className="stats-view-container">
      {/* Segmented Control */}
      <div className="stats-segmented-bar">
        {['Overview', 'Weekly', 'Monthly'].map((seg) => (
          <button
            key={seg}
            type="button"
            className={`seg-tab-btn ${activeSegment === seg ? 'active' : ''}`}
            onClick={() => setActiveSegment(seg)}
          >
            {seg}
          </button>
        ))}
      </div>

      {/* Donut Chart / Success Rate Card */}
      <div className="stats-donut-card">
        <div className="donut-chart-wrapper">
          <svg className="donut-svg" width="160" height="160" viewBox="0 0 160 160">
            {/* Background ring */}
            <circle
              className="donut-bg-ring"
              cx="80"
              cy="80"
              r={radius}
              strokeWidth="14"
            />
            {/* Progress ring */}
            <circle
              className="donut-fill-ring"
              cx="80"
              cy="80"
              r={radius}
              strokeWidth="14"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
              transform="rotate(-90 80 80)"
            />
          </svg>
          <div className="donut-center-content">
            <span className="donut-percentage">{currentRate}%</span>
          </div>
        </div>

        <div className="donut-info">
          <h3 className="donut-title">Overall Success Rate</h3>
          <p className="donut-subtitle">You completed {currentRate}% of your habits!</p>
          <div className="stats-chart-icon-box">
            <TrendingUp size={24} className="text-amber-500" />
          </div>
        </div>
      </div>

      {/* 2 Metrics Cards Grid */}
      <div className="metrics-grid">
        {/* Streak Metric */}
        <div className="metric-box">
          <div className="metric-label-row">
            <Flame size={16} className="text-amber-500 fill-amber-500" />
            <span className="metric-label">Streak</span>
          </div>
          <p className="metric-value">{streakDays} Days</p>
        </div>

        {/* Total Completions Metric */}
        <div className="metric-box">
          <div className="metric-label-row">
            <CheckCircle size={16} className="text-emerald-500" />
            <span className="metric-label">Total Completions</span>
          </div>
          <p className="metric-value">{totalCompletions} Times</p>
        </div>
      </div>

      {/* Cute Motivational Mascot Card */}
      <div className="mascot-cheer-card">
        <div className="star-mascot-wrapper">
          <div className="star-emoji-bubble">⭐</div>
          <Sparkles size={16} className="star-sparkle-1" />
          <Sparkles size={12} className="star-sparkle-2" />
        </div>
        <div className="mascot-text-box">
          <h4 className="mascot-title">You're doing great!</h4>
          <p className="mascot-desc">Keep up the good work!</p>
        </div>
      </div>
    </div>
  );
};
