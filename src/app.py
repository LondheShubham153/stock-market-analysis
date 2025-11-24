# Stock Market Analytics Dashboard - Main Application

import streamlit as st
from src import config
from src.services import api_service
from src.core import data_processor, technical_indicators
from src.ui import charts
from src.ui import components as ui_components
from src.managers import watchlist_manager, refresh_manager

# Page configuration
st.set_page_config(
    page_title="Stock Market Analytics Dashboard (JOSH Batch 10)",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
ui_components.apply_custom_css()
ui_components.add_smooth_transitions()

# Initialize session state for caching
if 'cached_data' not in st.session_state:
    st.session_state.cached_data = {}

# Initialize previous price for change detection
if 'previous_price' not in st.session_state:
    st.session_state.previous_price = {}

# Initialize watchlist and refresh managers
watchlist_manager.initialize_watchlist()
refresh_manager.initialize_refresh_state()

# Initialize disclaimer state
if 'disclaimer_accepted' not in st.session_state:
    st.session_state.disclaimer_accepted = False

# Show disclaimer banner if not accepted
if not st.session_state.disclaimer_accepted:
    st.error("""
    ### ⚠️ IMPORTANT DISCLAIMER - For JOSH Batch 10 Please Read Before Continuing
    
    **This application is for EDUCATIONAL and DEMONSTRATION purposes only.**
    
    #### DO NOT use this application for real stock market trading or investment decisions.
    
    **Important Points:**
    - This is a demo application to showcase technical analysis features
    - Data may be delayed or inaccurate  
    - Technical indicators are for educational purposes only
    - No financial advice is provided or implied
    - Always consult with a licensed financial advisor before making investment decisions
    - Past performance does not guarantee future results
    - The developers assume no liability for any financial losses
    
    **By clicking "I Understand" below, you acknowledge that you will use this application for educational purposes only.**
    """)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("✅ I Understand and Accept", type="primary", use_container_width=True, key="accept_disclaimer"):
            st.session_state.disclaimer_accepted = True
            st.rerun()
    
    st.stop()  # Stop execution until disclaimer is accepted

# Header
st.title("📈 Stock Market Analytics Dashboard (JOSH Batch 10)")
st.markdown("Real-time stock market data visualization and analysis")
st.caption("⚠️ Educational demo only - Not for real trading")

# Sidebar
with st.sidebar:
    st.header("Settings")
    
    # Stock selector
    selected_symbol = ui_components.render_stock_selector(config.SUPPORTED_SYMBOLS)
    
    # Interval selector
    selected_interval = ui_components.render_interval_selector()
    
    st.markdown("---")
    
    # Watchlist Section
    st.markdown("### ⭐ Watchlist")
    
    # Add to watchlist button
    if not watchlist_manager.is_in_watchlist(selected_symbol):
        if st.button(f"➕ Add {selected_symbol} to Watchlist", key="add_watchlist"):
            if watchlist_manager.is_watchlist_full():
                ui_components.render_toast_notification(
                    f"Watchlist is full ({watchlist_manager.get_watchlist_max_size()} stocks max)",
                    "warning"
                )
            else:
                if watchlist_manager.add_to_watchlist(selected_symbol):
                    ui_components.render_toast_notification(
                        f"Added {selected_symbol} to watchlist!",
                        "success"
                    )
                    st.rerun()
    else:
        st.info(f"✓ {selected_symbol} is in your watchlist")
    
    # Display watchlist
    watchlist = watchlist_manager.get_watchlist()
    
    if watchlist:
        st.markdown(f"**{watchlist_manager.get_watchlist_count()}/{watchlist_manager.get_watchlist_max_size()} stocks**")
        
        for symbol in watchlist:
            col1, col2 = st.columns([4, 1])
            with col1:
                if st.button(symbol, key=f"watch_{symbol}", use_container_width=True):
                    selected_symbol = symbol
                    st.rerun()
            with col2:
                if st.button("❌", key=f"remove_{symbol}"):
                    if watchlist_manager.remove_from_watchlist(symbol):
                        ui_components.render_toast_notification(
                            f"Removed {symbol} from watchlist",
                            "info"
                        )
                        st.rerun()
    else:
        st.caption("Your watchlist is empty. Add stocks to get started!")
    
    st.markdown("---")
    
    # Auto-Refresh Section
    st.markdown("### 🔄 Auto-Refresh")
    
    # Toggle auto-refresh
    col1, col2 = st.columns(2)
    with col1:
        if st.button("ON" if not refresh_manager.is_refresh_enabled() else "✓ ON", 
                     key="refresh_on", 
                     disabled=refresh_manager.is_refresh_enabled(),
                     use_container_width=True):
            refresh_manager.toggle_refresh()
            st.rerun()
    with col2:
        if st.button("OFF" if refresh_manager.is_refresh_enabled() else "✓ OFF", 
                     key="refresh_off",
                     disabled=not refresh_manager.is_refresh_enabled(),
                     use_container_width=True):
            refresh_manager.toggle_refresh()
            st.rerun()
    
    # Interval selector
    current_interval = refresh_manager.get_refresh_interval()
    interval_options = {
        "30 seconds": 30,
        "60 seconds": 60,
        "2 minutes": 120
    }
    
    selected_refresh_interval = st.selectbox(
        "Refresh Interval",
        options=list(interval_options.keys()),
        index=list(interval_options.values()).index(current_interval) if current_interval in interval_options.values() else 1,
        key="refresh_interval_select"
    )
    
    if interval_options[selected_refresh_interval] != current_interval:
        refresh_manager.set_refresh_interval(interval_options[selected_refresh_interval])
    
    # Display countdown and status
    if refresh_manager.is_refresh_enabled():
        countdown = refresh_manager.get_countdown()
        st.metric("Next refresh in", f"{countdown}s")
        
        # Manual refresh button
        if st.button("🔄 Refresh Now", key="manual_refresh", use_container_width=True):
            refresh_manager.mark_refreshed()
            st.rerun()
        
        # Show last refresh time
        time_since = refresh_manager.get_time_since_refresh()
        st.caption(f"Last refreshed: {time_since}s ago")
        
        # Auto-refresh logic
        if refresh_manager.should_refresh():
            refresh_manager.mark_refreshed()
            st.rerun()
    else:
        st.info("Auto-refresh is disabled")
    
    st.markdown("---")
    
    # Keyboard Shortcuts Help
    with st.expander("⌨️ Keyboard Shortcuts"):
        ui_components.render_keyboard_shortcuts_legend()
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("This dashboard provides real-time stock market analytics powered by Alpha Vantage API.")
    st.caption("⚠️ **For educational purposes only. Not financial advice.**")

# Create cache key
cache_key = f"{selected_symbol}_{selected_interval}"

# Main content
try:
    # Check if data is cached
    if cache_key not in st.session_state.cached_data:
        with st.spinner(f"Loading data for {selected_symbol}..."):
            # Fetch data from API (returns tuple: response, is_demo)
            response, is_demo = api_service.fetch_intraday_data(selected_symbol, selected_interval)
            df = api_service.parse_time_series(response, selected_symbol, selected_interval)
            
            if df.empty:
                st.error("No data available for the selected stock and interval.")
                st.stop()
            
            # Cache the data and demo flag
            st.session_state.cached_data[cache_key] = df
            st.session_state[f"{cache_key}_is_demo"] = is_demo
    else:
        df = st.session_state.cached_data[cache_key]
        is_demo = st.session_state.get(f"{cache_key}_is_demo", False)
    
    # Show demo data warning if applicable
    if is_demo:
        st.warning(f"""
        ⚠️ **Using Demo Data for {selected_symbol}**
        
        The Alpha Vantage API is currently unavailable (rate limit, invalid key, or connection issue).
        Displaying simulated data for demonstration purposes.
        
        **This is not real market data!**
        """)
    
    
    # Calculate metrics
    metrics = data_processor.calculate_metrics(df)
    trends = data_processor.calculate_trends(df)
    
    # Price change detection and highlighting
    current_price = metrics.get('current_price', 0)
    previous_price = st.session_state.previous_price.get(selected_symbol, current_price)
    
    # Display price change indicator if price changed
    if current_price != previous_price:
        ui_components.render_price_change_indicator(current_price, previous_price)
        st.session_state.previous_price[selected_symbol] = current_price
    
    # Display metrics in columns
    st.markdown("### Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        delta_str = f"{metrics['price_change']:+.2f}" if metrics.get('price_change') else None
        ui_components.render_metric_card(
            "Current Price",
            f"${metrics.get('current_price', 0):.2f}",
            delta_str
        )
    
    with col2:
        percent_str = f"{metrics.get('price_change_percent', 0):+.2f}%"
        ui_components.render_metric_card(
            "Change %",
            percent_str,
            None
        )
    
    with col3:
        ui_components.render_metric_card(
            "High",
            f"${metrics.get('high', 0):.2f}",
            None
        )
    
    with col4:
        ui_components.render_metric_card(
            "Low",
            f"${metrics.get('low', 0):.2f}",
            None
        )
    
    # Additional metrics
    st.markdown("### Additional Insights")
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        st.metric("Total Volume", f"{metrics.get('total_volume', 0):,}")
    
    with col6:
        st.metric("Avg Volume", f"{metrics.get('average_volume', 0):,}")
    
    with col7:
        st.metric("Trend", trends.get('trend', 'N/A'))
    
    with col8:
        st.metric("Volatility", f"${trends.get('volatility', 0):.2f}")
    
    st.markdown("---")
    
    # Technical Indicators Section
    st.markdown("### 📊 Technical Indicators")
    
    # Calculate all technical indicators
    current_price = metrics.get('current_price', 0)
    indicators = technical_indicators.calculate_all_indicators(df, current_price)
    
    # Display indicators in columns
    col_ind1, col_ind2, col_ind3, col_ind4 = st.columns(4)
    
    with col_ind1:
        rsi_value = indicators.get('rsi', 0)
        rsi_signal = indicators.get('rsi_signal', 'N/A')
        rsi_color = "🟢" if rsi_signal == "Oversold" else "🔴" if rsi_signal == "Overbought" else "🟡"
        st.metric("RSI (14)", f"{rsi_value:.2f}", f"{rsi_color} {rsi_signal}")
    
    with col_ind2:
        macd_value = indicators.get('macd', 0)
        macd_signal = indicators.get('macd_signal', 0)
        macd_trend = "Bullish" if macd_value > macd_signal else "Bearish"
        macd_color = "🟢" if macd_value > macd_signal else "🔴"
        st.metric("MACD", f"{macd_value:.4f}", f"{macd_color} {macd_trend}")
    
    with col_ind3:
        bb_upper = indicators.get('bb_upper', 0)
        bb_lower = indicators.get('bb_lower', 0)
        bb_position = "Upper" if current_price >= bb_upper else "Lower" if current_price <= bb_lower else "Middle"
        st.metric("Bollinger Bands", bb_position, f"${bb_lower:.2f} - ${bb_upper:.2f}")
    
    with col_ind4:
        ma_20 = indicators.get('ma_20', 0)
        ma_trend = "Above" if current_price > ma_20 else "Below"
        ma_color = "🟢" if current_price > ma_20 else "🔴"
        st.metric("MA(20)", f"${ma_20:.2f}", f"{ma_color} {ma_trend}")
    
    # Overall Signal
    overall_signal = indicators.get('overall_signal', 'HOLD')
    signal_confidence = indicators.get('signal_confidence', 5)
    signal_reasoning = indicators.get('signal_reasoning', 'Mixed signals')
    
    signal_color = {
        'BUY': 'success',
        'SELL': 'error',
        'HOLD': 'warning'
    }.get(overall_signal, 'info')
    
    signal_emoji = {
        'BUY': '🟢',
        'SELL': '🔴',
        'HOLD': '🟡'
    }.get(overall_signal, '⚪')
    
    st.markdown(f"""
    <div style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px; margin: 20px 0;">
        <h3 style="margin: 0;">{signal_emoji} Overall Signal: {overall_signal}</h3>
        <p style="margin: 10px 0 0 0;">Confidence: {signal_confidence}/10 | {signal_reasoning}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Moving Averages Summary
    with st.expander("📈 Moving Averages Details"):
        ma_col1, ma_col2, ma_col3, ma_col4 = st.columns(4)
        with ma_col1:
            st.metric("MA(5)", f"${indicators.get('ma_5', 0):.2f}")
        with ma_col2:
            st.metric("MA(20)", f"${indicators.get('ma_20', 0):.2f}")
        with ma_col3:
            st.metric("MA(50)", f"${indicators.get('ma_50', 0):.2f}")
        with ma_col4:
            st.metric("MA(200)", f"${indicators.get('ma_200', 0):.2f}")
    
    st.markdown("---")
    
    # Charts section
    st.markdown("### Price Analysis")
    
    # Candlestick chart (full width)
    candlestick_fig = charts.create_candlestick_chart(df)
    st.plotly_chart(candlestick_fig, use_container_width=True)
    
    # Price trend chart (full width)
    price_fig = charts.create_price_chart(df)
    st.plotly_chart(price_fig, use_container_width=True)
    
    # Price with Bollinger Bands
    bb_data = technical_indicators.calculate_bollinger_bands(df)
    bb_fig = charts.create_price_chart_with_bb(df, bb_data)
    st.plotly_chart(bb_fig, use_container_width=True)
    
    # Price with Moving Averages
    ma_data = technical_indicators.calculate_moving_averages(df)
    ma_fig = charts.create_price_chart_with_ma(df, ma_data)
    st.plotly_chart(ma_fig, use_container_width=True)
    
    st.markdown("### Technical Indicator Charts")
    
    # RSI and MACD charts (side by side)
    col_ind_chart1, col_ind_chart2 = st.columns(2)
    
    with col_ind_chart1:
        rsi_series = technical_indicators.calculate_rsi(df)
        rsi_fig = charts.create_rsi_chart(df, rsi_series)
        st.plotly_chart(rsi_fig, use_container_width=True)
    
    with col_ind_chart2:
        macd_data = technical_indicators.calculate_macd(df)
        macd_fig = charts.create_macd_chart(df, macd_data)
        st.plotly_chart(macd_fig, use_container_width=True)
    
    st.markdown("### Volume & Distribution")
    
    # Volume and Pie charts (side by side)
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        volume_fig = charts.create_volume_chart(df)
        st.plotly_chart(volume_fig, use_container_width=True)
    
    with col_chart2:
        pie_data = data_processor.prepare_chart_data(df, 'pie')
        pie_fig = charts.create_pie_chart(pie_data)
        st.plotly_chart(pie_fig, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown(f"*Last updated: {metrics.get('last_updated', 'N/A')}*")
    st.markdown("*Data provided by Alpha Vantage*")

except ValueError as e:
    st.error(f"Error: {str(e)}")
    st.info("Please check your settings and try again.")
except Exception as e:
    st.error(f"An unexpected error occurred: {str(e)}")
    st.info("Please refresh the page or contact support if the issue persists.")
