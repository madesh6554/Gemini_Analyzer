const config = {
    apiUrl: window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost'
        ? 'http://localhost:5000'
        : 'https://gemini-analyzer.onrender.com',
    apiEndpoints: {
        analyze: '/api/analyze',
        upload: '/api/upload'
    }
};

export default config;
