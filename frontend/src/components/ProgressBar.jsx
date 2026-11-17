import React from 'react';

export const ProgressBar = ({ completedCount = 0, totalCount = 0 }) => {
  const percentage = totalCount > 0 ? Math.round((completedCount / totalCount) * 100) : 0;

  return (
    <div className="progress-card">
      <div className="progress-header">
        <div>
          <span className="progress-title">Your Progress</span>
          <span className="progress-count-text">
            ({completedCount} of {totalCount} completed today)
          </span>
        </div>
        <span className="progress-percentage">{percentage}%</span>
      </div>

      <div className="progress-track" role="progressbar" aria-valuenow={percentage} aria-valuemin={0} aria-valuemax={100}>
        <div 
          className="progress-fill" 
          style={{ width: `${percentage}%` }}
        ></div>
      </div>
    </div>
  );
};
