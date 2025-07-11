import { ConfidenceData, ChartDataPoint, CategoryStats, Category, ConfidenceType } from '../types';
import { format, parseISO } from 'date-fns';

export const processTimeSeriesData = (data: ConfidenceData): ChartDataPoint[] => {
  const sortedDates = Object.keys(data).sort();
  
  return sortedDates.map(date => ({
    date: format(parseISO(date), 'MMM d'),
    value: data[date].daily_confidence_average,
  }));
};

export const processConfidenceTypeData = (data: ConfidenceData): ChartDataPoint[] => {
  const sortedDates = Object.keys(data).sort();
  
  return sortedDates.map(date => {
    const entries = data[date].entries;
    const personalEntries = entries.filter(e => e.confidence_type === 'personal');
    const professionalEntries = entries.filter(e => e.confidence_type === 'professional');
    
    const personalAvg = personalEntries.length > 0
      ? personalEntries.reduce((sum, e) => sum + e.power_level, 0) / personalEntries.length
      : 0;
    
    const professionalAvg = professionalEntries.length > 0
      ? professionalEntries.reduce((sum, e) => sum + e.power_level, 0) / professionalEntries.length
      : 0;
    
    return {
      date: format(parseISO(date), 'MMM d'),
      value: data[date].daily_confidence_average,
      personal: personalAvg,
      professional: professionalAvg,
    };
  });
};

export const calculateCategoryStats = (data: ConfidenceData): CategoryStats[] => {
  const categoryMap = new Map<Category, { total: number; count: number }>();
  let totalEntries = 0;
  
  // Collect data for each category
  Object.values(data).forEach(day => {
    day.entries.forEach(entry => {
      totalEntries++;
      const current = categoryMap.get(entry.category) || { total: 0, count: 0 };
      categoryMap.set(entry.category, {
        total: current.total + entry.power_level,
        count: current.count + 1,
      });
    });
  });
  
  // Calculate statistics
  const stats: CategoryStats[] = [];
  categoryMap.forEach((value, category) => {
    stats.push({
      category,
      avgPowerLevel: value.total / value.count,
      entryCount: value.count,
      percentage: (value.count / totalEntries) * 100,
    });
  });
  
  return stats.sort((a, b) => b.avgPowerLevel - a.avgPowerLevel);
};

export const getOverallStats = (data: ConfidenceData) => {
  const allEntries = Object.values(data).flatMap(day => day.entries);
  const allPowerLevels = allEntries.map(e => e.power_level);
  const personalEntries = allEntries.filter(e => e.confidence_type === 'personal');
  const professionalEntries = allEntries.filter(e => e.confidence_type === 'professional');
  
  return {
    totalDays: Object.keys(data).length,
    totalEntries: allEntries.length,
    avgConfidence: allPowerLevels.reduce((a, b) => a + b, 0) / allPowerLevels.length,
    highestConfidence: Math.max(...allPowerLevels),
    lowestConfidence: Math.min(...allPowerLevels),
    personalPercentage: (personalEntries.length / allEntries.length) * 100,
    professionalPercentage: (professionalEntries.length / allEntries.length) * 100,
  };
};

export const getPowerLevelDistribution = (data: ConfidenceData) => {
  const distribution = Array(10).fill(0);
  
  Object.values(data).forEach(day => {
    day.entries.forEach(entry => {
      distribution[entry.power_level - 1]++;
    });
  });
  
  return distribution.map((count, index) => ({
    level: index + 1,
    count,
  }));
};

export const formatCategoryName = (category: Category): string => {
  return category
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};