const config = {
    // Always use the current origin for API calls
    apiUrl: window.location.origin,
    apiEndpoints: {
        analyze: '/api/analyze',
        upload: '/api/upload'
    }
};

// If running locally, update API URL to point to localhost
if (window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost') {
    config.apiUrl = 'http://localhost:5000';
}

export default config;
