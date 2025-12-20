"""
Configuration settings for JIRA automation
"""

import os
from typing import Optional


class Config:
    """Configuration class for JIRA settings"""
    
    # JIRA connection settings
    JIRA_URL: str = os.getenv('JIRA_URL', '')
    JIRA_USERNAME: str = os.getenv('JIRA_USERNAME', '')
    JIRA_PASSWORD: str = os.getenv('JIRA_PASSWORD', '')
    JIRA_TOKEN: str = os.getenv('JIRA_TOKEN', '')
    
    # Default values for issue creation
    DEFAULT_PROJECT_KEY: str = os.getenv('DEFAULT_PROJECT_KEY', 'TEST')
    DEFAULT_ISSUE_TYPE: str = os.getenv('DEFAULT_ISSUE_TYPE', 'Task')
    DEFAULT_PRIORITY: str = os.getenv('DEFAULT_PRIORITY', 'Medium')
    
    # Query settings
    DEFAULT_MAX_RESULTS: int = int(os.getenv('DEFAULT_MAX_RESULTS', '50'))
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that required configuration values are present"""
        if not cls.JIRA_URL:
            raise ValueError("JIRA_URL must be set in environment variables or config")
        
        if not (cls.JIRA_TOKEN or (cls.JIRA_USERNAME and cls.JIRA_PASSWORD)):
            raise ValueError(
                "Either JIRA_TOKEN or both JIRA_USERNAME and JIRA_PASSWORD must be set"
            )
        
        return True
    
    @classmethod
    def get_auth_info(cls) -> dict:
        """Get authentication information"""
        auth_info = {
            'url': cls.JIRA_URL,
        }
        
        if cls.JIRA_TOKEN:
            auth_info['token'] = cls.JIRA_TOKEN
        else:
            auth_info['username'] = cls.JIRA_USERNAME
            auth_info['password'] = cls.JIRA_PASSWORD
            
        return auth_info