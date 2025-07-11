#!/usr/bin/env python3
"""
Advanced Confidence Data Analysis
Provides deeper insights into confidence patterns and trends
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict, Counter


class ConfidenceAnalyzer:
    """Analyze confidence tracking data for patterns and insights."""
    
    def __init__(self, data_path: str = "transcribed_data/final_20250711.json"):
        """Initialize analyzer with data file path."""
        self.data_path = Path(data_path)
        self.data = self.load_data()
        self.df = self.create_dataframe()
        
    def load_data(self) -> Dict:
        """Load JSON data from file."""
        with open(self.data_path, 'r') as f:
            return json.load(f)
    
    def create_dataframe(self) -> pd.DataFrame:
        """Convert nested JSON to flat DataFrame for analysis."""
        rows = []
        
        for date_str, day_data in self.data.items():
            date = pd.to_datetime(date_str)
            
            for entry in day_data.get('entries', []):
                row = {
                    'date': date,
                    'text': entry['text'],
                    'category': entry['category'],
                    'confidence_type': entry['confidence_type'],
                    'power_level': entry['power_level'],
                    'daily_avg': day_data['daily_confidence_average'],
                    'dominant_area': day_data['dominant_confidence_area']
                }
                rows.append(row)
        
        df = pd.DataFrame(rows)
        df['day_of_week'] = df['date'].dt.day_name()
        df['week_number'] = df['date'].dt.isocalendar().week
        df['month'] = df['date'].dt.month_name()
        
        return df
    
    def get_summary_statistics(self) -> Dict:
        """Calculate comprehensive summary statistics."""
        stats = {
            'overall': {
                'total_entries': len(self.df),
                'date_range': f"{self.df['date'].min().strftime('%Y-%m-%d')} to {self.df['date'].max().strftime('%Y-%m-%d')}",
                'avg_power_level': round(self.df['power_level'].mean(), 2),
                'std_power_level': round(self.df['power_level'].std(), 2),
                'median_power_level': self.df['power_level'].median(),
                'mode_power_level': self.df['power_level'].mode().values[0] if len(self.df['power_level'].mode()) > 0 else None
            },
            'by_type': {
                'personal': {
                    'count': len(self.df[self.df['confidence_type'] == 'personal']),
                    'avg_power': round(self.df[self.df['confidence_type'] == 'personal']['power_level'].mean(), 2)
                },
                'professional': {
                    'count': len(self.df[self.df['confidence_type'] == 'professional']),
                    'avg_power': round(self.df[self.df['confidence_type'] == 'professional']['power_level'].mean(), 2)
                }
            }
        }
        
        # Category statistics
        category_stats = {}
        for category in self.df['category'].unique():
            cat_df = self.df[self.df['category'] == category]
            category_stats[category] = {
                'count': len(cat_df),
                'avg_power': round(cat_df['power_level'].mean(), 2),
                'percentage': round(len(cat_df) / len(self.df) * 100, 1)
            }
        stats['by_category'] = category_stats
        
        return stats
    
    def analyze_temporal_patterns(self) -> Dict:
        """Analyze patterns over time."""
        patterns = {}
        
        # Day of week analysis
        dow_stats = self.df.groupby('day_of_week')['power_level'].agg(['mean', 'count'])
        patterns['by_day_of_week'] = {
            day: {'avg_power': round(stats['mean'], 2), 'count': int(stats['count'])}
            for day, stats in dow_stats.iterrows()
        }
        
        # Weekly trends
        weekly_avg = self.df.groupby('week_number')['power_level'].mean()
        patterns['weekly_trend'] = {
            'improving_weeks': sum(1 for i in range(1, len(weekly_avg)) if weekly_avg.iloc[i] > weekly_avg.iloc[i-1]),
            'declining_weeks': sum(1 for i in range(1, len(weekly_avg)) if weekly_avg.iloc[i] < weekly_avg.iloc[i-1])
        }
        
        # Best and worst streaks
        patterns['streaks'] = self.find_confidence_streaks()
        
        return patterns
    
    def find_confidence_streaks(self) -> Dict:
        """Find consecutive high/low confidence periods."""
        daily_avg = self.df.groupby('date')['power_level'].mean().sort_index()
        
        high_threshold = 7.5
        low_threshold = 5.5
        
        # Find high confidence streaks
        high_streaks = []
        current_streak = []
        
        for date, avg in daily_avg.items():
            if avg >= high_threshold:
                current_streak.append((date, avg))
            else:
                if len(current_streak) >= 2:
                    high_streaks.append(current_streak)
                current_streak = []
        
        if len(current_streak) >= 2:
            high_streaks.append(current_streak)
        
        # Find low confidence periods
        low_periods = [(date, avg) for date, avg in daily_avg.items() if avg <= low_threshold]
        
        return {
            'longest_high_streak': max(high_streaks, key=len) if high_streaks else [],
            'total_high_streak_days': sum(len(streak) for streak in high_streaks),
            'low_confidence_days': len(low_periods)
        }
    
    def get_category_correlations(self) -> pd.DataFrame:
        """Analyze which categories tend to occur together."""
        # Create a matrix of category co-occurrences by date
        date_categories = self.df.groupby(['date', 'category']).size().unstack(fill_value=0)
        
        # Calculate correlation matrix
        correlation_matrix = date_categories.corr()
        
        return correlation_matrix
    
    def get_improvement_areas(self) -> List[Dict]:
        """Identify areas that need attention based on low scores and frequency."""
        category_analysis = []
        
        for category in self.df['category'].unique():
            cat_df = self.df[self.df['category'] == category]
            
            analysis = {
                'category': category,
                'avg_power': cat_df['power_level'].mean(),
                'frequency': len(cat_df),
                'low_score_ratio': len(cat_df[cat_df['power_level'] <= 5]) / len(cat_df),
                'recent_trend': self.calculate_recent_trend(cat_df)
            }
            
            # Calculate improvement priority score
            analysis['priority_score'] = (
                (10 - analysis['avg_power']) * 0.4 +  # Lower avg = higher priority
                analysis['low_score_ratio'] * 10 * 0.3 +  # More low scores = higher priority
                (1 / (analysis['frequency'] + 1)) * 10 * 0.3  # Less frequent = higher priority
            )
            
            category_analysis.append(analysis)
        
        # Sort by priority score (higher = needs more attention)
        return sorted(category_analysis, key=lambda x: x['priority_score'], reverse=True)
    
    def calculate_recent_trend(self, df: pd.DataFrame) -> str:
        """Calculate if a category is trending up or down recently."""
        if len(df) < 2:
            return 'insufficient_data'
        
        # Get last 30% of entries
        recent_cutoff = df['date'].quantile(0.7)
        recent_avg = df[df['date'] >= recent_cutoff]['power_level'].mean()
        overall_avg = df['power_level'].mean()
        
        if recent_avg > overall_avg * 1.1:
            return 'improving'
        elif recent_avg < overall_avg * 0.9:
            return 'declining'
        else:
            return 'stable'
    
    def get_text_insights(self) -> Dict:
        """Analyze text content for patterns."""
        # Common words in high confidence moments
        high_conf_texts = self.df[self.df['power_level'] >= 8]['text'].str.lower()
        all_words = ' '.join(high_conf_texts).split()
        
        # Filter out common words
        stop_words = {'the', 'and', 'to', 'of', 'in', 'a', 'my', 'i', 'with', 'for', 'on', 'at', 'about'}
        meaningful_words = [w for w in all_words if w not in stop_words and len(w) > 3]
        
        word_freq = Counter(meaningful_words)
        
        return {
            'high_confidence_keywords': dict(word_freq.most_common(10)),
            'average_entry_length': round(self.df['text'].str.len().mean(), 1),
            'longest_entry': self.df.loc[self.df['text'].str.len().idxmax(), 'text'],
            'shortest_entry': self.df.loc[self.df['text'].str.len().idxmin(), 'text']
        }
    
    def generate_recommendations(self) -> List[str]:
        """Generate personalized recommendations based on analysis."""
        recommendations = []
        
        # Check overall trend
        weekly_avg = self.df.groupby('week_number')['power_level'].mean()
        if len(weekly_avg) > 1 and weekly_avg.iloc[-1] < weekly_avg.iloc[0]:
            recommendations.append("Your confidence has been trending downward. Consider revisiting activities from your peak confidence days.")
        
        # Category-specific recommendations
        improvement_areas = self.get_improvement_areas()
        if improvement_areas:
            top_area = improvement_areas[0]
            recommendations.append(f"Focus on improving '{top_area['category']}' - it has the highest priority for growth.")
        
        # Type balance
        type_counts = self.df['confidence_type'].value_counts()
        if type_counts.get('personal', 0) < type_counts.get('professional', 0) * 0.5:
            recommendations.append("You're focusing heavily on professional confidence. Consider balancing with more personal development activities.")
        elif type_counts.get('professional', 0) < type_counts.get('personal', 0) * 0.5:
            recommendations.append("Your personal confidence is strong! Consider applying this energy to professional challenges.")
        
        # Day of week patterns
        dow_stats = self.df.groupby('day_of_week')['power_level'].mean()
        best_day = dow_stats.idxmax()
        worst_day = dow_stats.idxmin()
        recommendations.append(f"You tend to feel most confident on {best_day}s. Schedule important activities then.")
        recommendations.append(f"Be mindful of {worst_day}s when confidence tends to dip. Plan supportive activities.")
        
        return recommendations
    
    def save_analysis_report(self, output_path: str = "confidence_analysis_report.json"):
        """Save comprehensive analysis report."""
        report = {
            'generated_at': datetime.now().isoformat(),
            'summary_statistics': self.get_summary_statistics(),
            'temporal_patterns': self.analyze_temporal_patterns(),
            'improvement_areas': self.get_improvement_areas(),
            'text_insights': self.get_text_insights(),
            'recommendations': self.generate_recommendations(),
            'metadata': {
                'total_days_tracked': len(self.df['date'].unique()),
                'data_completeness': round(len(self.df['date'].unique()) / 
                                          ((self.df['date'].max() - self.df['date'].min()).days + 1) * 100, 1)
            }
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"Analysis report saved to {output_path}")
        return report
    
    def create_visualizations(self, output_dir: str = "confidence_visualizations"):
        """Create and save visualization plots."""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Set style
        plt.style.use('seaborn-v0_8-darkgrid')
        
        # 1. Power level distribution
        plt.figure(figsize=(10, 6))
        self.df['power_level'].hist(bins=range(1, 12), alpha=0.7, color='skyblue', edgecolor='black')
        plt.xlabel('Power Level')
        plt.ylabel('Frequency')
        plt.title('Distribution of Confidence Power Levels')
        plt.savefig(output_path / 'power_distribution.png')
        plt.close()
        
        # 2. Category comparison
        plt.figure(figsize=(12, 8))
        category_stats = self.df.groupby('category')['power_level'].agg(['mean', 'count'])
        category_stats['mean'].sort_values().plot(kind='barh', color='coral')
        plt.xlabel('Average Power Level')
        plt.title('Average Confidence by Category')
        plt.tight_layout()
        plt.savefig(output_path / 'category_comparison.png')
        plt.close()
        
        # 3. Time series with rolling average
        plt.figure(figsize=(14, 8))
        daily_avg = self.df.groupby('date')['power_level'].mean().sort_index()
        daily_avg.plot(marker='o', markersize=4, linewidth=1, alpha=0.7, label='Daily Average')
        daily_avg.rolling(window=7).mean().plot(linewidth=2, color='red', label='7-Day Moving Average')
        plt.xlabel('Date')
        plt.ylabel('Power Level')
        plt.title('Confidence Journey Over Time')
        plt.legend()
        plt.tight_layout()
        plt.savefig(output_path / 'time_series.png')
        plt.close()
        
        # 4. Heatmap of category correlations
        plt.figure(figsize=(10, 8))
        corr_matrix = self.get_category_correlations()
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, 
                   fmt='.2f', square=True, linewidths=1)
        plt.title('Category Co-occurrence Correlations')
        plt.tight_layout()
        plt.savefig(output_path / 'category_correlations.png')
        plt.close()
        
        print(f"Visualizations saved to {output_dir}/")


def main():
    """Run the confidence analysis."""
    print("🔍 Starting Confidence Data Analysis...")
    
    analyzer = ConfidenceAnalyzer()
    
    # Generate and save report
    report = analyzer.save_analysis_report()
    
    # Create visualizations
    analyzer.create_visualizations()
    
    # Print key insights
    print("\n📊 Key Insights:")
    print(f"- Total entries analyzed: {report['summary_statistics']['overall']['total_entries']}")
    print(f"- Average confidence level: {report['summary_statistics']['overall']['avg_power_level']}")
    print(f"- Data completeness: {report['metadata']['data_completeness']}%")
    
    print("\n💡 Top Recommendations:")
    for i, rec in enumerate(report['recommendations'][:3], 1):
        print(f"{i}. {rec}")
    
    print("\n✅ Analysis complete! Check the generated files for detailed insights.")


if __name__ == "__main__":
    main()