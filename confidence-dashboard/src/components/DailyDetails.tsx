import React from 'react';
import { DailyData } from '../types';
import { format, parseISO } from 'date-fns';
import { X, TrendingUp, TrendingDown, Activity } from 'lucide-react';
import { formatCategoryName } from '../utils/dataProcessing';

interface Props {
  date: string;
  data: DailyData;
  onClose: () => void;
}

export const DailyDetails: React.FC<Props> = ({ date, data, onClose }) => {
  const getPowerLevelIcon = (level: number) => {
    if (level >= 8) return <TrendingUp size={16} color="#22c55e" />;
    if (level >= 6) return <Activity size={16} color="#facc15" />;
    return <TrendingDown size={16} color="#ef4444" />;
  };

  const getPowerLevelClass = (level: number) => {
    if (level >= 8) return 'high';
    if (level >= 6) return 'medium';
    return 'low';
  };

  return (
    <div className="daily-details-overlay" onClick={onClose}>
      <div className="daily-details" onClick={(e) => e.stopPropagation()}>
        <div className="details-header">
          <h3>{format(parseISO(date), 'MMMM d, yyyy')}</h3>
          <button className="close-button" onClick={onClose}>
            <X size={20} />
          </button>
        </div>
        
        <div className="details-summary">
          <div className="summary-item">
            <span className="summary-label">Daily Average:</span>
            <span className={`summary-value ${getPowerLevelClass(data.daily_confidence_average)}`}>
              {data.daily_confidence_average.toFixed(1)}
            </span>
          </div>
          <div className="summary-item">
            <span className="summary-label">Dominant Area:</span>
            <span className={`summary-value ${data.dominant_confidence_area}`}>
              {data.dominant_confidence_area}
            </span>
          </div>
          <div className="summary-item">
            <span className="summary-label">Total Entries:</span>
            <span className="summary-value">{data.entries.length}</span>
          </div>
        </div>

        <div className="entries-list">
          <h4>Confidence Moments</h4>
          {data.entries.map((entry, index) => (
            <div key={index} className="entry-card">
              <div className="entry-header">
                <span className={`entry-category ${entry.confidence_type}`}>
                  {formatCategoryName(entry.category)}
                </span>
                <span className={`power-level ${getPowerLevelClass(entry.power_level)}`}>
                  {getPowerLevelIcon(entry.power_level)}
                  {entry.power_level}
                </span>
              </div>
              <p className="entry-text">{entry.text}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};