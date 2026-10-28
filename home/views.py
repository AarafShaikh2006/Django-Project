import requests
from datetime import datetime, timedelta, date
from urllib.parse import urlparse
from .models import IPO
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.shortcuts import render
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout


import json
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import yfinance as yf
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from django.views.decorators.http import require_http_methods
from home.models import Contact, Portfolio
from .forms import PortfolioForm

import yfinance as yf

# -----------------------------
# API Key (Alpha Vantage)
# -----------------------------
API_KEY = "ca2a060104ca435ca185c72a6c63f439"
def normalize_symbol(symbol):
    symbol = symbol.upper().strip()

    # BSE
    if symbol.endswith(".BSE") or symbol.endswith(".BO"):
        base = symbol.split('.')[0]
        symbol = f"{base}.BO"  # YFinance uses .BO
    # NSE
    elif symbol.endswith(".NS"):
        base = symbol.split('.')[0]
        symbol = f"{base}.NS"
    return symbol
# -----------------------------
# -----------------------------
# Get real-time price
# -----------------------------
def get_realtime_price(symbol):
    symbol = normalize_symbol(symbol)

    # Try Alpha Vantage first
    try:
        url = "https://www.alphavantage.co/query"
        params = {"function": "GLOBAL_QUOTE", "symbol": symbol, "apikey": API_KEY}
        res = requests.get(url, params=params, timeout=8)
        res.raise_for_status()
        data = res.json()
        quote = data.get("Global Quote", {})
        price = quote.get("05. price")
        if price:
            return float(price)
    except Exception as e:
        print(f"Alpha Vantage failed for {symbol}: {e}")

    # Fallback: YFinance
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        price = info.get("regularMarketPrice")
        if price:
            return float(price)
    except Exception as e:
        print(f"YFinance failed for {symbol}: {e}")

    return None

# -----------------------------
# Static Pages
# -----------------------------
def index(request): 
    return render(request, "index.html")

def about(request): 
    return render(request, "about.html")

def services(request): 
    return render(request, "services.html")

from django.contrib import messages
from django.shortcuts import render, redirect
from .models import Contact

def contact(request):
    if request.method == "POST":
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        desc = request.POST.get('desc', '').strip()

        if not name or not email or not phone or not desc:
            messages.error(request, "Please fill in all fields.", extra_tags='contact')
            return redirect('contact')

        # Save contact to database
        contact_entry = Contact(name=name, email=email, phone=phone, desc=desc)
        contact_entry.save()

        # Success message
        messages.success(request, "Thank you! Your message has been sent successfully.", extra_tags='contact')
        return redirect('contact')

    return render(request, 'contact.html')
# News Page complete

