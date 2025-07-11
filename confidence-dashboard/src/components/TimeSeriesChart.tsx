import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { ConfidenceData } from '../types';
import { processConfidenceTypeData } from '../utils/dataProcessing';

interface Props {
  data: ConfidenceData;
}

export const TimeSeriesChart: React.FC<Props> = ({ data }) => {
  const chartData = processConfidenceTypeData(data);

  return (
    <ResponsiveContainer width="100%" height={400}>
      <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
        <XAxis dataKey="date" stroke="#666" />
        <YAxis domain={[0, 10]} stroke="#666" />
        <Tooltip 
          contentStyle={{ backgroundColor: '#f5f5f5', border: '1px solid #ddd' }}
          labelStyle={{ color: '#333' }}
        />
        <Legend />
        <Line 
          type="monotone" 
          dataKey="value" 
          stroke="#8884d8" 
          strokeWidth={2}
          name="Overall Average"
          dot={{ fill: '#8884d8', r: 4 }}
        />
        <Line 
          type="monotone" 
          dataKey="personal" 
          stroke="#82ca9d" 
          strokeWidth={2}
          name="Personal"
          dot={{ fill: '#82ca9d', r: 4 }}
        />
        <Line 
          type="monotone" 
          dataKey="professional" 
          stroke="#ffc658" 
          strokeWidth={2}
          name="Professional"
          dot={{ fill: '#ffc658', r: 4 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
};