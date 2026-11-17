import React from 'react';
import { Trophy, Flame, Sparkles } from 'lucide-react';

export const StreakBanner = ({ streak = 7, totalCompleted = 0 }) => {
  return (
    <div className="streak-banner">
      <div className="streak-banner-content">
        <div className="trophy-illustration-box">
          <div className="trophy-bg-glow"></div>
          <div className="trophy-badge">
            <Trophy size={48} className="trophy-icon" strokeWidth={2.2} />
            <Sparkles size={16} className="trophy-sparkle" />
          </div>
        </div>

        <div className="streak-text-box">
          <span className="streak-subheading">You're on a roll!</span>
          <h2 className="streak-main-heading">
            {streak} Day Streak
          </h2>
          <div className="streak-footer">
            <span>Keep going!</span>
            <Flame size={16} className="streak-flame" />
          </div>
        </div>
      </div>
      
      {/* Decorative decorative ambient circle */}
      <div className="banner-decor-circle circle-1"></div>
      <div className="banner-decor-circle circle-2"></div>
    </div>
  );
};