def news(request):
    articles = []
    message = None

    # 1️⃣ Collect user's US stock tickers from Portfolio
    tickers = []
    if request.user.is_authenticated:
        try:
            user_stocks = Portfolio.objects.filter(user=request.user)
            for stock in user_stocks:
                # Only include non-Indian symbols (US stocks)
                if not (stock.stock_symbol.endswith(".NS") or stock.stock_symbol.endswith(".BO")):
                    tickers.append(stock.stock_symbol)
        except Exception as e:
            # Note: This print is for debugging; consider using Django logging
            print("Error reading portfolio:", e)

    if not tickers:
        tickers = ["AAPL", "TSLA", "MSFT"]

    # 2️⃣ Fetch news from Alpha Vantage
    try:
        url = "https://www.alphavantage.co/query"
        params = {"function": "NEWS_SENTIMENT", "tickers": ",".join(tickers), "apikey": API_KEY}
        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if "feed" in data and data["feed"]:
            for item in data["feed"]:
                url_src = item.get("url", "")
                domain = urlparse(url_src).netloc if url_src else ""
                favicon = f"https://www.google.com/s2/favicons?sz=128&domain={domain}"
                source = item.get("source", "")

                # 🚫 CRITICAL FIX: Skip the entire article if the source is Benzinga
                if "benzinga" in source.lower():
                    continue 

                # Format published time
                try:
                    time_published = datetime.strptime(
                        item.get("time_published", "20250101T000000"), "%Y%m%dT%H%M%S"
                    ).strftime("%Y-%m-%d %H:%M:%S")
                except:
                    time_published = ""

                # ✅ Filter out placeholder images from other sources
                image_url = item.get("banner_image", "")
                if image_url:
                    bad_keywords = ["logo", "placeholder", "default", "icon"]
                    if any(k in image_url.lower() for k in bad_keywords):
                        image_url = ""
                        
                if not image_url:
                    image_url = favicon  # fallback to favicon if no real image

                # Add article to list
                articles.append({
                    "title": item.get("title"),
                    "url": url_src,
                    "summary": item.get("summary", ""),
                    "source": source or "Alpha Vantage",
                    "favicon": favicon,
                    "time_published": time_published,
                    "image_url": image_url,
                })

        elif "Note" in data:
            message = "Alpha Vantage API limit reached. Using fallback news."
        elif "Error Message" in data:
            message = data["Error Message"]

    except Exception as e:
        print("Error fetching Alpha Vantage news:", e)

    # 3️⃣ Yahoo Finance fallback
    if not articles:
        try:
            fallback_tickers = ["AAPL", "TSLA", "^NSEI"]
            unique_urls = set()

            for symbol in fallback_tickers:
                try:
                    # Note: yf.Ticker() needs to be handled carefully as it's external
                    ticker = yf.Ticker(symbol)
                    # getattr/callable check for compatibility across yfinance versions
                    news_data = getattr(ticker, "news", [])
                    if callable(news_data):
                        news_data = news_data()
                except:
                    news_data = []

                for item in news_data:
                    url_src = item.get("link")
                    if not url_src or url_src in unique_urls:
                        continue

                    # Extract thumbnail if available
                    thumbnail = ""
                    if "thumbnail" in item and isinstance(item["thumbnail"], dict):
                        # Attempt to get the first resolution URL
                        thumbnail = item["thumbnail"].get("resolutions", [{}])[0].get("url", "")
                    elif "providerThumbnail" in item:
                        thumbnail = item["providerThumbnail"].get("url", "")

                    # Construct necessary fallback data
                    link_domain = urlparse(url_src).netloc
                    
                    # Add to article list
                    articles.append({
                        "title": item.get("title"),
                        "url": url_src,
                        "summary": item.get("summary", ""),
                        "source": item.get("publisher", "Yahoo Finance"),
                        "favicon": f"https://www.google.com/s2/favicons?sz=128&domain={link_domain}",
                        "time_published": datetime.fromtimestamp(
                            item.get("providerPublishTime", datetime.now().timestamp())
                        ).strftime("%Y-%m-%d %H:%M:%S"),
                        "image_url": thumbnail or f"https://www.google.com/s2/favicons?sz=128&domain={link_domain}",
                    })
                    unique_urls.add(url_src)

        except Exception as e:
            print("Error fetching Yahoo Finance news:", e)

    # 4️⃣ Final fallback message
    if not articles and not message:
        message = "No news available at the moment."

    return render(request, "news.html", {"articles": articles, "message": message})
# Authentication
# -----------------------------
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                return redirect('portfolio')
        messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, "login.html", {'form': form})

