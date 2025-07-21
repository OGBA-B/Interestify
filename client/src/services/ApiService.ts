import axios from 'axios'

const API = axios.create({
    baseURL: 'http://127.0.0.1:8000'  // Updated to use the FastAPI port
});

export default class ApiService {
    searchTweets(query: string) {
        return API.get(`search/${query}`);
    }

    getFollowers(query: string) {
        return API.get(`followers/${query}`);
    }

    // Dashboard API methods
    getDashboardSummary() {
        return API.get('/api/v1/dashboard/summary');
    }

    getGeographicSentiment(params: any = {}) {
        return API.get('/api/v1/dashboard/geographic-sentiment', { params });
    }

    getInterestTrends(params: any = {}) {
        return API.get('/api/v1/dashboard/interest-trends', { params });
    }
}