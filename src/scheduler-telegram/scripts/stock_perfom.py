import yfinance as yf
from datetime import datetime
import logging
import requests
import random

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def read_reomte(url):
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.text
    except requests.exceptions.RequestException as e:
        logging.error(f"Error: {e}")
        return None

# Read stocks file
def read_stocks():
    file_url = "https://raw.githubusercontent.com/aksh-github/py-utils/refs/heads/master/src/scheduler-telegram/stocks.txt?t=" + str(random.randint(1, 1000))
    content = read_reomte(file_url)
    
    if content is None:
        logging.error("Failed to load stocks data. Exiting.")
        exit(1)
    stocks = []
    for line in content.splitlines():
        line = line.strip()
        if line == '':
            continue
        # Split by comma
        data = line.split(',')
        stocks.append({
            'stock': data[0],
            'buy_price': float(data[1]) if len(data) > 1 else 0.0,
            'qty': int(data[2]) if len(data) > 2 else 0,
        })
    return stocks
    # with open('./src/telegram/stocks.txt', 'r') as f:
    #     stocks = []
    #     for line in f:
    #         line = line.strip()
    #         if line == '':
    #             break
    #         # Split by comma
    #         data = line.split(',')
    #         # stock = [0].strip()
    #         stocks.append({
    #             'stock': data[0],
    #             'buy_price': float(data[1]),
    #             'qty': int(data[2]),
    #         })
    # return stocks

def_time = '7d'

def get_stock_performance(stockObj, period=def_time):
    ticker = stockObj["stock"]
    buy_price = stockObj["buy_price"]
    qty = stockObj["qty"]

    stock = yf.Ticker(ticker)
    data = stock.history(period=period)
    
    if data.empty:
        logging.info(f"No data found for {ticker}")
        return (f"No data found for {ticker}")
                
    current_price = data['Close'].iloc[-1]  # today's price
    yest_price = data['Close'].iloc[-2]     # yest's price
    one_month_perc_change = three_month_perc_change = six_month_perc_change = 0.0

    if period == '1y' and len(data) >= 126:
        six_month_price = data['Close'].iloc[-126]     # price before 6 month
        six_month_perc_change = ((current_price - six_month_price) / six_month_price) * 100
        three_month_price = data['Close'].iloc[-63]     # price before 3 month
        three_month_perc_change = ((current_price - three_month_price) / three_month_price) * 100
        one_month_price = data['Close'].iloc[-21]     # price before 1 month
        one_month_perc_change = ((current_price - one_month_price) / one_month_price) * 100

    # Yesterday's change
    today_change = current_price - yest_price
    today_perc_change = ((current_price - yest_price) / yest_price) * 100

    lastXdayPrice =  data['Close'].iloc[0]     # price before 7 / 15 d etc.


    # calc for buy price to today    
    change = (current_price - buy_price) * qty
    perc_change = ((current_price - buy_price) / buy_price) * 100


    # calc for last x'th day to today    
    recent_chng = (current_price - lastXdayPrice)
    recent_perc_chng = ((current_price - lastXdayPrice) / lastXdayPrice) * 100
    
    # print(f"Stock: {ticker}")
    # print(f"Current Price: ₹{current_price:.2f}")
    # print(f"Open Price: ₹{lastXdayPrice:.2f}")
    # print(f"Change: {change:.2f} ({perc_change:.2f}%)")
    logging.info(f"Got data for {ticker}")

    # return f"""**{ticker}: {buy_price} , Qty: {qty}** : 
    # ({lastXdayPrice:.2f} to {current_price:.2f}) {change:.2f} ({perc_change:.2f}%)
    # (Since yest: {yest_price:.2f} to {current_price:.2f}) {recent_chng:.2f} ({recent_perc_chng:.2f}%)"""

    return f"""**{ticker}: {buy_price} , Qty: {qty} {"⚠️" if perc_change < 0 or recent_perc_chng < 0 else ""}**:    
 **Current Price: {current_price:.2f}**
 **Since Yesterday: {yest_price:.2f} to {current_price:.2f} {today_change:.2f} ({today_perc_change:.2f}%)**
 **Total Change: {change:.2f} ({perc_change:.2f}%)**
 1 Mon: {one_month_perc_change:.2f}% (Exp: {recent_perc_chng/12:.2f}%)
 3 Mon: {three_month_perc_change:.2f}% (Exp: {recent_perc_chng/4:.2f}%)
 6 Mon: {six_month_perc_change:.2f}% (Exp: {recent_perc_chng/2:.2f}%)
 Since {period}: {lastXdayPrice:.2f} to {current_price:.2f} {recent_chng:.2f} ({recent_perc_chng:.2f}%)"""

def check_stock_performance(stockObj, period=def_time):
    ticker = stockObj["stock"]
    buy_price = stockObj["buy_price"]
    qty = stockObj["qty"]

    stock = yf.Ticker(ticker)
    data = stock.history(period=period)
    
    if data.empty:
        logging.info(f"No data found for {ticker}")
        return ""

    current_price = data['Close'].iloc[-1]
    if buy_price <= 0:
        logging.info(f"Invalid buy price for {ticker}")
        return ""

    loss = (buy_price - current_price) * qty
    loss_perc = ((buy_price - current_price) / buy_price) * 100

    # Highlight only when loss is greater than 500 or greater than 5%
    if loss <= 500 and loss_perc <= 5:
        return ""

    logging.info(f"Got data for {ticker}")
    return f"**{ticker}: {buy_price} , Qty: {qty}**: Loss ⚠️: {loss:.2f} ({loss_perc:.2f}%)"
    

def process(period, msg):

    logging.info(f'got msg: {msg}')

    stocks = read_stocks()
    result = ""
    
    # only when stocks are falling
    if msg == "perf-check":
        for stock in stocks:
            res = check_stock_performance(stock, period=period)
            if res:
                res = res + "\n\r"
            result = result + res

    # usual everyday update
    else:
        for stock in stocks:
            result = result + get_stock_performance(stock, period=period) + "\n\r" + "\n\r"

    return result
