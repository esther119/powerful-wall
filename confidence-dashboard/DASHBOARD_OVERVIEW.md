# Confidence Journey Dashboard

## Overview
This React dashboard visualizes and analyzes your confidence journey data, tracking both personal and professional growth over time.

## Key Features

### 1. Overview Statistics
- **Total Days Tracked**: Shows the span of your confidence journey
- **Total Entries**: Number of confidence moments recorded
- **Average Confidence**: Overall confidence score (1-10 scale)
- **Peak Confidence**: Your highest recorded confidence level
- **Personal vs Professional Split**: Percentage breakdown of confidence types

### 2. Time Series Visualization
- Interactive line chart showing confidence trends over time
- Separate lines for:
  - Overall average (purple)
  - Personal confidence (green)
  - Professional confidence (yellow)
- Helps identify patterns and trends in your confidence journey

### 3. Daily Confidence Calendar
- Heatmap view of daily confidence levels
- Color-coded from red (low) to green (high)
- Click any day to see detailed entries
- Organized by month for easy navigation

### 4. Category Performance Analysis
- Bar chart showing average confidence by category
- Categories include:
  - Career Development
  - Personal Growth
  - Technical Skills
  - Social Interactions
  - Self Image
  - Physical Wellness
  - Creative Work
  - Professional Presentation
- Click on bars to filter the entire dashboard by category

### 5. Power Level Distribution
- Histogram showing frequency of different confidence levels
- Color-coded bars:
  - Red (1-3): Low confidence
  - Yellow (4-6): Medium confidence
  - Green (7-8): Good confidence
  - Teal (9-10): Excellent confidence

### 6. Interactive Filtering
- Filter by category (e.g., only show "Technical Skills" entries)
- Filter by type (Personal vs Professional)
- Filters apply to all visualizations for focused analysis

### 7. Daily Details Modal
- Click any day in the calendar to see all entries
- Shows each confidence moment with:
  - Category tag
  - Power level with visual indicator
  - Full text description
- Summary statistics for the selected day

## Data Insights Available

1. **Confidence Trends**: Track if your confidence is improving over time
2. **Strength Areas**: Identify categories where you consistently feel confident
3. **Growth Opportunities**: Spot categories with lower confidence for focused improvement
4. **Balance Analysis**: See if you're maintaining a healthy personal/professional balance
5. **Peak Moments**: Celebrate your highest confidence achievements
6. **Pattern Recognition**: Identify what types of activities boost your confidence

## Technical Stack

- **React** with TypeScript for type safety
- **Recharts** for interactive data visualizations
- **date-fns** for date formatting
- **Lucide React** for modern icons
- **Responsive Design** works on desktop and mobile

## Usage

1. Start the dashboard: `npm start`
2. Explore the visualizations to understand your confidence patterns
3. Use filters to dive deep into specific areas
4. Click on calendar days to read individual entries
5. Use insights to guide personal development

The dashboard transforms raw confidence data into actionable insights, helping you understand and improve your personal and professional growth journey.