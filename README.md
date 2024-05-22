
---

# Google Analytics Reporting Bot

## Introduction / 简介

This project is an automated Google Analytics reporting bot written in Python. The program queries Google Analytics data at a specified time every day and sends the results to a specified Telegram chat.

该项目是一个自动化的Google Analytics数据报告机器人，使用Python编写。该程序每天在指定的时间查询Google Analytics数据，并将结果发送到指定的Telegram聊天中。

## Features / 功能

- Daily scheduled queries of Google Analytics data
- Aggregation and formatting of data
- Sending results via Telegram Bot
- Logging of information and errors during the query process

- 每天定时查询Google Analytics数据
- 聚合并格式化数据
- 通过Telegram Bot发送结果
- 日志记录查询过程中的信息和错误

## Requirements / 依赖

- Python 3.7+
- Google Analytics API
- Telegram Bot API

## Installation / 安装

1. Clone the repository / 克隆仓库：

   ```bash
   git clone https://github.com/cecats/googleanalytics.git
   cd googleanalytics
   ```

2. Install the required Python packages / 安装所需的Python包：

   ```bash
   pip install -r requirements.txt
   ```

3. Create and configure `config.ini` / 创建并配置 `config.ini`：

   ```ini
   [DEFAULT]
   SCOPES = https://www.googleapis.com/auth/analytics.readonly
   KEY_FILE_LOCATION = credentials.json
   PROPERTY_ID = your_property_id  # Replace with your GA4 property ID
   PAGE_SIZE = 1000
   START_DATE = 30daysAgo
   END_DATE = today
   SITE_NAME = Example Site
   LOG_FILE = analytics_log.txt
   TELEGRAM_BOT_TOKEN = your_telegram_bot_token
   TELEGRAM_CHAT_ID = your_telegram_chat_id
   QUERY_TIME = 14:00  # Query time each day in HH:MM format
   ```

4. Obtain your `credentials.json` from Google Cloud Platform and place it in the project directory / 从Google Cloud Platform获取您的 `credentials.json` 文件，并将其放置在项目目录中。

## Usage / 用法

Run the script / 运行脚本：

```bash
python3 show_info.py
```

The script will run indefinitely, querying Google Analytics data at the specified time each day and sending the results to the configured Telegram chat.

该脚本将无限期运行，每天在指定的时间查询Google Analytics数据，并将结果发送到配置的Telegram聊天中。

## Logging / 日志记录

Logs are written to the file specified in `config.ini` (default is `analytics_log.txt`). This includes both informational messages and errors encountered during execution.

日志记录在 `config.ini` 中指定的文件中（默认是 `analytics_log.txt`）。这包括执行过程中遇到的信息和错误。

## License / 许可证

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

本项目根据MIT许可证授权 - 详见[LICENSE](LICENSE)文件。

---