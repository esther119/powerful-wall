import React, { useState, useMemo } from 'react';
import './App.css';
import confidenceDataJson from './confidenceData.json';
import { ConfidenceData, Category, ConfidenceType } from './types';
import { TimeSeriesChart } from './components/TimeSeriesChart';
import { CategoryBreakdown } from './components/CategoryBreakdown';
import { PowerDistribution } from './components/PowerDistribution';
import { OverviewStats } from './components/OverviewStats';
import { DailyDetails } from './components/DailyDetails';
import { CalendarHeatmap } from './components/CalendarHeatmap';
import { Filter } from 'lucide-react';

// Type assertion to ensure JSON data matches our types
const confidenceData = confidenceDataJson as ConfidenceData;

function App() {
  const [selectedCategory, setSelectedCategory] = useState<Category | null>(null);
  const [selectedType, setSelectedType] = useState<ConfidenceType | null>(null);
  const [selectedDate, setSelectedDate] = useState<string | null>(null);

  const filteredData = useMemo(() => {
    if (!selectedCategory && !selectedType) return confidenceData;

    const filtered: ConfidenceData = {};
    
    Object.entries(confidenceData).forEach(([date, dayData]) => {
      const filteredEntries = dayData.entries.filter(entry => {
        const categoryMatch = !selectedCategory || entry.category === selectedCategory;
        const typeMatch = !selectedType || entry.confidence_type === selectedType;
        return categoryMatch && typeMatch;
      });

      if (filteredEntries.length > 0) {
        const powerLevels = filteredEntries.map(e => e.power_level);
        const avg = powerLevels.reduce((a, b) => a + b, 0) / powerLevels.length;
        const personalCount = filteredEntries.filter(e => e.confidence_type === 'personal').length;
        
        filtered[date] = {
          entries: filteredEntries,
          daily_confidence_average: avg,
          dominant_confidence_area: personalCount > filteredEntries.length / 2 ? 'personal' : 'professional',
        };
      }
    });

    return filtered;
  }, [selectedCategory, selectedType]);

  const clearFilters = () => {
    setSelectedCategory(null);
    setSelectedType(null);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Confidence Journey Dashboard</h1>
        <p>Tracking personal and professional growth over time</p>
      </header>

      <div className="filters">
        <div className="filter-group">
          <label>Category:</label>
          <select 
            value={selectedCategory || ''} 
            onChange={(e) => setSelectedCategory(e.target.value as Category || null)}
          >
            <option value="">All Categories</option>
            <option value="career_development">Career Development</option>
            <option value="personal_growth">Personal Growth</option>
            <option value="professional_presentation">Professional Presentation</option>
            <option value="technical_skills">Technical Skills</option>
            <option value="social_interactions">Social Interactions</option>
            <option value="self_image">Self Image</option>
            <option value="physical_wellness">Physical Wellness</option>
            <option value="creative_work">Creative Work</option>
          </select>
        </div>

        <div className="filter-group">
          <label>Type:</label>
          <select 
            value={selectedType || ''} 
            onChange={(e) => setSelectedType(e.target.value as ConfidenceType || null)}
          >
            <option value="">All Types</option>
            <option value="personal">Personal</option>
            <option value="professional">Professional</option>
          </select>
        </div>

        {(selectedCategory || selectedType) && (
          <button className="clear-filters" onClick={clearFilters}>
            <Filter size={16} /> Clear Filters
          </button>
        )}
      </div>

      <div className="dashboard-grid">
        <div className="overview-section">
          <OverviewStats data={filteredData} />
        </div>

        <div className="chart-section">
          <h2>Confidence Over Time</h2>
          <TimeSeriesChart data={filteredData} />
        </div>

        <div className="calendar-section">
          <h2>Daily Confidence Calendar</h2>
          <CalendarHeatmap 
            data={filteredData} 
            onDateSelect={setSelectedDate}
            selectedDate={selectedDate}
          />
        </div>

        <div className="category-section">
          <h2>Performance by Category</h2>
          <CategoryBreakdown 
            data={filteredData} 
            onCategorySelect={setSelectedCategory}
            selectedCategory={selectedCategory}
          />
        </div>

        <div className="distribution-section">
          <h2>Power Level Distribution</h2>
          <PowerDistribution data={filteredData} />
        </div>

        {selectedDate && confidenceData[selectedDate] && (
          <div className="details-section">
            <DailyDetails 
              date={selectedDate} 
              data={confidenceData[selectedDate]}
              onClose={() => setSelectedDate(null)}
            />
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
