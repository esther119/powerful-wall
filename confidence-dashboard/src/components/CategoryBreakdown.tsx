import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { ConfidenceData, Category } from '../types';
import { calculateCategoryStats, formatCategoryName } from '../utils/dataProcessing';

interface Props {
  data: ConfidenceData;
  onCategorySelect?: (category: Category) => void;
  selectedCategory?: Category | null;
}

const COLORS = [
  '#8884d8', '#82ca9d', '#ffc658', '#ff7c7c', '#8dd1e1',
  '#d084d0', '#ffb347', '#67b7dc', '#a4de6c'
];

export const CategoryBreakdown: React.FC<Props> = ({ data, onCategorySelect, selectedCategory }) => {
  const stats = calculateCategoryStats(data);
  const chartData = stats.map(stat => ({
    name: formatCategoryName(stat.category),
    category: stat.category,
    value: stat.avgPowerLevel,
    count: stat.entryCount,
  }));

  const handleClick = (data: any) => {
    if (onCategorySelect && data && data.category) {
      onCategorySelect(data.category);
    }
  };

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
        <XAxis 
          dataKey="name" 
          angle={-45} 
          textAnchor="end" 
          height={100}
          stroke="#666"
        />
        <YAxis domain={[0, 10]} stroke="#666" />
        <Tooltip 
          content={({ active, payload }) => {
            if (active && payload && payload[0]) {
              return (
                <div style={{ 
                  backgroundColor: '#f5f5f5', 
                  padding: '10px', 
                  border: '1px solid #ddd',
                  borderRadius: '4px'
                }}>
                  <p style={{ margin: 0, fontWeight: 'bold' }}>{payload[0].payload.name}</p>
                  <p style={{ margin: '5px 0', color: '#666' }}>
                    Avg Power: {payload[0].value?.toFixed(1)}
                  </p>
                  <p style={{ margin: 0, color: '#666' }}>
                    Entries: {payload[0].payload.count}
                  </p>
                </div>
              );
            }
            return null;
          }}
        />
        <Bar 
          dataKey="value" 
          onClick={handleClick}
          style={{ cursor: onCategorySelect ? 'pointer' : 'default' }}
        >
          {chartData.map((entry, index) => (
            <Cell 
              key={`cell-${index}`} 
              fill={entry.category === selectedCategory ? '#ff6b6b' : COLORS[index % COLORS.length]}
            />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
};