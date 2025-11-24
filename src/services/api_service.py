# API Service module for fetching stock data from Alpha Vantage

import requests
import pandas as pd
from typing import Optional, Dict, Tuple
from src import config
from src.services import demo_data


def fetch_intraday_data(symbol: str, interval: str, api_key: str = config.ALPHA_VANTAGE_API_KEY) -> Tuple[Optional[Dict], bool]:
    """
    Fetch intraday time series data from Alpha Vantage API.
    Falls back to demo data if API is unavailable.
    
    Args:
        symbol: Stock symbol (e.g., 'IBM', 'AAPL')
        interval: Time interval ('1min', '5min', '15min', '30min', '60min')
        api_key: Alpha Vantage API key
        
    Returns:
        Tuple of (JSON response dict or None, is_demo_data boolean)
    """
    try:
        params = {
            "function": "TIME_SERIES_INTRADAY",
            "symbol": symbol,
            "interval": interval,
            "outputsize": "full",
            "apikey": api_key
        }
        
        response = requests.get(config.ALPHA_VANTAGE_BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Check for API error messages
        if "Error Message" in data:
            raise ValueError(f"Invalid symbol: {symbol}")
        if "Note" in data:
            raise ValueError("API rate limit reached. Using demo data instead.")
            
        return data, False
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            print(f"Invalid API key. Using demo data for {symbol}.")
        elif e.response.status_code == 429:
            print(f"API rate limit exceeded. Using demo data for {symbol}.")
        else:
            print(f"HTTP error occurred: {e}. Using demo data for {symbol}.")
        return None, True
    except requests.exceptions.ConnectionError:
        print(f"Network connection error. Using demo data for {symbol}.")
        return None, True
    except requests.exceptions.Timeout:
        print(f"Request timed out. Using demo data for {symbol}.")
        return None, True
    except Exception as e:
        print(f"Error occurred: {str(e)}. Using demo data for {symbol}.")
        return None, True


def parse_time_series(response: Optional[Dict], symbol: str = None, interval: str = None) -> pd.DataFrame:
    """
    Convert API response to pandas DataFrame.
    Falls back to demo data if response is None or invalid.
    
    Args:
        response: JSON response from Alpha Vantage API (or None for demo data)
        symbol: Stock symbol (used for demo data generation)
        interval: Time interval (used for demo data generation)
        
    Returns:
        DataFrame with columns: timestamp, open, high, low, close, volume
    """
    if not response:
        # Generate demo data if no response
        if symbol and interval:
            return demo_data.generate_demo_stock_data(symbol, interval)
        return pd.DataFrame()
    
    # Find the time series key (varies by interval)
    time_series_key = None
    for key in response.keys():
        if key.startswith("Time Series"):
            time_series_key = key
            break
    
    if not time_series_key:
        # Fall back to demo data if no valid time series found
        if symbol and interval:
            return demo_data.generate_demo_stock_data(symbol, interval)
        return pd.DataFrame()
    
    time_series = response[time_series_key]
    
    # Convert to DataFrame
    df = pd.DataFrame.from_dict(time_series, orient='index')
    
    # Rename columns
    df.columns = ['open', 'high', 'low', 'close', 'volume']
    
    # Convert index to datetime
    df.index = pd.to_datetime(df.index)
    df.index.name = 'timestamp'
    
    # Convert columns to numeric
    df['open'] = pd.to_numeric(df['open'])
    df['high'] = pd.to_numeric(df['high'])
    df['low'] = pd.to_numeric(df['low'])
    df['close'] = pd.to_numeric(df['close'])
    df['volume'] = pd.to_numeric(df['volume'])
    
    # Sort by timestamp
    df = df.sort_index()
    
    return df
