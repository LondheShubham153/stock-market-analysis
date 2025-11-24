# Stock Market Analytics Dashboard

A modern Python Streamlit application for real-time stock market data visualization and analysis, containerized with Docker for easy deployment.

## ⚠️ DISCLAIMER

**This application is for educational and demonstration purposes only.**

**DO NOT use this application for real stock market trading or investment decisions.**

- This is a demo application to showcase technical analysis and data visualization
- Data may be delayed, inaccurate, or incomplete
- Technical indicators and signals are for learning purposes only
- No financial advice is provided or implied
- Always consult with a licensed financial advisor before making any investment decisions
- Past performance does not guarantee future results
- The developers assume no liability for any financial losses incurred from using this application

**Use at your own risk.**

## 🚀 Quick Start

See [QUICK_START.md](QUICK_START.md) for detailed setup instructions.

**TL;DR:**
```bash
# Docker (Recommended)
cp config/.env.example .env  # Add your API key
cd docker && docker-compose up -d
# Access at http://localhost:8080

# Local
pip install -e . && streamlit run src/app.py
```

## Features

- Real-time stock data from Alpha Vantage API
- Support for major stocks: IBM, AAPL, MSFT, GOOGL, AMZN, TSLA, META
- Multiple time intervals: 1min, 5min, 15min, 30min, 60min
- Interactive charts: Price trends, Volume analysis, Candlestick patterns
- Key metrics: Current price, Change %, High/Low, Volume
- Modern UI with glass morphism effects
- Purple, yellow, and orange color theme
- Docker containerization for consistent deployment

## Quick Start with Docker (Recommended)

### Prerequisites
- Docker and Docker Compose installed
- Alpha Vantage API key ([Get free key](https://www.alphavantage.co/support/#api-key))

### Steps

1. **Clone or download the project**

2. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env and add your API key
   ```

3. **Start the application**:
   ```bash
   docker-compose up -d
   ```

4. **Access the dashboard**:
   Open your browser and navigate to http://localhost:8080

5. **Stop the application**:
   ```bash
   docker-compose down
   ```

## Local Development Setup

1. Ensure Python 3.9+ is installed
2. Create virtual environment:
   ```bash
   python3 -m venv venv
   ```

3. Activate virtual environment:
   ```bash
   source venv/bin/activate  # On macOS/Linux
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

### Method 1: Docker Compose (Recommended)
```bash
docker-compose up -d
```

### Method 2: Docker CLI
```bash
# Build the image
docker build -t stock-dashboard .

# Run the container
docker run -p 8080:8080 -e ALPHA_VANTAGE_API_KEY=your_key stock-dashboard
```

### Method 3: Local Development
```bash
# Using the startup script
./run.sh

# Or manually
source venv/bin/activate
streamlit run app.py --server.port 8080
```

The dashboard will be available at: http://localhost:8080

## Configuration

### Environment Variables

The application reads configuration from environment variables:

- `ALPHA_VANTAGE_API_KEY`: Your Alpha Vantage API key (required)

**For Docker**: Set in `.env` file or pass via `-e` flag  
**For local development**: Set in shell or use default in `config.py`

### Application Settings

Additional settings can be modified in `config.py`:
- `SUPPORTED_SYMBOLS`: List of stock symbols
- `TIME_INTERVALS`: Available time intervals
- `COLORS`: UI color theme
- `PORT`: Server port (default: 8080)

## Project Structure

```
.
├── app.py                 # Main Streamlit application
├── api_service.py         # Alpha Vantage API integration
├── data_processor.py      # Data processing and metrics
├── charts.py              # Plotly chart components
├── ui_components.py       # UI components and styling
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── Dockerfile             # Docker container definition
├── docker-compose.yml     # Docker Compose configuration
├── .env.example           # Environment variables template
├── .env                   # Environment variables (not in git)
├── run.sh                 # Local startup script
└── README.md             # This file
```

## Docker Details

### Dockerfile
- Base image: `python:3.11-slim`
- Exposed port: 8080
- Runs Streamlit with headless mode enabled
- Optimized with layer caching for faster builds

### Docker Compose
- Service name: `stock-dashboard`
- Port mapping: `8080:8080`
- Environment variables loaded from `.env` file
- Restart policy: `unless-stopped`
- Health check enabled

## Troubleshooting

### Docker Issues

**Container won't start:**
```bash
# Check logs
docker-compose logs -f

# Rebuild without cache
docker-compose build --no-cache
docker-compose up -d
```

**Port already in use:**
```bash
# Change port in docker-compose.yml
ports:
  - "8081:8080"  # Use 8081 on host instead
```

**Environment variables not loading:**
```bash
# Verify .env file exists and has correct format
cat .env

# Restart container
docker-compose restart
```

### API Issues

**Rate limit errors:**
- Free API keys have 5 requests/minute limit
- Wait 60 seconds between requests
- Consider upgrading to premium API key

**Invalid API key:**
- Verify key in `.env` file
- Get new key at https://www.alphavantage.co/support/#api-key

## API Information

This application uses the Alpha Vantage API for stock market data.
- API Documentation: https://www.alphavantage.co/documentation/
- Free API key: https://www.alphavantage.co/support/#api-key
- Rate limits: 5 requests/minute (free tier)

