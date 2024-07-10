from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

import datetime as dt
import pandas as pd
import os

import sqlite3
import yfinance as yf

tickers = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA',     
    'DIS', 'JPM', 'WMT', 'KO',             
    'VIC', 'VHM', 'VNM',                   # Các mã chứng khoán trên sàn Ho Chi Minh Stock Exchange (HOSE)
    'GAS', 'BVH', 'TBC',                   # Các mã chứng khoán trên sàn Hanoi Stock Exchange (HNX)
]

def _crawl_data():
    for ticker in tickers:
        data = yf.download(ticker)
        data = data.sort_index(ascending=False)
       
        data.to_csv(ticker + '.csv')
    print('Successfully.')
    return True

def _clean_data():
    for ticker in tickers:
        data = pd.read_csv(ticker + '.csv')
        h, _ = data.shape
        ls = []
        ls_rate = []
        for i in range(h):
            if i == (h - 1):
                ls.append(0)
                ls_rate.append(0)
                break
            ls.append(round(data.iloc[i][4] - data.iloc[i + 1][4], 2))
            ls_rate.append(str(round(ls[i] / data.iloc[i + 1][4] * 100, 2)) + '%')

        data = data.assign(Changed=ls)
        data = data.assign(Changed_rate=ls_rate)
        data.to_csv(ticker + '.csv')
    print('Successfully.')
    return True

def insert_to_sqlite():
    conn = sqlite3.connect('/opt/airflow/share_data/database.db')
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS StockData (
            ID TEXT,
            Date DATE,
            Open REAL,
            High REAL,
            Low REAL,
            Close REAL,
            Adj_Close REAL,
            Volume INTEGER,
            Changed REAL,
            Changed_rate TEXT
        );
    """)

    for ticker in tickers:
        data = pd.read_csv(ticker + '.csv')
        
        for _, row in data.iterrows():
            date = pd.to_datetime(row['Date']).date()
            cursor.execute("""
                INSERT INTO StockData (ID, Date, Open, High, Low, Close, Adj_Close, Volume, Changed, Changed_rate)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (ticker, date, round(row['Open'], 2), round(row['High'], 2), 
                  round(row['Low'], 2), round(row['Close'], 2), round(row['Adj Close'], 2), 
                  round(row['Volume'], 2), row['Changed'], row['Changed_rate']))

    print('Successfully.')
    conn.commit()
    conn.close()

def get_data_from_sqlite3():
    conn = sqlite3.connect('/opt/airflow/share_data/database.db')
    start_date = '2024-04-01'
    end_date = '2024-04-30'

    query = f"SELECT * FROM StockData WHERE date >= '{start_date}' AND date <= '{end_date}' AND ID = '{'AAPL'}'"

    df = pd.read_sql_query(query, conn)
    print(df)
    conn.close()
    print('Successfully.')

default_args = {
    "owner": "HA",
    'email': ['ha20040204@gmail.com'],
    'email_on_failure': True,
    "start_date": dt.datetime.now() - dt.timedelta(minutes=2),
    "retries": 1,
    "retry_delay": dt.timedelta(minutes=1),
}

with DAG("Final",
    default_args=default_args,
    tags=['Test'],
    schedule_interval ='0 8 * * *' # '@once' '0 8 * * *'
) as dag:

    starting = BashOperator(task_id = 'starting', bash_command = 'echo "Chuẩn bị cào dữ liệu"')

    create_file= BashOperator(task_id='create_file_task', bash_command='touch /opt/airflow/share_data/database.db',)
    
    crawl_data = PythonOperator(task_id = 'craw_data', python_callable = _crawl_data)

    clean_data = PythonOperator(task_id = 'clean_data', python_callable = _clean_data)

    insert_db = PythonOperator(task_id = 'insert_db', python_callable = insert_to_sqlite)

    get_data = PythonOperator(task_id = 'get_data', python_callable = get_data_from_sqlite3)

    ending = BashOperator(task_id = 'ending', bash_command = 'echo "Completed"')


starting >> create_file >> crawl_data >> clean_data >> insert_db >> get_data >> ending