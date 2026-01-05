// API Base URL - will be set by config.js or default to empty for local dev
let API_BASE = typeof window !== 'undefined' && window.API_BASE ? window.API_BASE : '';

// Global state
let companies = [];
let currentSymbol = null;
let priceChart = null;
let returnsChart = null;
let volumeChart = null;

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    loadCompanies();
    loadInsights();
    setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
    document.getElementById('timeFilter').addEventListener('change', () => {
        if (currentSymbol) {
            loadStockData(currentSymbol);
        }
    });

    document.getElementById('searchInput').addEventListener('input', (e) => {
        filterCompanies(e.target.value);
    });

    document.getElementById('compareBtn').addEventListener('click', () => {
        openCompareModal();
    });

    document.getElementById('predictBtn').addEventListener('click', () => {
        if (currentSymbol) {
            loadPrediction(currentSymbol);
        } else {
            alert('Please select a company first');
        }
    });

    document.getElementById('compareSubmit').addEventListener('click', () => {
        const symbol1 = document.getElementById('symbol1Select').value;
        const symbol2 = document.getElementById('symbol2Select').value;
        if (symbol1 && symbol2) {
            compareStocks(symbol1, symbol2);
        } else {
            alert('Please select both stocks');
        }
    });

    // Close modals
    document.querySelectorAll('.close').forEach(closeBtn => {
        closeBtn.addEventListener('click', (e) => {
            e.target.closest('.modal').style.display = 'none';
        });
    });

    window.addEventListener('click', (e) => {
        if (e.target.classList.contains('modal')) {
            e.target.style.display = 'none';
        }
    });
}

// Load companies list
async function loadCompanies() {
    try {
        const response = await fetch(`${API_BASE}/companies`);
        if (!response.ok) throw new Error('Failed to load companies');
        
        companies = await response.json();
        renderCompanies(companies);
    } catch (error) {
        console.error('Error loading companies:', error);
        document.getElementById('companiesList').innerHTML = 
            '<div class="error">Failed to load companies. Please try again later.</div>';
    }
}

// Render companies list
function renderCompanies(companiesList) {
    const container = document.getElementById('companiesList');
    if (companiesList.length === 0) {
        container.innerHTML = '<div class="loading">No companies found</div>';
        return;
    }

    container.innerHTML = companiesList.map(company => `
        <div class="company-item" data-symbol="${company.symbol}">
            <div class="symbol">${company.symbol}</div>
            <div class="name">${company.name}</div>
        </div>
    `).join('');

    // Add click listeners
    container.querySelectorAll('.company-item').forEach(item => {
        item.addEventListener('click', () => {
            const symbol = item.dataset.symbol;
            selectCompany(symbol);
        });
    });
}

// Filter companies
function filterCompanies(searchTerm) {
    const filtered = companies.filter(company => 
        company.symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
        company.name.toLowerCase().includes(searchTerm.toLowerCase())
    );
    renderCompanies(filtered);
}

// Select company
function selectCompany(symbol) {
    currentSymbol = symbol;
    
    // Update UI
    document.querySelectorAll('.company-item').forEach(item => {
        item.classList.remove('active');
        if (item.dataset.symbol === symbol) {
            item.classList.add('active');
        }
    });

    const company = companies.find(c => c.symbol === symbol);
    document.getElementById('selectedCompany').textContent = 
        company ? `${company.symbol} - ${company.name}` : symbol;

    // Load data
    loadStockData(symbol);
    loadSummary(symbol);
}

// Load stock data
async function loadStockData(symbol) {
    try {
        const days = document.getElementById('timeFilter').value;
        const response = await fetch(`${API_BASE}/data/${symbol}?days=${days}`);
        if (!response.ok) throw new Error('Failed to load stock data');
        
        const data = await response.json();
        renderCharts(data);
    } catch (error) {
        console.error('Error loading stock data:', error);
        alert('Failed to load stock data');
    }
}

// Load summary
async function loadSummary(symbol) {
    try {
        const response = await fetch(`${API_BASE}/data/summary/${symbol}`);
        if (!response.ok) throw new Error('Failed to load summary');
        
        const summary = await response.json();
        renderSummary(summary);
    } catch (error) {
        console.error('Error loading summary:', error);
    }
}

