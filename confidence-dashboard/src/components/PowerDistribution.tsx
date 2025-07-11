import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { ConfidenceData } from '../types';
import { getPowerLevelDistribution } from '../utils/dataProcessing';

interface Props {
  data: ConfidenceData;
}

export const PowerDistribution: React.FC<Props> = ({ data }) => {
  const distribution = getPowerLevelDistribution(data);
  
  const getBarColor = (level: number) => {
    if (level <= 3) return '#ff6b6b';
    if (level <= 6) return '#ffc658';
    if (level <= 8) return '#82ca9d';
    return '#4ecdc4';
  };

  return (
    <ResponsiveContainer width="100%" height={250}>
      <BarChart data={distribution} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
        <XAxis 
          dataKey="level" 
          label={{ value: 'Power Level', position: 'insideBottom', offset: -5 }}
          stroke="#666"
        />
        <YAxis 
          label={{ value: 'Frequency', angle: -90, position: 'insideLeft' }}
          stroke="#666"
        />
        <Tooltip 
          contentStyle={{ backgroundColor: '#f5f5f5', border: '1px solid #ddd' }}
          labelFormatter={(value) => `Power Level ${value}`}
        />
        <Bar dataKey="count" name="Entries">
          {distribution.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={getBarColor(entry.level)} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
};