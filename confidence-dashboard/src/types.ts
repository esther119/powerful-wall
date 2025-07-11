export interface ConfidenceEntry {
  text: string;
  category: Category;
  confidence_type: ConfidenceType;
  power_level: number;
}

export interface DailyData {
  entries: ConfidenceEntry[];
  daily_confidence_average: number;
  dominant_confidence_area: ConfidenceType;
}

export interface ConfidenceData {
  [date: string]: DailyData;
}

export type ConfidenceType = 'personal' | 'professional';

export type Category = 
  | 'career_development'
  | 'personal_growth'
  | 'professional_presentation'
  | 'technical_skills'
  | 'social_interactions'
  | 'self_image'
  | 'physical_wellness'
  | 'creative_work';

export interface ChartDataPoint {
  date: string;
  value: number;
  personal?: number;
  professional?: number;
}

export interface CategoryStats {
  category: Category;
  avgPowerLevel: number;
  entryCount: number;
  percentage: number;
}