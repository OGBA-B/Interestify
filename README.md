# Interestify v2.0
A modern, scalable social media sentiment analysis platform that aggregates and analyzes posts from multiple data sources including Twitter, Reddit, Facebook, Instagram, and more.

## 🚀 Features

- **Multi-Platform Support**: Aggregate data from Twitter, Reddit, Facebook, Instagram, Truth Social, and more
- **Advanced Sentiment Analysis**: Multiple sentiment analysis engines (TextBlob, VADER) with confidence scoring
- **Dynamic Data Sources**: Add, remove, and configure data sources on-the-fly
- **Intelligent Caching**: Redis-based caching system to minimize API costs
- **Bot Detection**: Built-in bot detection and filtering
- **RESTful API**: Modern FastAPI-based REST API with automatic documentation
- **Real-time Analysis**: Async processing for better performance
- **Comprehensive Testing**: 100+ unit tests with extensive coverage
- **Database Integration**: SQLite/PostgreSQL support for data persistence

## 🏗️ Architecture

### New Project Structure
```
src/
├── api/                    # API endpoints and routes
├── core/
│   ├── sentiment/         # Sentiment analysis engines
│   ├── datasources/       # Data source implementations
│   └── cache/             # Caching system
├── models/                # Data models and schemas
├── utils/                 # Utility functions
└── main.py               # FastAPI application entry point

tests/                     # Comprehensive test suite
config/                    # Configuration files
client/                    # React frontend (existing)
```

### Key Components

#### Sentiment Analysis
- **Abstract Base Class**: `SentimentAnalyzer` for consistent interface
- **TextBlob Analyzer**: Lightweight, fast sentiment analysis
- **VADER Analyzer**: Specialized for social media text
- **Factory Pattern**: Easy switching between analyzers
- **Batch Processing**: Efficient analysis of multiple texts

#### Data Sources
- **Abstract Base Class**: `DataSource` for unified interface
- **Twitter Integration**: Twitter API v2 support
- **Reddit Integration**: Reddit API with post aggregation
- **Extensible**: Easy to add new platforms
- **Bot Detection**: Built-in filtering of suspicious content
- **Rate Limiting**: Configurable rate limits per source

#### Caching System
- **In-Memory Cache**: Fast access to frequent queries
- **TTL Support**: Configurable cache expiration
- **Cost Optimization**: Reduces API calls and costs
- **Statistics Tracking**: Monitor cache performance

## 🛠️ Installation

### Backend Setup

1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

2. **Set Environment Variables**
```bash
# Create .env file
cp .env.example .env

# Configure your API keys
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
```

3. **Initialize Database**
```bash
# Database will be automatically created on first run
# SQLite by default, PostgreSQL supported
```

4. **Run the Application**
```bash
# Development server
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Production server
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### Frontend Setup
```bash
cd client/
npm install
```

**Development Mode**
```bash
npm start
```

**Production Build**
```bash
npm run build
```

## 📚 API Documentation

### Base URL
```
http://localhost:8000
```

### Authentication
API keys are configured per data source in the admin interface.

### Main Endpoints

#### Analyze Posts
```http
POST /api/v1/analyze
```

**Request Body:**
```json
{
  "query": "machine learning",
  "limit": 50,
  "offset": 0,
  "data_sources": ["twitter", "reddit"],
  "include_sentiment": true,
  "min_confidence": 0.5,
  "language": "en"
}
```

**Response:**
```json
{
  "query": "machine learning",
  "total_posts": 25,
  "sentiment_distribution": {
    "positive": 15,
    "negative": 5,
    "neutral": 5
  },
  "average_confidence": 0.78,
  "sources_used": ["twitter", "reddit"],
  "posts": [...],
  "sentiment_results": [...],
  "created_at": "2023-01-01T00:00:00Z",
  "processing_time": 2.5
}
```

#### Get User Posts
```http
GET /api/v1/users/{user_id}/posts?source=twitter&limit=50
```

#### Data Source Management
```http
GET /api/v1/datasources
POST /api/v1/datasources
PUT /api/v1/datasources/{name}
DELETE /api/v1/datasources/{name}
```

#### Sentiment Analysis
```http
GET /api/v1/analyzers
POST /api/v1/analyze-text?text=Hello&analyzer_name=textblob
```

#### Cache Management
```http
GET /api/v1/cache/stats
DELETE /api/v1/cache/clear
DELETE /api/v1/cache/expired
```

### Interactive API Documentation
Visit `http://localhost:8000/docs` for interactive Swagger documentation.

## 🧪 Testing

### Run All Tests
```bash
pytest
```

### Run Specific Test Categories
```bash
# Unit tests only
pytest -m unit

# Integration tests
pytest -m integration

# API tests
pytest -m api

# Database tests
pytest -m database
```

### Test Coverage
```bash
pytest --cov=src --cov-report=html
```

