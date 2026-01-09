// API Configuration
// This file allows easy configuration of the API base URL for different environments

// For local development (empty = same origin)
const API_BASE_LOCAL = '';

// For production - UPDATE THIS with your deployed backend URL
// Examples:
// - Render: https://your-app.onrender.com
// - Railway: https://your-app.railway.app
// - Heroku: https://your-app.herokuapp.com
// - Fly.io: https://your-app.fly.dev
// - Custom domain: https://api.yourdomain.com
const API_BASE_PRODUCTION = 'https://stock-data-intelligence-dashboard-3.onrender.com';

// Auto-detect environment
const isLocalhost = window.location.hostname === 'localhost' || 
                   window.location.hostname === '127.0.0.1' ||
                   window.location.hostname === '';

// Set the API base URL
// This will be used by app.js
window.API_BASE = isLocalhost ? API_BASE_LOCAL : API_BASE_PRODUCTION;

// Log for debugging
console.log('API Base URL:', window.API_BASE || '(using same origin)');
