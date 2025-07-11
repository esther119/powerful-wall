import React from 'react';
import { ConfidenceData } from '../types';
import { getOverallStats } from '../utils/dataProcessing';
import { TrendingUp, TrendingDown, Activity, Calendar, BarChart3, Users } from 'lucide-react';

interface Props {
  data: ConfidenceData;
}

export const OverviewStats: React.FC<Props> = ({ data }) => {
  const stats = getOverallStats(data);
  
  const confidenceChange = stats.avgConfidence >= 7 ? 'positive' : 'neutral';

  return (
    <div className="overview-stats">
      <div className="stat-card">
        <div className="stat-icon">
          <Calendar size={24} />
        </div>
        <div className="stat-content">
          <span className="stat-value">{stats.totalDays}</span>
          <span className="stat-label">Days Tracked</span>
        </div>
      </div>

      <div className="stat-card">
        <div className="stat-icon">
          <Activity size={24} />
        </div>
        <div className="stat-content">
          <span className="stat-value">{stats.totalEntries}</span>
          <span className="stat-label">Total Entries</span>
        </div>
      </div>

      <div className="stat-card highlight">
        <div className="stat-icon">
          {confidenceChange === 'positive' ? <TrendingUp size={24} /> : <TrendingDown size={24} />}
        </div>
        <div className="stat-content">
          <span className="stat-value">{stats.avgConfidence.toFixed(1)}</span>
          <span className="stat-label">Average Confidence</span>
        </div>
      </div>

      <div className="stat-card">
        <div className="stat-icon">
          <BarChart3 size={24} />
        </div>
        <div className="stat-content">
          <span className="stat-value">{stats.highestConfidence}</span>
          <span className="stat-label">Peak Confidence</span>
        </div>
      </div>

      <div className="stat-card">
        <div className="stat-icon personal">
          <Users size={24} />
        </div>
        <div className="stat-content">
          <span className="stat-value">{stats.personalPercentage.toFixed(0)}%</span>
          <span className="stat-label">Personal</span>
        </div>
      </div>

      <div className="stat-card">
        <div className="stat-icon professional">
          <Users size={24} />
        </div>
        <div className="stat-content">
          <span className="stat-value">{stats.professionalPercentage.toFixed(0)}%</span>
          <span className="stat-label">Professional</span>
        </div>
      </div>
    </div>
  );
};