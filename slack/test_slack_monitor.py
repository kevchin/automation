"""
Test script to verify the functionality of the Slack monitor
"""

from slack_monitor import SlackKeywordMonitor
import re


def test_clean_message():
    """Test the clean_message function"""
    # Test basic functionality
    monitor = SlackKeywordMonitor(keyword='bugbot')
    
    test_cases = [
        ("bugbot this is a test", "this is a test"),
        ("this is bugbot a test", "this is a test"),
        ("this is a test bugbot", "this is a test"),
        ("  bugbot   this   is   a   test  ", "this is a test"),  # with extra whitespace
        ("BUGBOT case insensitive", "case insensitive"),  # case insensitive
        ("no keyword here", "no keyword here"),  # no keyword
        ("bugbot", ""),  # just the keyword
        ("bugbot bugbot duplicate", "duplicate"),  # duplicate keywords - first bugbot removes "bugbot ", second removes "bugbot" leaving " duplicate" -> "duplicate"
        ("before bugbot after", "before after"),  # keyword in middle
    ]
    
    print("Testing clean_message function:")
    for original, expected in test_cases:
        result = monitor.clean_message(original)
        status = "✓" if result == expected else "✗"
        print(f"{status} Original: '{original}' -> Cleaned: '{result}' (Expected: '{expected}')")


def test_keyword_matching():
    """Test keyword matching logic"""
    monitor = SlackKeywordMonitor(keyword='bugbot')
    
    test_messages = [
        {"text": "Hey bugbot can you help?", "should_match": True},
        {"text": "BUGBOT uppercase test", "should_match": True},
        {"text": "No keyword here", "should_match": False},
        {"text": "This has bugbot in the middle", "should_match": True},
    ]
    
    print("\nTesting keyword matching:")
    for msg in test_messages:
        contains_keyword = monitor.keyword in msg['text'].lower()
        status = "✓" if contains_keyword == msg['should_match'] else "✗"
        print(f"{status} Message: '{msg['text']}' -> Contains keyword: {contains_keyword}")


if __name__ == "__main__":
    test_clean_message()
    test_keyword_matching()
    print("\nAll tests completed!")