@login_required
def portfolio(request):
    if request.method == "POST":
        form = PortfolioForm(request.POST)
        if form.is_valid():
            new_stock = form.save(commit=False)
            # Normalize symbol before saving
            new_stock.stock_symbol = normalize_symbol(new_stock.stock_symbol)
            new_stock.user = request.user
            new_stock.save()
            messages.success(request, f"{new_stock.stock_symbol} added to your portfolio!")
            return redirect('portfolio')
    else:
        form = PortfolioForm()

    holdings = Portfolio.objects.filter(user=request.user)
    portfolio_data = []
    total_investment = 0
    total_current_value = 0

    for stock in holdings:
        current_price = get_realtime_price(stock.stock_symbol)
        effective_price = current_price if current_price is not None else stock.buy_price
        investment = stock.quantity * stock.buy_price
        current_value = stock.quantity * effective_price
        profit_loss = current_value - investment

        portfolio_data.append({
            "symbol": stock.stock_symbol,
            "quantity": stock.quantity,
            "buy_price": stock.buy_price,
            "investment": round(investment, 2),
            "current_price": round(effective_price, 2),
            "current_value": round(current_value, 2),
            "profit_loss": round(profit_loss, 2),
            "id": stock.pk
        })

        total_investment += investment
        total_current_value += current_value

    context = {
        "form": form,
        "portfolio": portfolio_data,
        "total_stocks": holdings.count(),
        "total_investment": round(total_investment, 2),
        "total_current_value": round(total_current_value, 2),
        "total_profit_loss": round(total_current_value - total_investment, 2),
        "portfolio_history": {
            "dates": [datetime.now().strftime("%Y-%m-%d")],
            "values": [round(total_current_value, 2)]
        },
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    return render(request, "portfolio.html", context)


# -----------------------------
# AJAX: Update Portfolio Prices
# -----------------------------
@login_required
def update_prices(request):
    holdings = Portfolio.objects.filter(user=request.user)
    data = []

    for stock in holdings:
        current_price = get_realtime_price(stock.stock_symbol)
        effective_price = current_price if current_price is not None else stock.buy_price
        investment = stock.quantity * stock.buy_price
        current_value = stock.quantity * effective_price
        profit_loss = current_value - investment
        data.append({
            "id": stock.pk,
            "current_price": round(effective_price, 2),
            "current_value": round(current_value, 2),
            "profit_loss": round(profit_loss, 2),
        })

    total_current_value = sum(item["current_value"] for item in data)
    total_profit_loss = total_current_value - sum(stock.quantity * stock.buy_price for stock in holdings)

    return JsonResponse({
        "stocks": data,
        "total_current_value": round(total_current_value, 2),
        "total_profit_loss": round(total_profit_loss, 2)
    })

# Stock Suggestions Endpoint
# -----------------------------
@login_required
def symbol_search(request):
    query = request.GET.get("q", "").strip()
    results = []

    if query:
        try:
            url = "https://www.alphavantage.co/query"
            params = {"function": "SYMBOL_SEARCH", "keywords": query, "apikey": API_KEY}
            res = requests.get(url, params=params, timeout=10).json()
            matches = res.get("bestMatches", [])

            for match in matches:
                symbol = match.get("1. symbol", "")
                name = match.get("2. name", "")
                region = match.get("4. region", "")
                currency = match.get("8. currency", "")

                # Normalize Indian stocks
                if region == "India":
                    if symbol.endswith(".BSE") or symbol.endswith(".BO"):
                        symbol = symbol.split('.')[0] + ".BO"
                    elif symbol.endswith(".NS"):
                        symbol = symbol.split('.')[0] + ".NS"

                # Filter symbols starting with query
                if symbol.upper().startswith(query.upper()) or name.upper().startswith(query.upper()):
                    results.append({
                        "symbol": symbol,
                        "name": name,
                        "region": region,
                        "currency": currency
                    })

            print("Alpha Vantage matches:", results)  # Debug log

        except Exception as e:
            print("Error fetching suggestions:", e)

    return JsonResponse(results, safe=False)
# -----------------------------
# Delete Stock
# -----------------------------
@login_required
def delete_stock(request, pk):
    if request.method == "POST":
        stock = get_object_or_404(Portfolio, pk=pk, user=request.user)
        stock.delete()
        messages.success(request, f"{stock.stock_symbol} has been removed from your portfolio.")
    return redirect('portfolio')

    #---IPO DASHBOARD
from .models import IPO
from .models import IPO

def ipo_view(request):
    ongoing_ipos = IPO.objects.filter(status='open')
    upcoming_ipos = IPO.objects.filter(status='upcoming')
    listed_ipos = IPO.objects.filter(status='listed')
    return render(request, 'ipo.html', {
        'ongoing_ipos': ongoing_ipos,
        'upcoming_ipos': upcoming_ipos,
        'listed_ipos': listed_ipos,
    })

# Stock Price Prediction View
@require_http_methods(["GET", "POST"])
def predict_stock(request):

    # 1️⃣ Get stock symbol & parameters
    symbol = request.GET.get("symbol") or request.POST.get("symbol") or "RELIANCE.NS"
    period = request.GET.get("period") or request.POST.get("period") or "2y"
    lookback_days = int(request.GET.get("lookback") or request.POST.get("lookback") or 120)

    # 2️⃣ Download data
    df = yf.download(symbol, period=period, progress=False)
    if df.empty or len(df) < (lookback_days + 50):
        return render(request, "prediction.html", {"error": "Not enough data for symbol.", "symbol": symbol})

    # 3️⃣ Prepare Close price data
    data = df[['Close']].values
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled = scaler.fit_transform(data)

    # Create time windows
    X, y = [], []
    for i in range(lookback_days, len(scaled) - 1):
        X.append(scaled[i - lookback_days:i, 0])
        y.append(scaled[i, 0])
    X, y = np.array(X), np.array(y)
    X = X.reshape((X.shape[0], X.shape[1], 1))

    # Train/test split
    split_idx = int(len(X) * 0.9)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]

    # 4️⃣ Build LSTM model
    model = Sequential([
        LSTM(64, return_sequences=True, input_shape=(lookback_days, 1)),
        Dropout(0.2),
        LSTM(64),
        Dropout(0.2),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mean_squared_error')
    model.fit(X_train, y_train, epochs=30, batch_size=32, verbose=0)

    # 5️⃣ LSTM predictions
    y_pred_scaled = model.predict(X_test)
    y_pred = scaler.inverse_transform(y_pred_scaled)
    y_true = scaler.inverse_transform(y_test.reshape(-1, 1))
    mae_lstm = mean_absolute_error(y_true, y_pred)

    # 6️⃣ Random Forest fine-tuning on residuals
    X_flat = X_train.reshape((X_train.shape[0], -1))
    rf = RandomForestRegressor(n_estimators=80, random_state=42)
    rf.fit(X_flat, scaler.inverse_transform(y_train.reshape(-1, 1)).ravel())
    y_pred_rf = rf.predict(X_test.reshape((X_test.shape[0], -1)))
    mae_rf = mean_absolute_error(y_true, y_pred_rf.reshape(-1, 1))

    # 7️⃣ Hybrid prediction (average)
    hybrid_pred = (float(y_pred[-1]) + float(y_pred_rf[-1])) / 2

    # 8️⃣ Predict next day
    last_window = scaled[-lookback_days:].reshape(1, lookback_days, 1)
    next_pred_scaled = model.predict(last_window)
    next_pred_lstm = scaler.inverse_transform(next_pred_scaled)[0, 0]
    next_pred_rf = rf.predict(last_window.reshape(1, -1))[0]
    next_pred = (next_pred_lstm + next_pred_rf) / 2  # hybrid final

    # 9️⃣ Chart Data
    closes = df['Close'].astype(float).values[-60:].flatten().tolist()
    closes = [float(x) for x in closes]
    dates = df.index[-60:].strftime("%Y-%m-%d").tolist()
    next_date = (df.index[-1] + pd.Timedelta(days=1)).strftime("%Y-%m-%d")

    # 🔟 Context
    context = {
        "symbol": symbol,
        "current_price": round(float(df['Close'].iloc[-1]), 2),
        "predicted_price": round(float(next_pred), 2),
        "model_used": "Hybrid Model (LSTM + RF)",
        "model_mae": round((mae_lstm + mae_rf) / 2, 4),
        "chart_dates": json.dumps(dates + [next_date]),
        "chart_values": json.dumps([round(float(x), 2) for x in closes] + [round(float(next_pred), 2)]),
        "history": list(zip(dates, [round(float(x), 2) for x in closes])),
        "period": period,
        "lookback_days": lookback_days,
    }
    return render(request, "prediction.html", context)

# Context Processor for Current Year
# -----------------------------
def current_year(request):
    return {'current_year': datetime.now().year}