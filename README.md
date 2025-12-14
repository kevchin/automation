# Slack Keyword Monitor

A Python program that monitors Slack messages for a specific keyword and responds in threads.

## Features
- Monitors a specified Slack channel for messages containing a keyword
- Responds to matching messages in a thread
- Configurable keyword, channel, and check interval
- Removes the keyword from the original message in the response

## Requirements
- Python 3.x
- Slack Bot Token

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Place your Slack bot token in `SLACK_BOT_KEY.txt`
3. Configure the channel ID and keyword in the script
4. Run the script: `python slack_monitor.py`

## Configuration
- `SLACK_BOT_KEY.txt`: File containing your Slack bot token
- `channel_id`: The ID of the Slack channel to monitor (default: C1234567)
- `keyword`: The keyword to search for (default: bugbot)
- `check_interval`: How often to check for new messages (default: 30 seconds)

## Usage
The program runs continuously, checking for new messages every n seconds. When it finds a message containing the keyword, it responds in a thread with the format: "Hello <@user>, I will respond to your input '<original message with keyword removed>'."
