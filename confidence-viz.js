// Confidence Visualization Dashboard
// Main JavaScript file for processing and visualizing confidence data

class ConfidenceVisualizer {
    constructor() {
        this.data = {};
        this.filteredData = {};
        this.charts = {};
        this.categories = [
            'career_development',
            'personal_growth',
            'self_image',
            'social_interactions',
            'technical_skills',
            'professional_presentation',
            'creative_work',
            'physical_wellness'
        ];
        this.categoryColors = {
            'career_development': '#8B5CF6',
            'personal_growth': '#10B981',
            'self_image': '#F59E0B',
            'social_interactions': '#3B82F6',
            'technical_skills': '#EF4444',
            'professional_presentation': '#6366F1',
            'creative_work': '#EC4899',
            'physical_wellness': '#14B8A6'
        };
    }

    async init() {
        await this.loadData();
        this.setupEventListeners();
        this.processData();
        this.updateUI();
        this.createCharts();
        this.displayEntries();
    }

    async loadData() {
        try {
            const response = await fetch('transcribed_data/final_20250711.json');
            this.data = await response.json();
            this.filteredData = { ...this.data };
        } catch (error) {
            console.error('Error loading data:', error);
            // Fallback to sample data for demo
            this.data = this.getSampleData();
            this.filteredData = { ...this.data };
        }
    }

    setupEventListeners() {
        // Filter listeners
        document.getElementById('typeFilter').addEventListener('change', () => this.applyFilters());
        document.getElementById('categoryFilter').addEventListener('change', () => this.applyFilters());
        document.getElementById('powerFilter').addEventListener('input', (e) => {
            document.getElementById('powerValue').textContent = `≥ ${e.target.value}`;
            this.applyFilters();
        });
        
        // Search listener
        document.getElementById('searchEntries').addEventListener('input', (e) => {
            this.searchEntries(e.target.value);
        });
        
        // Export button
        document.getElementById('exportBtn').addEventListener('click', () => this.exportReport());
        
        // Populate category filter
        this.populateCategoryFilter();
    }

    populateCategoryFilter() {
        const select = document.getElementById('categoryFilter');
        this.categories.forEach(category => {
            const option = document.createElement('option');
            option.value = category;
            option.textContent = this.formatCategoryName(category);
            select.appendChild(option);
        });
    }

    formatCategoryName(category) {
        return category
            .split('_')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    }

    processData() {
        // Calculate overall statistics
        const stats = this.calculateStats();
        
        // Update overview cards
        document.getElementById('avgConfidence').textContent = stats.avgConfidence.toFixed(1);
        document.getElementById('totalEntries').textContent = stats.totalEntries;
        document.getElementById('peakDay').textContent = this.formatDate(stats.peakDay);
        document.getElementById('peakDayScore').textContent = `Score: ${stats.peakScore.toFixed(1)}`;
        
        // Calculate growth trend
        const trend = this.calculateGrowthTrend();
        const trendElement = document.getElementById('growthTrend');
        trendElement.textContent = trend > 0 ? `+${trend.toFixed(1)}%` : `${trend.toFixed(1)}%`;
        trendElement.className = `text-3xl font-bold ${trend > 0 ? 'text-green-600' : 'text-red-600'}`;
        
        // Update date range
        const dates = Object.keys(this.data).sort();
        if (dates.length > 0) {
            const startDate = this.formatDate(dates[0]);
            const endDate = this.formatDate(dates[dates.length - 1]);
            document.getElementById('dateRange').textContent = `${startDate} - ${endDate}`;
        }
    }

    calculateStats() {
        let totalPower = 0;
        let totalEntries = 0;
        let peakDay = '';
        let peakScore = 0;
        
        Object.entries(this.filteredData).forEach(([date, dayData]) => {
            const entries = dayData.entries || [];
            entries.forEach(entry => {
                totalPower += entry.power_level;
                totalEntries++;
            });
            
            if (dayData.daily_confidence_average > peakScore) {
                peakScore = dayData.daily_confidence_average;
                peakDay = date;
            }
        });
        
        return {
            avgConfidence: totalEntries > 0 ? totalPower / totalEntries : 0,
            totalEntries,
            peakDay,
            peakScore
        };
    }

    calculateGrowthTrend() {
        const dates = Object.keys(this.data).sort();
        if (dates.length < 2) return 0;
        
        // Get first and last month averages
        const firstMonth = dates.slice(0, Math.floor(dates.length / 3));
        const lastMonth = dates.slice(-Math.floor(dates.length / 3));
        
        const firstAvg = this.getAverageForDates(firstMonth);
        const lastAvg = this.getAverageForDates(lastMonth);
        
        if (firstAvg === 0) return 0;
        return ((lastAvg - firstAvg) / firstAvg) * 100;
    }

