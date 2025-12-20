#!/usr/bin/env python3
"""
Command Line Interface for JIRA Automation
"""

import argparse
from jira_client import JIRAHelper
from config import Config
from dotenv import load_dotenv
import sys
import json


def create_issue_cli(args):
    """Handle the create-issue command"""
    try:
        jira_helper = JIRAHelper(**Config.get_auth_info())
        
        # Parse labels if provided
        labels = args.labels.split(',') if args.labels else []
        
        new_issue = jira_helper.create_issue(
            project_key=args.project,
            issue_type=args.type,
            summary=args.summary,
            description=args.description,
            assignee=args.assignee,
            priority=args.priority,
            labels=labels
        )
        
        print(f"Successfully created issue: {new_issue['key']}")
        if args.output_format == 'json':
            print(json.dumps(new_issue, indent=2))
        
    except Exception as e:
        print(f"Error creating issue: {e}")
        sys.exit(1)


def search_issues_cli(args):
    """Handle the search command"""
    try:
        jira_helper = JIRAHelper(**Config.get_auth_info())
        
        issues = jira_helper.search_issues(
            jql_query=args.query,
            max_results=args.max_results
        )
        
        if args.output_format == 'json':
            print(json.dumps(issues, indent=2))
        else:
            print(f"Found {len(issues)} issues:")
            for issue in issues:
                print(f"  - {issue['key']}: {issue['fields']['summary']}")
                
    except Exception as e:
        print(f"Error searching issues: {e}")
        sys.exit(1)


def get_issue_cli(args):
    """Handle the get-issue command"""
    try:
        jira_helper = JIRAHelper(**Config.get_auth_info())
        
        issue = jira_helper.get_issue(args.issue_key)
        
        if args.output_format == 'json':
            print(json.dumps(issue, indent=2))
        else:
            print(f"Issue Key: {issue['key']}")
            print(f"Summary: {issue['fields']['summary']}")
            print(f"Status: {issue['fields']['status']['name']}")
            print(f"Assignee: {issue['fields'].get('assignee', {}).get('displayName', 'Unassigned')}")
            print(f"Reporter: {issue['fields']['reporter']['displayName']}")
            print(f"Created: {issue['fields']['created']}")
        
    except Exception as e:
        print(f"Error getting issue: {e}")
        sys.exit(1)


def add_comment_cli(args):
    """Handle the add-comment command"""
    try:
        jira_helper = JIRAHelper(**Config.get_auth_info())
        
        success = jira_helper.add_comment(args.issue_key, args.comment)
        
        if success:
            print(f"Successfully added comment to issue {args.issue_key}")
        else:
            print(f"Failed to add comment to issue {args.issue_key}")
            sys.exit(1)
        
    except Exception as e:
        print(f"Error adding comment: {e}")
        sys.exit(1)


def setup_parser():
    """Set up the argument parser"""
    parser = argparse.ArgumentParser(description='JIRA Automation CLI')
    parser.add_argument('--output-format', '-o', choices=['text', 'json'], 
                       default='text', help='Output format (default: text)')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create issue command
    create_parser = subparsers.add_parser('create-issue', help='Create a new JIRA issue')
    create_parser.add_argument('--project', '-p', required=True, help='Project key')
    create_parser.add_argument('--type', '-t', required=True, help='Issue type (e.g., Task, Bug, Story)')
    create_parser.add_argument('--summary', '-s', required=True, help='Issue summary')
    create_parser.add_argument('--description', '-d', help='Issue description')
    create_parser.add_argument('--assignee', '-a', help='Assignee username or account ID')
    create_parser.add_argument('--priority', help='Priority level', default='Medium')
    create_parser.add_argument('--labels', help='Comma-separated list of labels')
    create_parser.set_defaults(func=create_issue_cli)
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search for JIRA issues')
    search_parser.add_argument('query', help='JQL query string')
    search_parser.add_argument('--max-results', '-m', type=int, default=50, 
                              help='Maximum number of results (default: 50)')
    search_parser.set_defaults(func=search_issues_cli)
    
    # Get issue command
    get_parser = subparsers.add_parser('get-issue', help='Get details of a specific issue')
    get_parser.add_argument('issue_key', help='Issue key (e.g., PROJ-123)')
    get_parser.set_defaults(func=get_issue_cli)
    
    # Add comment command
    comment_parser = subparsers.add_parser('add-comment', help='Add a comment to an issue')
    comment_parser.add_argument('issue_key', help='Issue key (e.g., PROJ-123)')
    comment_parser.add_argument('comment', help='Comment text')
    comment_parser.set_defaults(func=add_comment_cli)
    
    return parser


def main():
    # Load environment variables
    load_dotenv()
    
    # Validate configuration
    try:
        Config.validate()
    except ValueError as e:
        print(f"Configuration error: {e}")
        sys.exit(1)
    
    parser = setup_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == '__main__':
    main()