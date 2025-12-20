# JIRA Automation Program

A Python program to create JIRA issues and run queries using the Atlassian Python API.

## Features

- Create new JIRA issues with customizable fields
- Run JQL queries to search for issues
- Retrieve specific issue details
- Update existing issues
- Add comments to issues
- Transition issues between statuses

## Setup

### Prerequisites

- Python 3.7+
- JIRA instance with API access
- Appropriate permissions to create and modify issues

### Installation

1. Install the required packages:
```bash
pip install -r requirements.txt
```

2. Set up authentication by either:
   - Using environment variables (recommended)
   - Passing credentials directly to the constructor

### Authentication Methods

#### Option 1: Environment Variables

Create a `.env` file in your project root (or set system environment variables):

```bash
JIRA_URL=https://your-domain.atlassian.net
JIRA_USERNAME=your-email@example.com
JIRA_PASSWORD=your-api-token
# OR use token-based authentication
JIRA_TOKEN=your-api-token
```

#### Option 2: Direct Parameters

Pass credentials directly when initializing the JIRAHelper:

```python
jira_helper = JIRAHelper(
    url="https://your-domain.atlassian.net",
    username="your-email@example.com",
    password="your-api-token"
)
# OR
jira_helper = JIRAHelper(
    url="https://your-domain.atlassian.net",
    token="your-api-token"
)
```

## Usage Examples

### Creating an Issue

```python
from jira_client import JIRAHelper

jira_helper = JIRAHelper()

new_issue = jira_helper.create_issue(
    project_key="PROJ",
    issue_type="Task",
    summary="Sample Task",
    description="Description of the task",
    assignee="assignee-account-id",  # Optional
    priority="High",  # Optional, default is "Medium"
    labels=["bug", "urgent"],  # Optional
    custom_fields={"customfield_12345": "Custom Value"}  # Optional
)
print(f"Created issue: {new_issue['key']}")
```

### Running Queries

```python
# Search for open bugs in a project
issues = jira_helper.search_issues(
    jql_query="project = PROJ AND issuetype = Bug AND status = Open",
    max_results=50
)

for issue in issues:
    print(f"{issue['key']}: {issue['fields']['summary']}")
```

### Updating an Issue

```python
success = jira_helper.update_issue(
    issue_key="PROJ-123",
    fields={
        "summary": "Updated Summary",
        "description": "Updated description",
        "priority": {"name": "High"}
    }
)
```

### Adding Comments

```python
success = jira_helper.add_comment(
    issue_key="PROJ-123",
    comment="This is a helpful comment added via API"
)
```

## Running the Example

To run the example script:

```bash
cd jira_automation
python example_usage.py
```

Make sure to update the project keys and JQL queries in the example to match your JIRA setup.

## Security Notes

- Store API tokens securely and don't commit them to version control
- Use environment variables for sensitive information
- Follow your organization's security policies when automating JIRA interactions

## Error Handling

The JIRAHelper class includes basic error handling. All methods will print error messages and re-raise exceptions so you can handle them appropriately in your application.