import yfinance as yf
from datetime import datetime
import logging

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Read stocks file
def read_stocks():
    with open('./src/telegram/stocks.txt', 'r') as f:
        stocks = []
        for line in f:
            line = line.strip()
            if line == '':
                break
            # Split by comma
            data = line.split(',')
            # stock = [0].strip()
            stocks.append({
                'stock': data[0],
                'buy_price': float(data[1]),
                'qty': int(data[2]),
            })
    return stocks

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
    # yest_price = data['Close'].iloc[-2]     # yest's price

    lastXdayPrice =  data['Close'].iloc[0]     # price before 7 / 15 d etc.


    # calc for buy price to today    
    change = (current_price - buy_price) * qty
    perc_change = change / buy_price * 100


    # calc for last x'th day to today    
    recent_chng = (current_price - lastXdayPrice)
    recent_perc_chng = recent_chng / lastXdayPrice * 100
    
    # print(f"Stock: {ticker}")
    # print(f"Current Price: ₹{current_price:.2f}")
    # print(f"Open Price: ₹{lastXdayPrice:.2f}")
    # print(f"Change: {change:.2f} ({perc_change:.2f}%)")
    logging.info(f"Got data for {ticker}")

    # return f"""**{ticker}: {buy_price} , Qty: {qty}** : 
    # ({lastXdayPrice:.2f} to {current_price:.2f}) {change:.2f} ({perc_change:.2f}%)
    # (Since yest: {yest_price:.2f} to {current_price:.2f}) {recent_chng:.2f} ({recent_perc_chng:.2f}%)"""

    return f"""**{ticker}: {buy_price} , Qty: {qty} {"CHECK !!!" if perc_change < 0 or recent_perc_chng < 0 else ""}**:    
 Total Change: {buy_price:.2f} to {current_price:.2f} {change:.2f} ({perc_change:.2f}%)
 Since {period}: {lastXdayPrice:.2f} to {current_price:.2f} {recent_chng:.2f} ({recent_perc_chng:.2f}%)"""
    

def process(period):
    stocks = read_stocks()

    resp = ""
    # for s in stocks:
    #     resp = resp + get_stock_performance(s, period=period) + "\n\r" + "\n\r"
    for stock in stocks:
        resp = resp + get_stock_performance(stock, period=period) + "\n\r" + "\n\r"

    return resp