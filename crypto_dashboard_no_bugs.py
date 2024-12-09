
import requests
import pandas as pd
from ta.trend import SMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands
import streamlit as st

# تنظیمات API
BASE_URL = "https://api.coingecko.com/api/v3/coins/markets"
VS_CURRENCY = "usd"  # ارز مرجع
THRESHOLD = 5  # درصد رشد برای تحلیل اولیه
MIN_VOLUME = 1000000  # حداقل حجم معاملات

# گرفتن داده‌های بازار از CoinGecko
def fetch_market_data():
    params = {
        "vs_currency": VS_CURRENCY,
        "order": "market_cap_desc",
        "per_page": 100,  # تعداد ارزها
        "page": 1,
        "sparkline": "false",
    }
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"خطا در دریافت داده‌ها: {e}")
        return []

# تحلیل تکنیکال پیشرفته
def advanced_analysis(data):
    results = []
    for coin in data:
        try:
            current_price = coin['current_price']
            price_change_24h = coin.get('price_change_percentage_24h', 0)
            volume = coin['total_volume']

            # فیلتر ارزها بر اساس تغییر قیمت و حجم معاملات
            if price_change_24h > THRESHOLD and volume > MIN_VOLUME:
                # محاسبه اندیکاتورهای تکنیکال
                price_data = pd.Series([coin['high_24h'], coin['low_24h'], current_price])
                sma = SMAIndicator(price_data, window=2).sma_indicator().iloc[-1]
                rsi = RSIIndicator(price_data, window=2).rsi().iloc[-1]
                macd = MACD(price_data).macd().iloc[-1]
                bb = BollingerBands(price_data).bollinger_mavg().iloc[-1]

                results.append({
                    "Name": coin['name'],
                    "Symbol": coin['symbol'],
                    "Price (USD)": current_price,
                    "24h Change (%)": round(price_change_24h, 2),
                    "Volume": volume,
                    "SMA": round(sma, 2),
                    "RSI": round(rsi, 2),
                    "MACD": round(macd, 2),
                    "Bollinger Avg": round(bb, 2),
                })
        except Exception:
            continue
    return results

# نمایش داشبورد
def display_dashboard(data):
    st.title("تحلیل ارزهای دیجیتال با پتانسیل رشد")
    if not data:
        st.warning("داده‌ای برای نمایش وجود ندارد.")
    else:
        df = pd.DataFrame(data)
        st.dataframe(df)

# اجرای برنامه
if __name__ == "__main__":
    st.sidebar.title("تنظیمات")
    threshold = st.sidebar.slider("حداقل درصد رشد:", 1, 20, THRESHOLD)
    volume_limit = st.sidebar.number_input("حداقل حجم معاملات:", value=MIN_VOLUME, step=100000)

    st.sidebar.write("در حال بارگذاری داده‌ها...")
    raw_data = fetch_market_data()
    if raw_data:
        analyzed_data = advanced_analysis(raw_data)
        display_dashboard(analyzed_data)
    else:
        st.error("نتوانستیم داده‌ها را از CoinGecko دریافت کنیم.")
