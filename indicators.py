import pandas as pd
import ta

def compute_indicators(df):
    """حساب المؤشرات الفنية"""
    try:
        close = df['close'].astype(float)
        
        # RSI
        rsi = ta.momentum.RSIIndicator(close, window=14).rsi()
        
        # MACD
        macd_indicator = ta.trend.MACD(close)
        macd = macd_indicator.macd()
        macd_signal = macd_indicator.macd_signal()
        macd_diff = macd_indicator.macd_diff()
        
        # Bollinger Bands
        bb = ta.volatility.BollingerBands(close, window=20, window_dev=2)
        bb_upper = bb.bollinger_hband()
        bb_lower = bb.bollinger_lband()
        
        # EMA
        ema_fast = ta.trend.EMAIndicator(close, window=12).ema_indicator()
        ema_slow = ta.trend.EMAIndicator(close, window=26).ema_indicator()
        
        return {
            'rsi': rsi,
            'macd': macd,
            'macd_signal': macd_signal,
            'macd_diff': macd_diff,
            'bb_upper': bb_upper,
            'bb_lower': bb_lower,
            'ema_fast': ema_fast,
            'ema_slow': ema_slow
        }
    except Exception as e:
        print(f"Indicators calculation error: {e}")
        return None
