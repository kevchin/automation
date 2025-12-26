import os
import time
import re
from pathlib import Path
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

class ThreadedSlackKeywordMonitor:
    def __init__(self, bot_token_file='SLACK_BOT_KEY.txt', channel_id='C1234567', keyword='bugbot', check_interval=30):
        """
        Initialize the Slack monitor with thread-aware functionality

        Args:
            bot_token_file: Path to the file containing the Slack bot token
            channel_id: Channel ID to monitor
            keyword: Keyword to look for in messages
            check_interval: Time interval (in seconds) between checks
        """
        self.channel_id = channel_id
        self.keyword = keyword.lower()  # Case insensitive matching
        self.check_interval = check_interval
        self.last_timestamp = None

        # Dictionary to store thread contexts - though we'll mainly use the API to fetch current context
        # This could be used for caching if needed later
        self.thread_contexts = {}

        # Read the bot token
        try:
            with open(bot_token_file, 'r') as f:
                token = f.read().strip()
            self.client = WebClient(token=token)
        except FileNotFoundError:
            raise Exception(f"Bot token file '{bot_token_file}' not found")
        except Exception as e:
            raise Exception(f"Error initializing Slack client: {str(e)}")

    def clean_message(self, original_text):
        """
        Remove the keyword and any leading whitespace from the original message
        """
        # Create pattern to match the keyword (case-insensitive) with possible leading/trailing spaces
        pattern = r'\s*' + re.escape(self.keyword) + r'\s*'
        cleaned = re.sub(pattern, ' ', original_text, flags=re.IGNORECASE)
        # Replace multiple consecutive spaces with single space and strip
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned

    def get_thread_context(self, thread_ts):
        """
        Retrieve all messages in a thread and concatenate them into a context
        """
        try:
            response = self.client.conversations_replies(
                channel=self.channel_id,
                ts=thread_ts
            )
            
            messages = response['messages']
            thread_context = []
            
            for msg in messages:
                user_id = msg.get('user', 'unknown')
                text = msg.get('text', '')
                
                # Format each message as "User: message"
                formatted_msg = f"<@{user_id}>: {text}"
                thread_context.append(formatted_msg)
            
            # Concatenate all messages into a single context string
            return '\n'.join(thread_context)
        
        except SlackApiError as e:
            print(f"Error retrieving thread context: {e}")
            return ""

    def get_new_messages(self):
        """
        Fetch messages since the last check
        """
        try:
            # Set oldest timestamp to last checked time, or fetch recent messages if first run
            oldest = self.last_timestamp if self.last_timestamp else str(time.time() - self.check_interval * 2)

            response = self.client.conversations_history(
                channel=self.channel_id,
                oldest=oldest,
                inclusive=True  # Back to True, but we'll handle duplicates carefully
            )

            messages = response['messages']
            new_messages = []
            max_timestamp_in_batch = self.last_timestamp  # Track the max timestamp in this batch

            for msg in messages:
                # Only consider messages that came after our last check
                if self.last_timestamp is None or float(msg['ts']) > float(self.last_timestamp):
                    new_messages.append(msg)

                    # Track the max timestamp in this batch (don't update instance variable yet)
                    if max_timestamp_in_batch is None or float(msg['ts']) > float(max_timestamp_in_batch):
                        max_timestamp_in_batch = msg['ts']

            # After processing all messages in this batch, update the instance variable
            if max_timestamp_in_batch != self.last_timestamp:
                self.last_timestamp = max_timestamp_in_batch

            return new_messages

        except SlackApiError as e:
            print(f"Error fetching messages: {e}")
            return []

    def find_keyword_messages(self, messages):
        """
        Filter messages that contain the keyword
        """
        keyword_messages = []

        for msg in messages:
            if 'text' in msg and self.keyword in msg['text'].lower():
                keyword_messages.append(msg)

        return keyword_messages

    def is_in_thread(self, message):
        """
        Check if a message is part of a thread
        """
        # A message is in a thread if it has a 'thread_ts' field that's different from its own 'ts'
        # Root messages in a thread have 'thread_ts' equal to their own 'ts'
        # Messages in a thread but not root have 'thread_ts' different from their 'ts'
        if 'thread_ts' in message and message['thread_ts'] != message['ts']:
            return True
        return False

    def is_thread_root(self, message):
        """
        Check if a message is the root of a thread
        """
        # Root messages in a thread have 'thread_ts' equal to their own 'ts'
        if 'thread_ts' in message and message['thread_ts'] == message['ts']:
            return True
        return False

    def reply_to_message(self, message):
        """
        Reply to a message appropriately based on whether it's in a thread
        """
        try:
            original_text = message['text']
            user_id = message.get('user', 'unknown')
            is_threaded = self.is_in_thread(message)

            print(f"DEBUG: Processing message - ts:{message.get('ts')}, thread_ts:{message.get('thread_ts')}, text:'{original_text[:30]}...'")
            print(f"DEBUG: is_threaded result: {is_threaded}")

            # Get the cleaned message (without the keyword)
            cleaned_message = self.clean_message(original_text)

            # Check if the message is part of any thread (either as root or reply)
            has_thread_ts = 'thread_ts' in message
            in_existing_thread = is_threaded or (has_thread_ts and message['thread_ts'] == message['ts'])

            print(f"DEBUG: has_thread_ts: {has_thread_ts}, in_existing_thread: {in_existing_thread}")

            if in_existing_thread:
                # Message is in an existing thread (either as root or as reply)
                # For both cases, use the thread_ts to identify the thread
                # For thread roots: message['thread_ts'] == message['ts']
                # For thread replies: message['thread_ts'] != message['ts'], but we still use message['thread_ts']
                thread_identifier = message['thread_ts']  # This identifies the original thread
                print(f"DEBUG: Getting context for thread starting with ts: {thread_identifier}")
                thread_context = self.get_thread_context(thread_identifier)

                # Format the reply with full thread context
                reply_text = f"Hello <@{user_id}>, I detected your keyword in this thread:\n\n{thread_context}\n\nCleaned input: '{cleaned_message}'"

                print(f"DEBUG: Posting reply to thread using thread_ts: {thread_identifier}")

                # Post the reply in the same thread using the original thread's root timestamp
                response = self.client.chat_postMessage(
                    channel=self.channel_id,
                    text=reply_text,
                    thread_ts=thread_identifier  # This ensures the reply stays in the original thread
                )

                print(f"Replied in existing thread to message from {user_id}: {original_text[:50]}...")
                print(f"DEBUG: Bot reply timestamp: {response.get('ts', 'N/A')}")

            else:
                # Message is not in any thread (main channel message)
                reply_text = f"Hello <@{user_id}>, I detected your keyword in your message: '{cleaned_message}'. Starting a new thread..."

                print(f"DEBUG: Posting reply to create new thread with thread_ts: {message['ts']}")

                # Post the reply in a thread (starting a new thread by using the original message's ts as thread_ts)
                response = self.client.chat_postMessage(
                    channel=self.channel_id,
                    text=reply_text,
                    thread_ts=message['ts']  # This creates the threaded reply
                )

                print(f"Started new thread for message from {user_id}: {original_text[:50]}...")
                print(f"DEBUG: Bot reply timestamp: {response.get('ts', 'N/A')}")

        except SlackApiError as e:
            print(f"Error posting reply: {e}")
        except Exception as e:
            print(f"Unexpected error in reply_to_message: {e}")

    def run(self):
        """
        Main monitoring loop
        """
        print(f"Starting Threaded Slack monitor for keyword '{self.keyword}' in channel {self.channel_id}")
        print(f"Checking every {self.check_interval} seconds...")

        while True:
            try:
                # Get new messages since last check
                new_messages = self.get_new_messages()

                # Find messages containing the keyword
                keyword_messages = self.find_keyword_messages(new_messages)

                # Reply to each keyword-containing message
                for msg in keyword_messages:
                    self.reply_to_message(msg)

                # Wait before next check with countdown updates every 5 seconds
                remaining_time = self.check_interval
                while remaining_time > 0:
                    if remaining_time % 5 == 0 or remaining_time <= 5:
                        print(f"Next check in {remaining_time} seconds...")

                    sleep_time = min(5, remaining_time)
                    time.sleep(sleep_time)
                    remaining_time -= sleep_time

            except KeyboardInterrupt:
                print("\nShutting down Threaded Slack monitor...")
                break
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                time.sleep(self.check_interval)


def main():
    # Configuration
    BOT_TOKEN_FILE = 'SLACK_BOT_KEY.txt'
    # Read channel ID from file if present, otherwise fall back to env var
    def _get_channel_id(filename: str = 'CHANNEL_ID.txt') -> str:
        candidate = Path(__file__).resolve().parent / filename
        if candidate.exists():
            text = candidate.read_text(encoding='utf-8').strip()
            for line in text.splitlines():
                channel = line.strip()
                if channel:
                    return channel

        env = os.environ.get('CHANNEL_ID')
        if env:
            return env

        raise RuntimeError(
            f"Channel ID not found. Create {candidate} with the channel ID, or set CHANNEL_ID env var."
        )

    CHANNEL_ID = _get_channel_id()
    KEYWORD = 'bugbot'
    CHECK_INTERVAL = 30  # seconds

    # Create the monitor and start running
    monitor = ThreadedSlackKeywordMonitor(
        bot_token_file=BOT_TOKEN_FILE,
        channel_id=CHANNEL_ID,
        keyword=KEYWORD,
        check_interval=CHECK_INTERVAL
    )

    monitor.run()


if __name__ == "__main__":
    main()