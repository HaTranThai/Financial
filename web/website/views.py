from flask import Blueprint, render_template
from flask_login import current_user
import sqlite3
import pandas as pd
import os
import json
from datetime import datetime
import yfinance as yf

views = Blueprint('views', __name__)

# Đường dẫn đến volume mydata
DATABASE_PATH = '/opt/airflow/share_data/database.db'

@views.route('/')
def home():
    conn = sqlite3.connect(DATABASE_PATH)
    ids = pd.read_sql_query("SELECT DISTINCT ID FROM StockData", conn)
    query = "SELECT ID, Close, Changed, Changed_rate FROM StockData"
    data = pd.read_sql_query(query, conn)
    data = data.drop_duplicates(subset=['ID'])
    conn.close()
    
    conv_db_to_json(data['ID'].values)

    return render_template('home.html', 
                           user=current_user,
                           data=data,
                           ids=ids
                           )

@views.route('/news')
def news():
    tickers = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA',     
        'DIS', 'JPM', 'WMT', 'KO',             
        'VIC', 'VHM', 'VNM',                   # Các mã chứng khoán trên sàn Ho Chi Minh Stock Exchange (HOSE)
        'GAS', 'BVH', 'TBC',                   # Các mã chứng khoán trên sàn Hanoi Stock Exchange (HNX)
    ]

    items = []
    today = datetime.today().strftime('%Y-%m-%d')

    for ticker in tickers:
        news = yf.Ticker(ticker).get_news()
        for new in news:
            title = new['title']
            publisher = new['publisher']
            link = new['link']
            time = datetime.utcfromtimestamp(new['providerPublishTime']).strftime('%Y-%m-%d')
            related_tickers = []
            img_url = ""
                
            if 'relatedTickers' in new:
                related_tickers = new['relatedTickers']
            
            if 'thumbnail' in new:
                img_url = new['thumbnail']['resolutions'][-1]['url']
            
            item = [title, link, publisher, time, img_url, related_tickers]
            if item not in items and time == today:
                items.append(item)

    return render_template('news.html', user=current_user, items=items)

def conv_db_to_json(ids):
    conn = sqlite3.connect(DATABASE_PATH)
    query = "SELECT *, Adj_Close * Volume AS volume_dollar FROM StockData;"
    df = pd.read_sql_query(query, conn)
    for id in ids:
        df_stock = df[df['ID'] == id]
        df_stock = df_stock[pd.to_datetime(df_stock['Date']).dt.year >= 2012]
        df_stock.columns = [i.lower() for i in df_stock.columns] 
        json_data = df_stock.to_dict(orient='records')
        output_dir = 'website/static'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        output_path = os.path.join(output_dir, f'{id}.json')
        with open(output_path, 'w') as file:
            json.dump(json_data, file, indent=2)
    conn.close()