    getAverageForDates(dates) {
        let total = 0;
        let count = 0;
        
        dates.forEach(date => {
            if (this.data[date] && this.data[date].entries) {
                this.data[date].entries.forEach(entry => {
                    total += entry.power_level;
                    count++;
                });
            }
        });
        
        return count > 0 ? total / count : 0;
    }

    createCharts() {
        this.createTimelineChart();
        this.createCategoryChart();
        this.createTypeChart();
        this.createCalendarHeatmap();
        this.displayInsights();
    }

    createTimelineChart() {
        const ctx = document.getElementById('timelineChart').getContext('2d');
        
        // Prepare data
        const dates = Object.keys(this.filteredData).sort();
        const dailyAverages = dates.map(date => ({
            x: date,
            y: this.filteredData[date].daily_confidence_average
        }));
        
        const personalData = dates.map(date => {
            const entries = this.filteredData[date].entries || [];
            const personalEntries = entries.filter(e => e.confidence_type === 'personal');
            const sum = personalEntries.reduce((acc, e) => acc + e.power_level, 0);
            return {
                x: date,
                y: personalEntries.length > 0 ? sum / personalEntries.length : null
            };
        });
        
        const professionalData = dates.map(date => {
            const entries = this.filteredData[date].entries || [];
            const profEntries = entries.filter(e => e.confidence_type === 'professional');
            const sum = profEntries.reduce((acc, e) => acc + e.power_level, 0);
            return {
                x: date,
                y: profEntries.length > 0 ? sum / profEntries.length : null
            };
        });
        
        if (this.charts.timeline) {
            this.charts.timeline.destroy();
        }
        
        this.charts.timeline = new Chart(ctx, {
            type: 'line',
            data: {
                datasets: [
                    {
                        label: 'Daily Average',
                        data: dailyAverages,
                        borderColor: '#6366F1',
                        backgroundColor: 'rgba(99, 102, 241, 0.1)',
                        borderWidth: 3,
                        pointRadius: 4,
                        pointHoverRadius: 6,
                        tension: 0.3
                    },
                    {
                        label: 'Personal',
                        data: personalData,
                        borderColor: '#10B981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        borderWidth: 2,
                        pointRadius: 3,
                        tension: 0.3,
                        borderDash: [5, 5]
                    },
                    {
                        label: 'Professional',
                        data: professionalData,
                        borderColor: '#F59E0B',
                        backgroundColor: 'rgba(245, 158, 11, 0.1)',
                        borderWidth: 2,
                        pointRadius: 3,
                        tension: 0.3,
                        borderDash: [5, 5]
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                    }
                },
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: 'day',
                            displayFormats: {
                                day: 'MMM d'
                            }
                        }
                    },
                    y: {
                        beginAtZero: true,
                        max: 10,
                        title: {
                            display: true,
                            text: 'Confidence Level'
                        }
                    }
                }
            }
        });
    }

    createCategoryChart() {
        const ctx = document.getElementById('categoryChart').getContext('2d');
        
        // Count entries by category
        const categoryCounts = {};
        Object.values(this.filteredData).forEach(dayData => {
            (dayData.entries || []).forEach(entry => {
                categoryCounts[entry.category] = (categoryCounts[entry.category] || 0) + 1;
            });
        });
        
        const labels = Object.keys(categoryCounts).map(cat => this.formatCategoryName(cat));
        const data = Object.values(categoryCounts);
        const colors = Object.keys(categoryCounts).map(cat => this.categoryColors[cat] || '#999');
        
        if (this.charts.category) {
            this.charts.category.destroy();
        }
        
        this.charts.category = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: colors,
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            padding: 10,
                            font: {
                                size: 11
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((context.parsed / total) * 100).toFixed(1);
                                return `${context.label}: ${context.parsed} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }

    createTypeChart() {
        const ctx = document.getElementById('typeChart').getContext('2d');
        
        // Count by type
        let personal = 0;
        let professional = 0;
        
        Object.values(this.filteredData).forEach(dayData => {
            (dayData.entries || []).forEach(entry => {
                if (entry.confidence_type === 'personal') personal++;
                else if (entry.confidence_type === 'professional') professional++;
            });
        });
        
        if (this.charts.type) {
            this.charts.type.destroy();
        }
        
        this.charts.type = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: ['Personal', 'Professional'],
                datasets: [{
                    data: [personal, professional],
                    backgroundColor: ['#10B981', '#F59E0B'],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            font: {
                                size: 14
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((context.parsed / total) * 100).toFixed(1);
                                return `${context.label}: ${context.parsed} entries (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }

    createCalendarHeatmap() {
        const container = document.getElementById('calendarHeatmap');
        container.innerHTML = '';
        
        // Create calendar grid
        const dates = Object.keys(this.filteredData).sort();
        if (dates.length === 0) return;
        
        const startDate = new Date(dates[0]);
        const endDate = new Date(dates[dates.length - 1]);
        
        // Create month headers
        const months = this.getMonthsBetween(startDate, endDate);
        const monthHeader = document.createElement('div');
        monthHeader.className = 'flex gap-8 mb-2 text-sm text-gray-600';
        months.forEach(month => {
            const span = document.createElement('span');
            span.textContent = month;
            monthHeader.appendChild(span);
        });
        container.appendChild(monthHeader);
        
        // Create calendar grid
        const grid = document.createElement('div');
        grid.className = 'grid grid-cols-7 gap-1';
        
        // Add day labels
        ['S', 'M', 'T', 'W', 'T', 'F', 'S'].forEach(day => {
            const label = document.createElement('div');
            label.className = 'text-xs text-gray-500 text-center';
            label.textContent = day;
            grid.appendChild(label);
        });
        
        // Fill calendar
        let currentDate = new Date(startDate);
        currentDate.setDate(1); // Start from beginning of month
        
        // Add empty cells for days before start
        const startDay = currentDate.getDay();
        for (let i = 0; i < startDay; i++) {
            const empty = document.createElement('div');
            grid.appendChild(empty);
        }
        
        // Add all days
        while (currentDate <= endDate) {
            const dateStr = this.formatDateISO(currentDate);
            const dayData = this.filteredData[dateStr];
            
            const cell = document.createElement('div');
            cell.className = 'w-8 h-8 rounded cursor-pointer relative group';
            
            if (dayData) {
                const score = dayData.daily_confidence_average;
                const intensity = Math.floor((score / 10) * 5);
                cell.className += ` bg-indigo-${intensity * 100 + 100}`;
                cell.title = `${dateStr}: ${score.toFixed(1)}`;
                
                // Add hover tooltip
                const tooltip = document.createElement('div');
                tooltip.className = 'absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 bg-gray-800 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-10';
                tooltip.textContent = `${this.formatDate(dateStr)}: ${score.toFixed(1)}`;
                cell.appendChild(tooltip);
            } else {
                cell.className += ' bg-gray-100';
            }
            
            grid.appendChild(cell);
            currentDate.setDate(currentDate.getDate() + 1);
        }
        
        container.appendChild(grid);
        
        // Add legend
        const legend = document.createElement('div');
        legend.className = 'flex items-center gap-2 mt-4 text-sm text-gray-600';
        legend.innerHTML = `
            <span>Less</span>
            <div class="flex gap-1">
                <div class="w-4 h-4 bg-gray-100 rounded"></div>
                <div class="w-4 h-4 bg-indigo-200 rounded"></div>
                <div class="w-4 h-4 bg-indigo-300 rounded"></div>
                <div class="w-4 h-4 bg-indigo-400 rounded"></div>
                <div class="w-4 h-4 bg-indigo-500 rounded"></div>
                <div class="w-4 h-4 bg-indigo-600 rounded"></div>
            </div>
            <span>More</span>
        `;
        container.appendChild(legend);
    }

    getMonthsBetween(startDate, endDate) {
        const months = [];
        const current = new Date(startDate);
        current.setDate(1);
        
        while (current <= endDate) {
            months.push(current.toLocaleDateString('en-US', { month: 'short', year: 'numeric' }));
            current.setMonth(current.getMonth() + 1);
        }
        
        return months;
    }

    displayInsights() {
        // Top moments
        const topMoments = this.getTopMoments(5);
        const topContainer = document.getElementById('topMoments');
        topContainer.innerHTML = '';
        
        topMoments.forEach(moment => {
            const div = document.createElement('div');
            div.className = 'border-l-4 border-green-500 pl-4 py-2';
            div.innerHTML = `
                <div class="flex items-start justify-between">
                    <div class="flex-1">
                        <p class="text-sm text-gray-800">${moment.text}</p>
                        <p class="text-xs text-gray-500 mt-1">
                            ${this.formatDate(moment.date)} • 
                            ${this.formatCategoryName(moment.category)} • 
                            <span class="font-semibold text-green-600">Level ${moment.power_level}</span>
                        </p>
                    </div>
                </div>
            `;
            topContainer.appendChild(div);
        });
        
        // Growth areas
        const growthAreas = this.getGrowthAreas(5);
        const growthContainer = document.getElementById('growthAreas');
        growthContainer.innerHTML = '';
        
        growthAreas.forEach(area => {
            const div = document.createElement('div');
            div.className = 'border-l-4 border-amber-500 pl-4 py-2';
            div.innerHTML = `
                <div class="flex items-start justify-between">
                    <div class="flex-1">
                        <p class="text-sm text-gray-800">${area.text}</p>
                        <p class="text-xs text-gray-500 mt-1">
                            ${this.formatDate(area.date)} • 
                            ${this.formatCategoryName(area.category)} • 
                            <span class="font-semibold text-amber-600">Level ${area.power_level}</span>
                        </p>
                    </div>
                </div>
            `;
            growthContainer.appendChild(div);
        });
    }

    getTopMoments(count) {
        const allEntries = [];
        Object.entries(this.filteredData).forEach(([date, dayData]) => {
            (dayData.entries || []).forEach(entry => {
                allEntries.push({ ...entry, date });
            });
        });
        
        return allEntries
            .sort((a, b) => b.power_level - a.power_level)
            .slice(0, count);
    }

    getGrowthAreas(count) {
        const allEntries = [];
        Object.entries(this.filteredData).forEach(([date, dayData]) => {
            (dayData.entries || []).forEach(entry => {
                allEntries.push({ ...entry, date });
            });
        });
        
        return allEntries
            .sort((a, b) => a.power_level - b.power_level)
            .slice(0, count);
    }

    displayEntries() {
        const container = document.getElementById('entriesList');
        container.innerHTML = '';
        
        const allEntries = [];
        Object.entries(this.filteredData).forEach(([date, dayData]) => {
            (dayData.entries || []).forEach(entry => {
                allEntries.push({ ...entry, date });
            });
        });
        
        // Sort by date (newest first)
        allEntries.sort((a, b) => new Date(b.date) - new Date(a.date));
        
        allEntries.forEach(entry => {
            const div = document.createElement('div');
            div.className = 'border rounded-lg p-4 hover:bg-gray-50 transition';
            
            const powerColor = entry.power_level >= 7 ? 'text-green-600' : 
                              entry.power_level >= 5 ? 'text-amber-600' : 'text-red-600';
            
            div.innerHTML = `
                <div class="flex items-start justify-between">
                    <div class="flex-1">
                        <p class="text-sm text-gray-800">${entry.text}</p>
                        <div class="flex items-center gap-4 mt-2 text-xs text-gray-500">
                            <span>${this.formatDate(entry.date)}</span>
                            <span class="px-2 py-1 bg-gray-100 rounded">
                                ${this.formatCategoryName(entry.category)}
                            </span>
                            <span class="px-2 py-1 ${entry.confidence_type === 'personal' ? 'bg-green-100' : 'bg-amber-100'} rounded">
                                ${entry.confidence_type}
                            </span>
                            <span class="font-semibold ${powerColor}">
                                Level ${entry.power_level}
                            </span>
                        </div>
                    </div>
                </div>
            `;
            container.appendChild(div);
        });
    }

    applyFilters() {
        const typeFilter = document.getElementById('typeFilter').value;
        const categoryFilter = document.getElementById('categoryFilter').value;
        const powerFilter = parseInt(document.getElementById('powerFilter').value);
        
        // Reset filtered data
        this.filteredData = {};
        
        Object.entries(this.data).forEach(([date, dayData]) => {
            const filteredEntries = (dayData.entries || []).filter(entry => {
                if (typeFilter !== 'all' && entry.confidence_type !== typeFilter) return false;
                if (categoryFilter !== 'all' && entry.category !== categoryFilter) return false;
                if (entry.power_level < powerFilter) return false;
                return true;
            });
            
            if (filteredEntries.length > 0) {
                this.filteredData[date] = {
                    entries: filteredEntries,
                    daily_confidence_average: filteredEntries.reduce((sum, e) => sum + e.power_level, 0) / filteredEntries.length,
                    dominant_confidence_area: this.getDominantType(filteredEntries)
                };
            }
        });
        
        this.updateUI();
    }

    getDominantType(entries) {
        const counts = {};
        entries.forEach(entry => {
            counts[entry.confidence_type] = (counts[entry.confidence_type] || 0) + 1;
        });
        
        return Object.entries(counts).sort((a, b) => b[1] - a[1])[0]?.[0] || 'personal';
    }

    searchEntries(query) {
        if (!query) {
            this.displayEntries();
            return;
        }
        
        const container = document.getElementById('entriesList');
        container.innerHTML = '';
        
        const allEntries = [];
        Object.entries(this.filteredData).forEach(([date, dayData]) => {
            (dayData.entries || []).forEach(entry => {
                if (entry.text.toLowerCase().includes(query.toLowerCase())) {
                    allEntries.push({ ...entry, date });
                }
            });
        });
        
        if (allEntries.length === 0) {
            container.innerHTML = '<p class="text-gray-500 text-center py-4">No entries found</p>';
            return;
        }
        
        allEntries.sort((a, b) => new Date(b.date) - new Date(a.date));
        
        allEntries.forEach(entry => {
            const div = document.createElement('div');
            div.className = 'border rounded-lg p-4 hover:bg-gray-50 transition';
            
            const powerColor = entry.power_level >= 7 ? 'text-green-600' : 
                              entry.power_level >= 5 ? 'text-amber-600' : 'text-red-600';
            
            // Highlight search term
            const highlightedText = entry.text.replace(
                new RegExp(query, 'gi'),
                match => `<span class="bg-yellow-200">${match}</span>`
            );
            
            div.innerHTML = `
                <div class="flex items-start justify-between">
                    <div class="flex-1">
                        <p class="text-sm text-gray-800">${highlightedText}</p>
                        <div class="flex items-center gap-4 mt-2 text-xs text-gray-500">
                            <span>${this.formatDate(entry.date)}</span>
                            <span class="px-2 py-1 bg-gray-100 rounded">
                                ${this.formatCategoryName(entry.category)}
                            </span>
                            <span class="px-2 py-1 ${entry.confidence_type === 'personal' ? 'bg-green-100' : 'bg-amber-100'} rounded">
                                ${entry.confidence_type}
                            </span>
                            <span class="font-semibold ${powerColor}">
                                Level ${entry.power_level}
                            </span>
                        </div>
                    </div>
                </div>
            `;
            container.appendChild(div);
        });
    }

    updateUI() {
        this.processData();
        this.createCharts();
        this.displayEntries();
    }

    formatDate(dateStr) {
        const date = new Date(dateStr);
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    }

    formatDateISO(date) {
        const year = date.getFullYear();
        const month = (date.getMonth() + 1).toString().padStart(2, '0');
        const day = date.getDate().toString().padStart(2, '0');
        return `${year}-${month}-${day}`;
    }

    exportReport() {
        // Prepare data for export
        const report = {
            summary: {
                dateRange: document.getElementById('dateRange').textContent,
                averageConfidence: parseFloat(document.getElementById('avgConfidence').textContent),
                totalEntries: parseInt(document.getElementById('totalEntries').textContent),
                peakDay: document.getElementById('peakDay').textContent,
                growthTrend: document.getElementById('growthTrend').textContent
            },
            topMoments: this.getTopMoments(10),
            growthAreas: this.getGrowthAreas(10),
            categoryBreakdown: this.getCategoryBreakdown(),
            allData: this.data
        };
        
        // Download as JSON
        const dataStr = JSON.stringify(report, null, 2);
        const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
        
        const exportFileDefaultName = `confidence-report-${new Date().toISOString().split('T')[0]}.json`;
        
        const linkElement = document.createElement('a');
        linkElement.setAttribute('href', dataUri);
        linkElement.setAttribute('download', exportFileDefaultName);
        linkElement.click();
    }

    getCategoryBreakdown() {
        const breakdown = {};
        this.categories.forEach(category => {
            breakdown[category] = {
                count: 0,
                totalPower: 0,
                avgPower: 0
            };
        });
        
        Object.values(this.data).forEach(dayData => {
            (dayData.entries || []).forEach(entry => {
                if (breakdown[entry.category]) {
                    breakdown[entry.category].count++;
                    breakdown[entry.category].totalPower += entry.power_level;
                }
            });
        });
        
        // Calculate averages
        Object.keys(breakdown).forEach(category => {
            if (breakdown[category].count > 0) {
                breakdown[category].avgPower = 
                    breakdown[category].totalPower / breakdown[category].count;
            }
        });
        
        return breakdown;
    }

    // Sample data fallback for demo
    getSampleData() {
        return {
            "2025-05-09": {
                "entries": [
                    {
                        "text": "Come up with ideas for trying to get in AI startup school",
                        "category": "career_development",
                        "confidence_type": "professional",
                        "power_level": 7
                    }
                ],
                "daily_confidence_average": 7.0,
                "dominant_confidence_area": "professional"
            }
        };
    }
}

// Initialize the dashboard when the page loads
document.addEventListener('DOMContentLoaded', () => {
    const visualizer = new ConfidenceVisualizer();
    visualizer.init();
});