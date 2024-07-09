FROM apache/airflow:2.9.1

RUN pip install apache-airflow==${AIRFLOW_VERSION} pymongo==4.3.3
# Cài đặt thư viện yfinance
RUN pip install yfinance