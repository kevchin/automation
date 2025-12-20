"""
Example usage of the JIRA Helper class
"""

from jira_client import JIRAHelper
from config import Config
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

def main():
    # Initialize JIRA client
    # You can pass credentials directly or use environment variables
    jira_helper = JIRAHelper()
    
    print("JIRA Helper initialized successfully!")
    
    # Example 1: Creating an issue
    print("\n--- Creating a new issue ---")
    try:
        new_issue = jira_helper.create_issue(
            project_key="TEST",  # Replace with your project key
            issue_type="Task",
            summary="Example Task Created via API",
            description="This is a sample task created using the JIRA Helper class.",
            priority="Medium",
            labels=["api-created", "automation"]
        )
        print(f"Successfully created issue: {new_issue['key']}")
        issue_key = new_issue['key']
    except Exception as e:
        print(f"Failed to create issue: {e}")
        # For demo purposes, let's use a mock issue key
        issue_key = "TEST-123"
    
    # Example 2: Running a simple JQL query
    print("\n--- Running JQL query ---")
    try:
        # Search for issues assigned to the current user
        issues = jira_helper.search_issues(
            jql_query="project = TEST AND summary ~ 'Example'",  # Adjust the query as needed
            max_results=10
        )
        print(f"Found {len(issues)} issues matching the query")
        for issue in issues[:3]:  # Show first 3 issues
            print(f"  - {issue['key']}: {issue['fields']['summary']}")
    except Exception as e:
        print(f"Failed to run query: {e}")
    
    # Example 3: Getting a specific issue
    print(f"\n--- Getting issue details for {issue_key} ---")
    try:
        issue_details = jira_helper.get_issue(issue_key)
        print(f"Issue Summary: {issue_details['fields']['summary']}")
        print(f"Issue Status: {issue_details['fields']['status']['name']}")
        print(f"Created: {issue_details['fields']['created']}")
    except Exception as e:
        print(f"Failed to get issue details: {e}")
    
    # Example 4: Adding a comment to an issue
    print(f"\n--- Adding a comment to {issue_key} ---")
    try:
        success = jira_helper.add_comment(
            issue_key,
            "This comment was added via the JIRA Helper API."
        )
        if success:
            print("Comment added successfully!")
    except Exception as e:
        print(f"Failed to add comment: {e}")
    
    # Example 5: Updating an issue
    print(f"\n--- Updating issue {issue_key} ---")
    try:
        success = jira_helper.update_issue(
            issue_key,
            {
                "labels": ["api-created", "automation", "updated-via-api"]
            }
        )
        if success:
            print("Issue updated successfully!")
    except Exception as e:
        print(f"Failed to update issue: {e}")

if __name__ == "__main__":
    main()