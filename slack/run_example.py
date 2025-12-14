#!/usr/bin/env python3
"""
Example script to run the Slack keyword monitor with custom parameters
"""

from slack_monitor import SlackKeywordMonitor

def main():
    # Example with custom parameters
    monitor = SlackKeywordMonitor(
        bot_token_file='SLACK_BOT_KEY.txt',
        channel_id='C1234567',  # Replace with your actual channel ID
        keyword='bugbot',       # Replace with your desired keyword
        check_interval=10       # Check every 10 seconds
    )
    
    print("Starting Slack monitor...")
    print("Press Ctrl+C to stop")
    
    try:
        monitor.run()
    except KeyboardInterrupt:
        print("\nStopping monitor...")
        exit(0)

if __name__ == "__main__":
    main()