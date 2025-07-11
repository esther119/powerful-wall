import React from 'react';
import { ConfidenceData } from '../types';
import { format, parseISO } from 'date-fns';

interface Props {
  data: ConfidenceData;
  onDateSelect?: (date: string) => void;
  selectedDate?: string | null;
}

export const CalendarHeatmap: React.FC<Props> = ({ data, onDateSelect, selectedDate }) => {
  const getHeatmapColor = (value: number) => {
    if (value >= 8) return '#22c55e';
    if (value >= 7) return '#84cc16';
    if (value >= 6) return '#facc15';
    if (value >= 5) return '#fb923c';
    return '#ef4444';
  };

  const dates = Object.keys(data).sort();
  const months = new Map<string, string[]>();
  
  dates.forEach(date => {
    const month = format(parseISO(date), 'MMM yyyy');
    if (!months.has(month)) {
      months.set(month, []);
    }
    months.get(month)!.push(date);
  });

  return (
    <div className="calendar-heatmap">
      {Array.from(months.entries()).map(([month, monthDates]) => (
        <div key={month} className="month-section">
          <h3>{month}</h3>
          <div className="days-grid">
            {monthDates.map(date => {
              const dayData = data[date];
              const isSelected = date === selectedDate;
              const dayNum = format(parseISO(date), 'd');
              
              return (
                <div
                  key={date}
                  className={`day-cell ${isSelected ? 'selected' : ''}`}
                  style={{
                    backgroundColor: getHeatmapColor(dayData.daily_confidence_average),
                    opacity: isSelected ? 1 : 0.8,
                  }}
                  onClick={() => onDateSelect && onDateSelect(date)}
                  title={`${format(parseISO(date), 'MMM d, yyyy')} - Confidence: ${dayData.daily_confidence_average.toFixed(1)}`}
                >
                  <span className="day-number">{dayNum}</span>
                  <span className="day-value">{dayData.daily_confidence_average.toFixed(1)}</span>
                </div>
              );
            })}
          </div>
        </div>
      ))}
      
      <div className="legend">
        <span>Low</span>
        <div className="legend-scale">
          {[4, 5, 6, 7, 8].map(level => (
            <div
              key={level}
              className="legend-item"
              style={{ backgroundColor: getHeatmapColor(level) }}
              title={`Level ${level}`}
            />
          ))}
        </div>
        <span>High</span>
      </div>
    </div>
  );
};