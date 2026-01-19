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
            stocks.append(line)
            
    return(stocks)

def_time = '7d'

def get_stock_performance(ticker, period=def_time):
    stock = yf.Ticker(ticker)
    data = stock.history(period=period)
    
    if data.empty:
        logging.info(f"No data found for {ticker}")
        return (f"No data found for {ticker}")
                
    current_price = data['Close'].iloc[-1]  # today's price
    yest_price = data['Close'].iloc[-2]     # yest's price

    oldest_price =  data['Close'].iloc[0]     # price before 7 / 15 d etc.


    # calc for 15d to today    
    change = (current_price - oldest_price)
    perc_change = change / oldest_price * 100


    lastchange = (current_price - yest_price)
    last_perc_change = lastchange / yest_price * 100
    
    # print(f"Stock: {ticker}")
    # print(f"Current Price: ₹{current_price:.2f}")
    # print(f"Open Price: ₹{oldest_price:.2f}")
    # print(f"Change: {change:.2f} ({perc_change:.2f}%)")
    logging.info(f"Got data for {ticker}")

    # return(f"**{ticker}** : \n\r({oldest_price:.2f} to {current_price:.2f}) {change:.2f} ({perc_change:.2f}%)")

    return f"""**{ticker}** : 
    ({oldest_price:.2f} to {current_price:.2f}) {change:.2f} ({perc_change:.2f}%)
    (Since yest: {yest_price:.2f} to {current_price:.2f}) {lastchange:.2f} ({last_perc_change:.2f}%)"""
    

def process(period):
    stocks = read_stocks()

    resp = ""
    for s in stocks:
        resp = resp + get_stock_performance(s, period=period) + "\n\r" + "\n\r"

    return resp