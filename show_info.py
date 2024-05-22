import os
import configparser
import logging
import requests
import schedule
import time
from datetime import datetime, timedelta
from collections import defaultdict
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest
from google.oauth2 import service_account

# 读取配置文件
config = configparser.ConfigParser()
config.read('config.ini')

SCOPES = config['DEFAULT']['SCOPES'].split()
KEY_FILE_LOCATION = config['DEFAULT']['KEY_FILE_LOCATION']
PROPERTY_ID = config['DEFAULT']['PROPERTY_ID']
PAGE_SIZE = int(config['DEFAULT']['PAGE_SIZE'])
START_DATE = config['DEFAULT']['START_DATE']
END_DATE = config['DEFAULT']['END_DATE']
SITE_NAME = config['DEFAULT']['SITE_NAME']
LOG_FILE = config['DEFAULT']['LOG_FILE']
TELEGRAM_BOT_TOKEN = config['DEFAULT']['TELEGRAM_BOT_TOKEN']
TELEGRAM_CHAT_ID = config['DEFAULT']['TELEGRAM_CHAT_ID']
QUERY_TIME = config['DEFAULT']['QUERY_TIME']

# 设置日志
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')

def log_info(message):
    logging.info(message)
    print(message)

def log_error(message):
    logging.error(message)
    print(message)

def send_telegram_message(bot_token, chat_id, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        log_error(f"Failed to send message to Telegram: {e}")

def initialize_analyticsreporting():
    try:
        credentials = service_account.Credentials.from_service_account_file(KEY_FILE_LOCATION, scopes=SCOPES)
        client = BetaAnalyticsDataClient(credentials=credentials)
        return client
    except Exception as e:
        log_error(f"Failed to initialize analytics reporting: {e}")
        raise

def get_report(client, offset=0):
    try:
        request = RunReportRequest(
            property=PROPERTY_ID,
            date_ranges=[DateRange(start_date=START_DATE, end_date=END_DATE)],
            dimensions=[
                Dimension(name="country"),
                Dimension(name="browser"),
                Dimension(name="date")
            ],
            metrics=[
                Metric(name="sessions"),
                Metric(name="activeUsers"),
                Metric(name="screenPageViews"),
                Metric(name="eventCount")
            ],
            limit=PAGE_SIZE,
            offset=offset
        )
        response = client.run_report(request)
        return response
    except Exception as e:
        log_error(f"Failed to get report: {e}")
        raise

def aggregate_data(response, country_data, browser_data, totals):
    for row in response.rows:
        dimensions = row.dimension_values
        metrics = row.metric_values
        country = dimensions[0].value
        browser = dimensions[1].value
        
        # 更新国家维度数据
        country_data[country]['sessions'] += int(metrics[0].value)
        country_data[country]['activeUsers'] += int(metrics[1].value)
        country_data[country]['screenPageViews'] += int(metrics[2].value)
        country_data[country]['eventCount'] += int(metrics[3].value)

        # 更新浏览器维度数据
        browser_data[browser] += int(metrics[0].value)

        # 更新总数据
        totals['sessions'] += int(metrics[0].value)
        totals['activeUsers'] += int(metrics[1].value)
        totals['screenPageViews'] += int(metrics[2].value)
        totals['eventCount'] += int(metrics[3].value)

def print_aggregated_data(site_name, country_data, browser_data, totals):
    # Markdown 格式化的消息
    messages = []

    # 打印时间区间和站点信息
    messages.append(f"*Site:* **{site_name}**")
    messages.append(f"*Date Range:* `{START_DATE}` to `{END_DATE}`")

    # 打印国家维度数据并排序
    messages.append("\n*Country Data:*")
    sorted_country_data = sorted(country_data.items(), key=lambda item: (item[1]['sessions'] / totals['sessions']) * 100, reverse=True)
    for country, metrics in sorted_country_data:
        session_percentage = (metrics['sessions'] / totals['sessions']) * 100 if totals['sessions'] > 0 else 0
        messages.append(f"{country}, S: {metrics['sessions']} ({session_percentage:.2f}%), AU: {metrics['activeUsers']}, SPV: {metrics['screenPageViews']}, EvC: {metrics['eventCount']}")

    # 打印浏览器维度数据并排序
    messages.append("\n*Browser Data:*")
    sorted_browser_data = sorted(browser_data.items(), key=lambda item: (item[1] / totals['sessions']) * 100, reverse=True)
    for browser, sessions in sorted_browser_data:
        session_percentage = (sessions / totals['sessions']) * 100 if totals['sessions'] > 0 else 0
        messages.append(f"{browser}, S: {sessions} ({session_percentage:.2f}%)")

    # 打印总数据
    messages.append("\n*Totals:*")
    messages.append(f"Total S: {totals['sessions']}, Total AU: {totals['activeUsers']}, Total SPV: {totals['screenPageViews']}, Total EvC: {totals['eventCount']}")

    message_text = "\n".join(messages)
    send_telegram_message(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, message_text)

def main():
    client = initialize_analyticsreporting()
    offset = 0
    country_data = defaultdict(lambda: {'sessions': 0, 'activeUsers': 0, 'screenPageViews': 0, 'eventCount': 0})
    browser_data = defaultdict(int)  # 只需要记录session数
    totals = {'sessions': 0, 'activeUsers': 0, 'screenPageViews': 0, 'eventCount': 0}

    while True:
        response = get_report(client, offset)
        if not response.rows:
            break
        aggregate_data(response, country_data, browser_data, totals)
        offset += PAGE_SIZE

    print_aggregated_data(SITE_NAME, country_data, browser_data, totals)

def schedule_task():
    next_run_time = schedule.next_run() + timedelta(days=1)
    log_info(f"Next query scheduled at {next_run_time}")
    main()

def schedule_jobs():
    schedule.every().day.at(QUERY_TIME).do(schedule_task)
    next_run_time = schedule.next_run()
    log_info(f"Next run scheduled at {next_run_time}")

if __name__ == '__main__':
    schedule_jobs()
    while True:
        schedule.run_pending()
        time.sleep(1)