### Performance Tests
```bash
pytest -m "not slow"  # Skip slow tests
pytest -m slow        # Run only slow tests
```

## 🔧 Configuration

### Environment Variables
```bash
# Database
DATABASE_URL=sqlite:///./interestify.db

# API Keys
TWITTER_API_KEY=your_key
TWITTER_API_SECRET=your_secret
REDDIT_CLIENT_ID=your_id
REDDIT_CLIENT_SECRET=your_secret

# Cache Settings
CACHE_TTL=3600
CACHE_MAX_SIZE=1000

# Rate Limiting
DEFAULT_RATE_LIMIT=100
```

### Data Source Configuration
Data sources can be configured through the API or admin interface:

```python
{
  "name": "twitter",
  "enabled": true,
  "api_key": "your_api_key",
  "api_secret": "your_api_secret",
  "rate_limit": 100,
  "timeout": 30,
  "cache_ttl": 3600,
  "bot_detection_threshold": 0.8
}
```

## 🤖 Bot Detection

The system includes built-in bot detection with configurable thresholds:

- **Engagement Anomalies**: Unusually high likes-to-text ratio
- **Content Patterns**: Excessive hashtags, mentions, or promotional phrases
- **Account Behavior**: New accounts with high activity
- **Text Analysis**: Generic or template-like content

## 📊 Performance Optimization

### Caching Strategy
- **Query Results**: Cache analysis results for identical queries
- **API Responses**: Cache raw API responses to reduce external calls
- **TTL Management**: Configurable cache expiration per data source

### Rate Limiting
- **Per-Source Limits**: Individual rate limits for each data source
- **Adaptive Throttling**: Automatic adjustment based on API quotas
- **Cost Tracking**: Monitor API usage and costs

### Database Optimization
- **Indexed Queries**: Optimized database queries for fast retrieval
- **Batch Operations**: Efficient bulk data operations
- **Connection Pooling**: Optimized database connections

## 🚀 Deployment

### Docker Deployment
```bash
# Build image
docker build -t interestify .

# Run container
docker run -p 8000:8000 interestify
```

### Production Considerations
- Use PostgreSQL for production database
- Configure Redis for production caching
- Set up proper environment variable management
- Enable logging and monitoring
- Configure reverse proxy (nginx)

## 🔄 Migration from v1.x

### Breaking Changes
- **API Structure**: New RESTful API endpoints
- **Database Schema**: New database structure
- **Configuration**: Environment-based configuration
- **Dependencies**: Updated to modern libraries

### Migration Steps
1. **Backup Data**: Export existing data if needed
2. **Update Dependencies**: Install new requirements
3. **Configure Environment**: Set up new environment variables
4. **Update Client**: Modify frontend to use new API endpoints
5. **Test Integration**: Run comprehensive tests

## 🤝 Contributing

### Development Setup
```bash
# Clone repository
git clone https://github.com/your-org/interestify.git

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run linting
flake8 src/
black src/
```


### Adding New Data Sources (Dynamic/Plugin System)
1. Create a new Python file in `src/core/datasources/plugins/` (e.g., `my_source.py`).
2. Implement a class inheriting from `DataSource` and required methods (`search_posts`, `get_user_posts`, etc.).
3. The system will auto-register all valid plugins on startup—no code changes required.
4. Write tests for your new data source.
5. Update documentation if needed.

## 🎯 Use Cases

- **Influencers, celebrities, and social climbers**: Assess your social status and general public sentiment across platforms. Sentiment analysis incorporates follower/following counts where available for richer context and social status scoring.
- **Companies and brands**: Gauge sentiment on products (e.g., PlayStation, Xbox) or brands, track public perception, and monitor campaigns.

## 🥅 Goals

- Efficient, simple, and portable codebase
- Easy addition/removal of data sources (plugin system, no hardcoding required)
- Accurate, explainable sentiment analysis
- Minimize API costs via caching and bot detection
- Comprehensive documentation and tests

### Code Style
- Follow PEP 8 guidelines
- Use type hints
- Write comprehensive docstrings
- Maintain test coverage above 90%

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Documentation
- [API Documentation](http://localhost:8000/docs)
- [Developer Guide](docs/developer-guide.md)
- [Deployment Guide](docs/deployment.md)

### Community
- [GitHub Issues](https://github.com/your-org/interestify/issues)
- [Discussions](https://github.com/your-org/interestify/discussions)

## 📈 Changelog

### v2.0.0 (Current)
- ✅ Complete rewrite with FastAPI
- ✅ Multi-platform data source support
- ✅ Advanced sentiment analysis
- ✅ Comprehensive caching system
- ✅ Bot detection and filtering
- ✅ 100+ unit tests
- ✅ Interactive API documentation
- ✅ Database integration
- ✅ Performance optimizations

### v1.x (Legacy)
- Basic Twitter integration
- Simple sentiment analysis
- Flask-based API
- Limited caching
- Basic testing

---

**Built with ❤️ for modern social media analysis**