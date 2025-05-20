// Configuration file
window.config = {
    API_BASE_URL: window.location.origin,
    API_KEY: ''  // API key will be loaded from environment variables
};

// Load API key from environment
if (typeof process !== 'undefined' && process.env && process.env.GEMINI_API_KEY) {
    window.config.API_KEY = process.env.GEMINI_API_KEY;
} else if (typeof window !== 'undefined' && window.location) {
    // For development only - remove in production
    window.config.API_KEY = 'AIzaSyAhYUcUSjgW8_qHTg6a_uXqezq1JJ9JCiM';
}