// Render charts
function renderCharts(data) {
    // Sort by date
    data.sort((a, b) => new Date(a.date) - new Date(b.date));
    
    const dates = data.map(d => d.date);
    const closes = data.map(d => d.close);
    const returns = data.map(d => d.daily_return || 0);
    const volumes = data.map(d => d.volume);
    const movingAvg = data.map(d => d.moving_avg_7 || d.close);

    // Price Chart
    const priceCtx = document.getElementById('priceChart').getContext('2d');
    if (priceChart) priceChart.destroy();
    priceChart = new Chart(priceCtx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: 'Closing Price',
                data: closes,
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                tension: 0.4
            }, {
                label: '7-Day MA',
                data: movingAvg,
                borderColor: '#764ba2',
                backgroundColor: 'rgba(118, 75, 162, 0.1)',
                tension: 0.4,
                borderDash: [5, 5]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: true
                }
            },
            scales: {
                y: {
                    beginAtZero: false
                }
            }
        }
    });

    // Returns Chart
    const returnsCtx = document.getElementById('returnsChart').getContext('2d');
    if (returnsChart) returnsChart.destroy();
    returnsChart = new Chart(returnsCtx, {
        type: 'bar',
        data: {
            labels: dates,
            datasets: [{
                label: 'Daily Return (%)',
                data: returns,
                backgroundColor: returns.map(r => r >= 0 ? 'rgba(16, 185, 129, 0.6)' : 'rgba(239, 68, 68, 0.6)')
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });

    // Volume Chart
    const volumeCtx = document.getElementById('volumeChart').getContext('2d');
    if (volumeChart) volumeChart.destroy();
    volumeChart = new Chart(volumeCtx, {
        type: 'bar',
        data: {
            labels: dates,
            datasets: [{
                label: 'Volume',
                data: volumes,
                backgroundColor: 'rgba(102, 126, 234, 0.6)'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });

    // Update volatility and sentiment from latest data
    if (data.length > 0) {
        const latest = data[data.length - 1];
        document.getElementById('volatilityScore').textContent = 
            latest.volatility_score ? latest.volatility_score.toFixed(2) : '-';
        document.getElementById('sentimentIndex').textContent = 
            latest.sentiment_index ? latest.sentiment_index.toFixed(2) : '-';
    }
}

// Render summary
function renderSummary(summary) {
    document.getElementById('week52High').textContent = 
        summary.week_52_high ? `₹${summary.week_52_high.toFixed(2)}` : '-';
    document.getElementById('week52Low').textContent = 
        summary.week_52_low ? `₹${summary.week_52_low.toFixed(2)}` : '-';
    document.getElementById('avgClose').textContent = 
        summary.avg_close ? `₹${summary.avg_close.toFixed(2)}` : '-';
    document.getElementById('currentPrice').textContent = 
        summary.current_price ? `₹${summary.current_price.toFixed(2)}` : '-';
}

// Load insights
async function loadInsights() {
    try {
        const response = await fetch(`${API_BASE}/insights`);
        if (!response.ok) throw new Error('Failed to load insights');
        
        const insights = await response.json();
        renderInsights(insights);
    } catch (error) {
        console.error('Error loading insights:', error);
    }
}

// Render insights
function renderInsights(insights) {
    // Top Gainers
    const gainersHtml = insights.top_gainers.map(item => `
        <div class="insight-item positive">
            <span class="symbol">${item.symbol}</span>
            <span class="value">+${item.daily_return.toFixed(2)}%</span>
        </div>
    `).join('');
    document.getElementById('topGainers').innerHTML = gainersHtml || '<div class="loading">No data</div>';

    // Top Losers
    const losersHtml = insights.top_losers.map(item => `
        <div class="insight-item negative">
            <span class="symbol">${item.symbol}</span>
            <span class="value">${item.daily_return.toFixed(2)}%</span>
        </div>
    `).join('');
    document.getElementById('topLosers').innerHTML = losersHtml || '<div class="loading">No data</div>';

    // Most Volatile
    const volatileHtml = insights.most_volatile.map(item => `
        <div class="insight-item">
            <span class="symbol">${item.symbol}</span>
            <span class="value">${item.volatility_score.toFixed(2)}</span>
        </div>
    `).join('');
    document.getElementById('mostVolatile').innerHTML = volatileHtml || '<div class="loading">No data</div>';
}

// Open compare modal
function openCompareModal() {
    const modal = document.getElementById('compareModal');
    const select1 = document.getElementById('symbol1Select');
    const select2 = document.getElementById('symbol2Select');

    // Populate selects
    select1.innerHTML = '<option value="">Select first stock</option>';
    select2.innerHTML = '<option value="">Select second stock</option>';
    companies.forEach(company => {
        const option1 = document.createElement('option');
        option1.value = company.symbol;
        option1.textContent = `${company.symbol} - ${company.name}`;
        select1.appendChild(option1);

        const option2 = document.createElement('option');
        option2.value = company.symbol;
        option2.textContent = `${company.symbol} - ${company.name}`;
        select2.appendChild(option2);
    });

    modal.style.display = 'block';
}

// Compare stocks
async function compareStocks(symbol1, symbol2) {
    try {
        const days = document.getElementById('timeFilter').value;
        const response = await fetch(
            `${API_BASE}/data/compare?symbol1=${symbol1}&symbol2=${symbol2}&days=${days}`
        );
        if (!response.ok) throw new Error('Failed to compare stocks');
        
        const comparison = await response.json();
        renderComparison(comparison);
    } catch (error) {
        console.error('Error comparing stocks:', error);
        alert('Failed to compare stocks');
    }
}

// Render comparison
function renderComparison(comparison) {
    const resultsDiv = document.getElementById('compareResults');
    resultsDiv.innerHTML = `
        <div class="prediction-card">
            <h3>Correlation: ${comparison.correlation.toFixed(4)}</h3>
            <p>${comparison.correlation > 0.7 ? 'Strong positive correlation' : 
                comparison.correlation > 0.3 ? 'Moderate correlation' : 
                comparison.correlation > -0.3 ? 'Weak correlation' : 
                'Negative correlation'}</p>
        </div>
        <div class="prediction-card">
            <h3>${comparison.symbol1}</h3>
            <p>52W High: ₹${comparison.symbol1_summary.week_52_high.toFixed(2)}</p>
            <p>52W Low: ₹${comparison.symbol1_summary.week_52_low.toFixed(2)}</p>
            <p>Current: ₹${comparison.symbol1_summary.current_price.toFixed(2)}</p>
        </div>
        <div class="prediction-card">
            <h3>${comparison.symbol2}</h3>
            <p>52W High: ₹${comparison.symbol2_summary.week_52_high.toFixed(2)}</p>
            <p>52W Low: ₹${comparison.symbol2_summary.week_52_low.toFixed(2)}</p>
            <p>Current: ₹${comparison.symbol2_summary.current_price.toFixed(2)}</p>
        </div>
    `;
}

// Load prediction
async function loadPrediction(symbol) {
    try {
        const modal = document.getElementById('predictModal');
        const resultsDiv = document.getElementById('predictionResults');
        
        resultsDiv.innerHTML = '<div class="loading">Generating prediction...</div>';
        modal.style.display = 'block';

        const response = await fetch(`${API_BASE}/insights/predict/${symbol}`);
        if (!response.ok) throw new Error('Failed to generate prediction');
        
        const prediction = await response.json();
        
        const change = prediction.predicted_price - prediction.current_price;
        const changePercent = (change / prediction.current_price) * 100;
        
        resultsDiv.innerHTML = `
            <div class="prediction-card">
                <h3>${prediction.symbol}</h3>
                <p>Current Price: ₹${prediction.current_price.toFixed(2)}</p>
                <p class="prediction-value">Predicted: ₹${prediction.predicted_price.toFixed(2)}</p>
                <p style="color: ${change >= 0 ? '#10b981' : '#ef4444'};">
                    ${change >= 0 ? '+' : ''}${change.toFixed(2)} (${changePercent >= 0 ? '+' : ''}${changePercent.toFixed(2)}%)
                </p>
                <p>Confidence: ${(prediction.confidence * 100).toFixed(1)}%</p>
                <p style="font-size: 0.9em; color: #666; margin-top: 10px;">
                    Prediction Date: ${prediction.prediction_date}
                </p>
            </div>
        `;
    } catch (error) {
        console.error('Error loading prediction:', error);
        document.getElementById('predictionResults').innerHTML = 
            '<div class="error">Failed to generate prediction. Please try again later.</div>';
    }
}

