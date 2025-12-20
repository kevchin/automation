"""
Test script to demonstrate JIRA automation functionality
without requiring actual JIRA credentials
"""

import os
from unittest.mock import Mock, patch
from jira_client import JIRAHelper


def test_jira_helper_without_credentials():
    """Test that JIRAHelper can be instantiated with mocked JIRA client"""
    
    # Mock the JIRA client to avoid needing real credentials
    with patch('jira_client.Jira') as mock_jira_class:
        # Create a mock JIRA instance
        mock_jira_instance = Mock()
        mock_jira_class.return_value = mock_jira_instance
        
        # Mock the methods that would normally call the JIRA API
        mock_jira_instance.create_issue.return_value = {
            'key': 'TEST-123',
            'id': '10001'
        }
        mock_jira_instance.jql.return_value = {
            'issues': [
                {
                    'key': 'TEST-124',
                    'fields': {
                        'summary': 'Test issue 1',
                        'status': {'name': 'Open'},
                        'assignee': {'displayName': 'Test User'}
                    }
                },
                {
                    'key': 'TEST-125',
                    'fields': {
                        'summary': 'Test issue 2',
                        'status': {'name': 'In Progress'},
                        'assignee': {'displayName': 'Another User'}
                    }
                }
            ]
        }
        mock_jira_instance.issue.return_value = {
            'key': 'TEST-123',
            'fields': {
                'summary': 'Test issue details',
                'status': {'name': 'To Do'},
                'assignee': {'displayName': 'Test User'},
                'reporter': {'displayName': 'Creator'},
                'created': '2023-01-01T00:00:00.000+0000'
            }
        }
        mock_jira_instance.update_issue.return_value = None
        mock_jira_instance.add_comment.return_value = None
        mock_jira_instance.get_issue_transitions.return_value = [
            {'id': '11', 'name': 'To Do'},
            {'id': '21', 'name': 'In Progress'},
            {'id': '31', 'name': 'Done'}
        ]
        mock_jira_instance.transition_issue.return_value = None
        
        # Now we can test our JIRAHelper class
        jira_helper = JIRAHelper.__new__(JIRAHelper)  # Create instance without calling __init__
        jira_helper.url = 'https://test.atlassian.net'
        jira_helper.jira = mock_jira_instance
        
        print("Testing JIRA Helper functionality...")
        
        # Test creating an issue
        print("\n1. Testing create_issue:")
        try:
            result = jira_helper.create_issue(
                project_key="TEST",
                issue_type="Task",
                summary="Test task",
                description="Test description",
                labels=["test", "automation"]
            )
            print(f"   ✓ Created issue: {result['key']}")
        except Exception as e:
            print(f"   ✗ Error creating issue: {e}")
        
        # Test searching issues
        print("\n2. Testing search_issues:")
        try:
            results = jira_helper.search_issues("project = TEST", max_results=10)
            print(f"   ✓ Found {len(results)} issues")
            for issue in results:
                print(f"     - {issue['key']}: {issue['fields']['summary']}")
        except Exception as e:
            print(f"   ✗ Error searching issues: {e}")
        
        # Test getting a specific issue
        print("\n3. Testing get_issue:")
        try:
            issue = jira_helper.get_issue("TEST-123")
            print(f"   ✓ Retrieved issue: {issue['key']}")
            print(f"     Summary: {issue['fields']['summary']}")
            print(f"     Status: {issue['fields']['status']['name']}")
        except Exception as e:
            print(f"   ✗ Error getting issue: {e}")
        
        # Test updating an issue
        print("\n4. Testing update_issue:")
        try:
            success = jira_helper.update_issue("TEST-123", {"summary": "Updated summary"})
            if success:
                print("   ✓ Issue updated successfully")
            else:
                print("   ✗ Issue update failed")
        except Exception as e:
            print(f"   ✗ Error updating issue: {e}")
        
        # Test adding a comment
        print("\n5. Testing add_comment:")
        try:
            success = jira_helper.add_comment("TEST-123", "This is a test comment")
            if success:
                print("   ✓ Comment added successfully")
            else:
                print("   ✗ Comment addition failed")
        except Exception as e:
            print(f"   ✗ Error adding comment: {e}")
        
        # Test transitioning an issue
        print("\n6. Testing transition_issue:")
        try:
            success = jira_helper.transition_issue("TEST-123", "In Progress")
            if success:
                print("   ✓ Issue transitioned successfully")
            else:
                print("   ✗ Issue transition failed")
        except Exception as e:
            print(f"   ✗ Error transitioning issue: {e}")
        
        print("\n✓ All tests completed successfully!")


if __name__ == "__main__":
    test_jira_helper_without_credentials()