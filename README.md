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

## 🛠️ Installation & Build

### Quick Start (Recommended)

The easiest way to get Interestify running is using the provided build and run scripts:

1. **Build the Application**
```bash
./build.sh
```
This script will:
- Set up Python virtual environment
- Install all backend dependencies
- Install frontend dependencies
- Create environment configuration
- Download required NLTK data
- Build the production frontend
- Test the backend startup

2. **Run the Application**
```bash
./run.sh
```
This script will:
- Start the FastAPI backend server on http://localhost:8000
- Start the React frontend server on http://localhost:3000
- Display access URLs and log locations
- Handle graceful shutdown with Ctrl+C

3. **Access the Application**
- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Manual Installation

If you prefer to set up manually:

#### Backend Setup

1. **Install Dependencies**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn sqlalchemy aiosqlite python-dotenv textblob vaderSentiment aiohttp greenlet
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
source .venv/bin/activate
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Production server
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000
```

#### Frontend Setup
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

### Build Scripts

#### build.sh
Comprehensive build script that:
- Sets up Python virtual environment
- Installs all dependencies
- Creates environment configuration
- Downloads NLTK data for sentiment analysis
- Builds production frontend
- Creates necessary directories
- Tests backend functionality

#### run.sh
Production-ready run script that:
- Starts both backend and frontend servers
- Provides colored output and status updates
- Logs output to files in `logs/` directory
- Handles graceful shutdown
- Monitors server health
- Displays access URLs and helpful information

## � Build

### Automated Build Process

Interestify includes automated build scripts for easy setup and deployment:

#### Build Script (`build.sh`)
```bash
./build.sh
```

**What it does:**
- ✅ Creates Python virtual environment
- ✅ Installs all backend dependencies (FastAPI, SQLAlchemy, sentiment analysis libraries)
- ✅ Installs frontend dependencies (React, Material-UI)
- ✅ Sets up environment configuration (.env file)
- ✅ Downloads NLTK data for TextBlob sentiment analysis
- ✅ Builds production-optimized React frontend
- ✅ Creates necessary directories (logs/, data/)
- ✅ Tests backend startup functionality
- ✅ Provides helpful next steps

#### Run Script (`run.sh`)
```bash
./run.sh
```

**What it does:**
- 🚀 Starts FastAPI backend server (http://localhost:8000)
- 🌐 Starts React frontend server (http://localhost:3000)
- 📊 Provides real-time status updates with colored output
- 📝 Logs all output to `logs/backend.log` and `logs/frontend.log`
- 🔄 Monitors server health and auto-restarts if needed
- 🛑 Handles graceful shutdown on Ctrl+C
- 📱 Displays access URLs and helpful information

### Build Requirements

**System Requirements:**
- Python 3.8+ (Python 3.11+ recommended)
- Node.js 14+ and npm
- Git
- 4GB+ RAM (for sentiment analysis models)
- 2GB+ disk space

**Dependencies Installed:**
- **Backend:** FastAPI, Uvicorn, SQLAlchemy, Pydantic, TextBlob, VADER Sentiment, aiohttp
- **Frontend:** React, TypeScript, Material-UI, Chart.js, Axios

### Development Build

For development with hot reload:
```bash
# Backend (Terminal 1)
source .venv/bin/activate
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (Terminal 2)
cd client
npm start
```

### Production Build

For production deployment:
```bash
# Build frontend for production
cd client
npm run build

# Start backend in production mode
source .venv/bin/activate
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### Build Troubleshooting

**Common Issues:**

1. **Python version incompatibility**
   ```bash
   # Use specific Python version
   python3.11 -m venv .venv
   ```

2. **Node.js dependency conflicts**
   ```bash
   cd client
   rm -rf node_modules package-lock.json
   npm install
   ```

3. **Virtual environment issues**
   ```bash
   rm -rf .venv
   ./build.sh  # Rebuild from scratch
   ```

4. **Port conflicts**
   ```bash
   # Kill processes on ports 3000 and 8000
   lsof -ti:3000 | xargs kill -9
   lsof -ti:8000 | xargs kill -9
   ```

### Docker Build (Alternative)

```bash
# Build Docker image
docker build -t interestify .

# Run container
docker run -p 8000:8000 -p 3000:3000 interestify
```

## �📝 How to Use Interestify

### Quick Start
1. **Build and start the application:**
   ```bash
   ./build.sh  # First time setup
   ./run.sh    # Start the application
   ```

2. **Access the application:**
   - Frontend: http://localhost:3000
   - API: http://localhost:8000/docs

### Manual Startup
After installing dependencies and configuring your `.env` file:

1. **Start the Backend**
   ```bash
   source .venv/bin/activate
   python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```
   The API will be available at `http://localhost:8000`.

2. **Start the Frontend**
   ```bash
   cd client
   npm start
   ```
   Visit `http://localhost:3000` in your browser.

### Using the Application

3. **Search for Topics**
   - Enter keywords in the search bar.
   - Select data sources (Twitter, Reddit, etc.) to query.
   - Submit your search.

4. **View Sentiment Results**
   - See aggregated posts and sentiment charts.
   - Click items for detailed information.

5. **Manage Data Sources**
   - Toggle sources on the settings page.
   - Update API keys or switch analyzers.

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
