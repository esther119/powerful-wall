# Confidence Journey Dashboard

A comprehensive visualization and analysis system for tracking and understanding your confidence patterns over time.

## 🎯 Features

### Interactive Web Dashboard
- **Real-time visualizations** of confidence trends
- **Filtering capabilities** by type, category, and power level
- **Calendar heatmap** showing daily confidence levels
- **Top moments & growth areas** identification
- **Search functionality** across all entries
- **Export capabilities** for detailed reports

### Advanced Python Analysis
- **Statistical insights** including means, medians, and distributions
- **Temporal pattern analysis** (weekly trends, day-of-week patterns)
- **Category correlations** to understand relationships
- **Personalized recommendations** based on your data
- **Publication-ready visualizations** exported as PNG files

## 🚀 Quick Start

### Web Dashboard

1. **Open the dashboard:**
   ```bash
   # Option 1: Using Python's built-in server
   python -m http.server 8000
   
   # Option 2: Using Node.js http-server (if installed)
   npx http-server
   
   # Option 3: Simply open in browser
   open index.html  # macOS
   xdg-open index.html  # Linux
   start index.html  # Windows
   ```

2. **Navigate to:** `http://localhost:8000` (if using a server)

3. **Explore your data:**
   - View overall statistics in the top cards
   - Filter by confidence type, category, or power level
   - Click through different time periods in the calendar
   - Search for specific entries
   - Export comprehensive reports

### Python Analysis

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the analysis:**
   ```bash
   python confidence_analysis.py
   ```

3. **Check outputs:**
   - `confidence_analysis_report.json` - Detailed statistical report
   - `confidence_visualizations/` - Folder with PNG charts

## 📊 Understanding the Visualizations

### Dashboard Components

1. **Overview Cards**
   - Average Confidence: Your overall journey score
   - Total Entries: Number of documented confidence moments
   - Peak Day: Your highest confidence day
   - Growth Trend: Month-over-month change percentage

2. **Timeline Chart**
   - Blue line: Daily average confidence
   - Green dashed: Personal confidence trend
   - Orange dashed: Professional confidence trend

3. **Category Distribution**
   - Donut chart showing which life areas you're tracking most
   - Hover for exact counts and percentages

4. **Calendar Heatmap**
   - Darker blue = higher confidence days
   - Gray = no data for that day
   - Hover to see exact scores

### Python Analysis Outputs

1. **Power Distribution Chart**
   - Shows how often each confidence level occurs
   - Helps identify your typical confidence range

2. **Category Comparison**
   - Horizontal bars comparing average confidence by category
   - Identifies strongest and weakest areas

3. **Time Series Analysis**
   - Daily confidence with 7-day moving average
   - Helps spot trends and patterns

4. **Category Correlations**
   - Heatmap showing which categories tend to occur together
   - Useful for understanding confidence relationships

## 🔧 Customization

### Adding New Categories
Edit `confidence-viz.js` and add to the `categories` array:
```javascript
this.categories = [
    'career_development',
    'personal_growth',
    // Add your new category here
];
```

### Changing Color Schemes
Modify the `categoryColors` object in `confidence-viz.js`:
```javascript
this.categoryColors = {
    'career_development': '#8B5CF6',
    // Add or modify colors
};
```

### Adjusting Analysis Thresholds
In `confidence_analysis.py`, modify:
```python
high_threshold = 7.5  # What counts as "high confidence"
low_threshold = 5.5   # What counts as "low confidence"
```

## 📈 Interpreting Your Results

### Positive Indicators
- **Upward growth trend** (green percentage)
- **High data completeness** (>80%)
- **Balanced personal/professional split**
- **Consistent high confidence streaks**

### Areas for Attention
- **Categories with low average scores** (<5.0)
- **High "low score ratio"** in any category
- **Declining recent trends**
- **Large gaps in data** (low completeness)

## 🤔 Troubleshooting

### Dashboard Issues
- **Charts not loading:** Ensure you're accessing via a web server, not file://
- **No data showing:** Check that `transcribed_data/final_20250711.json` exists
- **Filters not working:** Try refreshing the page

### Analysis Issues
- **Import errors:** Run `pip install -r requirements.txt`
- **No visualizations:** Check that `confidence_visualizations/` folder was created
- **Empty report:** Verify your JSON data file is properly formatted

## 💡 Tips for Better Tracking

1. **Be consistent:** Try to log entries daily
2. **Be specific:** Detailed descriptions help with later analysis
3. **Be honest:** Track both highs and lows for accurate insights
4. **Review regularly:** Use the dashboard weekly to spot patterns
5. **Act on insights:** Use recommendations to guide your growth

## 🔮 Future Enhancements

- Goal setting and progress tracking
- Mood correlation analysis
- Export to PDF reports
- Mobile-responsive design improvements
- Integration with calendar apps
- Predictive confidence modeling

---

Built with ❤️ to help you understand and grow your confidence journey.