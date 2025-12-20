"""
JIRA Client for creating issues and running queries
"""

import os
from typing import Optional, Dict, Any, List
from atlassian import Jira


class JIRAHelper:
    def __init__(self, url: str = None, username: str = None, password: str = None, token: str = None):
        """
        Initialize JIRA client
        
        Args:
            url: JIRA URL (optional, defaults to JIRA_URL env var)
            username: JIRA username (optional, defaults to JIRA_USERNAME env var)
            password: JIRA password (optional, defaults to JIRA_PASSWORD env var)
            token: API token (alternative authentication method)
        """
        # Get credentials from parameters or environment variables
        self.url = url or os.getenv('JIRA_URL')
        self.username = username or os.getenv('JIRA_USERNAME')
        self.password = password or os.getenv('JIRA_PASSWORD')
        self.token = token or os.getenv('JIRA_TOKEN')
        
        if not self.url:
            raise ValueError("JIRA URL must be provided either as parameter or JIRA_URL environment variable")
        
        # Initialize JIRA client based on authentication method
        if self.token:
            self.jira = Jira(url=self.url, token=self.token)
        elif self.username and self.password:
            self.jira = Jira(url=self.url, username=self.username, password=self.password)
        else:
            raise ValueError(
                "Authentication credentials must be provided. Either:\n"
                "- JIRA_TOKEN environment variable or token parameter\n"
                "- JIRA_USERNAME and JIRA_PASSWORD environment variables or username/password parameters"
            )

    def create_issue(self, 
                    project_key: str,
                    issue_type: str,
                    summary: str,
                    description: str = None,
                    assignee: str = None,
                    priority: str = "Medium",
                    labels: List[str] = None,
                    custom_fields: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create a new JIRA issue
        
        Args:
            project_key: Project key (e.g., 'PROJ')
            issue_type: Issue type (e.g., 'Task', 'Bug', 'Story')
            summary: Issue summary/title
            description: Issue description (optional)
            assignee: Assignee account ID or username (optional)
            priority: Priority level (default: 'Medium')
            labels: List of labels to apply (optional)
            custom_fields: Dictionary of custom field values (optional)
            
        Returns:
            Created issue data
        """
        issue_data = {
            'project': {'key': project_key},
            'issuetype': {'name': issue_type},
            'summary': summary,
        }
        
        if description:
            issue_data['description'] = description
        if assignee:
            issue_data['assignee'] = {'name': assignee} if '@' not in assignee else {'accountId': assignee}
        if priority:
            issue_data['priority'] = {'name': priority}
        if labels:
            issue_data['labels'] = labels
        if custom_fields:
            issue_data.update(custom_fields)
        
        try:
            new_issue = self.jira.create_issue(fields=issue_data)
            print(f"Created issue: {new_issue['key']}")
            return new_issue
        except Exception as e:
            print(f"Error creating issue: {str(e)}")
            raise

    def search_issues(self, jql_query: str, max_results: int = 50, fields: List[str] = None) -> List[Dict[str, Any]]:
        """
        Run a JQL query to search for issues
        
        Args:
            jql_query: JQL query string
            max_results: Maximum number of results to return (default: 50)
            fields: List of specific fields to return (optional, returns all fields if None)
            
        Returns:
            List of issues matching the query
        """
        try:
            issues = self.jira.jql(jql=jql_query, limit=max_results, fields=fields)
            return issues.get('issues', [])
        except Exception as e:
            print(f"Error running query: {str(e)}")
            raise

    def get_issue(self, issue_key: str, fields: List[str] = None) -> Dict[str, Any]:
        """
        Get a specific issue by key
        
        Args:
            issue_key: Issue key (e.g., 'PROJ-123')
            fields: List of specific fields to return (optional)
            
        Returns:
            Issue data
        """
        try:
            issue = self.jira.issue(issue_key, fields=fields)
            return issue
        except Exception as e:
            print(f"Error retrieving issue {issue_key}: {str(e)}")
            raise

    def update_issue(self, issue_key: str, fields: Dict[str, Any]) -> bool:
        """
        Update an existing issue
        
        Args:
            issue_key: Issue key (e.g., 'PROJ-123')
            fields: Fields to update
            
        Returns:
            True if successful
        """
        try:
            self.jira.update_issue(issue_key, fields)
            print(f"Updated issue: {issue_key}")
            return True
        except Exception as e:
            print(f"Error updating issue {issue_key}: {str(e)}")
            return False

    def add_comment(self, issue_key: str, comment: str) -> bool:
        """
        Add a comment to an issue
        
        Args:
            issue_key: Issue key (e.g., 'PROJ-123')
            comment: Comment text
            
        Returns:
            True if successful
        """
        try:
            self.jira.add_comment(issue_key, comment)
            print(f"Added comment to issue: {issue_key}")
            return True
        except Exception as e:
            print(f"Error adding comment to issue {issue_key}: {str(e)}")
            return False

    def transition_issue(self, issue_key: str, status: str) -> bool:
        """
        Transition an issue to a new status
        
        Args:
            issue_key: Issue key (e.g., 'PROJ-123')
            status: Target status (e.g., 'In Progress', 'Done')
            
        Returns:
            True if successful
        """
        try:
            # Get available transitions
            transitions = self.jira.get_issue_transitions(issue_key)
            target_transition = None
            
            for transition in transitions:
                if transition['name'].lower() == status.lower():
                    target_transition = transition['id']
                    break
            
            if target_transition:
                self.jira.transition_issue(issue_key, target_transition)
                print(f"Transitioned issue {issue_key} to {status}")
                return True
            else:
                print(f"Transition '{status}' not found for issue {issue_key}. Available transitions: {[t['name'] for t in transitions]}")
                return False
        except Exception as e:
            print(f"Error transitioning issue {issue_key}: {str(e)}")
            return False