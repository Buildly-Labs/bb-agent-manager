"""
Git Operations Tools for BB Agent Manager
Handles PR creation, issue management, and code review workflows
"""
from typing import Dict, Any, Optional, List
import httpx
import os

class GitHubClient:
    """GitHub API client for PR and issue management"""
    
    def __init__(self, token: str, repo: str):
        self.token = token
        self.repo = repo  # format: "owner/repo"
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
    
    async def create_pull_request(
        self,
        title: str,
        body: str,
        head: str,
        base: str = "main",
        draft: bool = True,
        labels: Optional[List[str]] = None,
        reviewers: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a pull request with automatic draft mode for human review
        
        Args:
            title: PR title
            body: PR description
            head: Source branch
            base: Target branch (default: main)
            draft: Create as draft PR (default: True for human review)
            labels: Labels to apply
            reviewers: Reviewers to request
        """
        async with httpx.AsyncClient() as client:
            # Create PR
            pr_data = {
                "title": title,
                "body": body,
                "head": head,
                "base": base,
                "draft": draft
            }
            
            response = await client.post(
                f"{self.base_url}/repos/{self.repo}/pulls",
                headers=self.headers,
                json=pr_data
            )
            
            if response.status_code not in [200, 201]:
                return {"error": f"Failed to create PR: {response.text}", "status": response.status_code}
            
            pr = response.json()
            pr_number = pr["number"]
            
            # Add labels if provided
            if labels:
                await client.post(
                    f"{self.base_url}/repos/{self.repo}/issues/{pr_number}/labels",
                    headers=self.headers,
                    json={"labels": labels}
                )
            
            # Request reviewers if provided
            if reviewers:
                await client.post(
                    f"{self.base_url}/repos/{self.repo}/pulls/{pr_number}/requested_reviewers",
                    headers=self.headers,
                    json={"reviewers": reviewers}
                )
            
            return {
                "success": True,
                "pr_number": pr_number,
                "pr_url": pr["html_url"],
                "draft": draft,
                "message": f"PR #{pr_number} created successfully" + (" (draft - requires human review)" if draft else "")
            }
    
    async def close_issue(
        self,
        issue_number: int,
        comment: Optional[str] = None,
        reason: str = "completed"
    ) -> Dict[str, Any]:
        """
        Close an issue with optional comment
        Only closes if checks pass and PR is merged
        """
        async with httpx.AsyncClient() as client:
            # Add comment if provided
            if comment:
                await client.post(
                    f"{self.base_url}/repos/{self.repo}/issues/{issue_number}/comments",
                    headers=self.headers,
                    json={"body": comment}
                )
            
            # Close issue
            response = await client.patch(
                f"{self.base_url}/repos/{self.repo}/issues/{issue_number}",
                headers=self.headers,
                json={"state": "closed", "state_reason": reason}
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "issue_number": issue_number,
                    "message": f"Issue #{issue_number} closed successfully"
                }
            else:
                return {"error": f"Failed to close issue: {response.text}"}
    
    async def get_pr_status(self, pr_number: int) -> Dict[str, Any]:
        """Get PR status including checks and review status"""
        async with httpx.AsyncClient() as client:
            # Get PR details
            pr_response = await client.get(
                f"{self.base_url}/repos/{self.repo}/pulls/{pr_number}",
                headers=self.headers
            )
            
            if pr_response.status_code != 200:
                return {"error": "PR not found"}
            
            pr = pr_response.json()
            
            # Get check runs
            checks_response = await client.get(
                f"{self.base_url}/repos/{self.repo}/commits/{pr['head']['sha']}/check-runs",
                headers=self.headers
            )
            
            checks = checks_response.json() if checks_response.status_code == 200 else {}
            check_runs = checks.get("check_runs", [])
            
            all_checks_passed = all(run["conclusion"] == "success" for run in check_runs if run.get("conclusion"))
            
            return {
                "pr_number": pr_number,
                "state": pr["state"],
                "draft": pr["draft"],
                "mergeable": pr.get("mergeable"),
                "merged": pr.get("merged", False),
                "checks_passed": all_checks_passed,
                "total_checks": len(check_runs),
                "reviews": pr.get("requested_reviewers", []),
                "url": pr["html_url"]
            }
    
    async def add_pr_comment(self, pr_number: int, comment: str) -> Dict[str, Any]:
        """Add a comment to a PR"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/repos/{self.repo}/issues/{pr_number}/comments",
                headers=self.headers,
                json={"body": comment}
            )
            
            if response.status_code == 201:
                return {"success": True, "message": "Comment added successfully"}
            else:
                return {"error": f"Failed to add comment: {response.text}"}


# Tool definitions for MCP
GIT_CREATE_PR_TOOL = {
    "name": "create_pull_request",
    "description": "Create a pull request from current branch. Always creates as DRAFT requiring human review before merging.",
    "parameters": {
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "PR title summarizing the changes"},
            "body": {"type": "string", "description": "Detailed PR description with context"},
            "head": {"type": "string", "description": "Source branch name"},
            "base": {"type": "string", "description": "Target branch (default: main)", "default": "main"},
            "labels": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Labels to apply (e.g., ['bug', 'enhancement', 'ai-generated'])"
            },
            "reviewers": {
                "type": "array",
                "items": {"type": "string"},
                "description": "GitHub usernames to request review from"
            }
        },
        "required": ["title", "body", "head"]
    }
}

GIT_CLOSE_ISSUE_TOOL = {
    "name": "close_issue",
    "description": "Close an issue. Only use this when PR checks have passed and changes are merged.",
    "parameters": {
        "type": "object",
        "properties": {
            "issue_number": {"type": "integer", "description": "Issue number to close"},
            "comment": {"type": "string", "description": "Optional closing comment explaining resolution"},
            "reason": {
                "type": "string",
                "enum": ["completed", "not_planned"],
                "description": "Reason for closing",
                "default": "completed"
            }
        },
        "required": ["issue_number"]
    }
}

GIT_PR_STATUS_TOOL = {
    "name": "get_pr_status",
    "description": "Get status of a pull request including checks and reviews",
    "parameters": {
        "type": "object",
        "properties": {
            "pr_number": {"type": "integer", "description": "PR number to check"}
        },
        "required": ["pr_number"]
    }
}

GIT_PR_COMMENT_TOOL = {
    "name": "add_pr_comment",
    "description": "Add a comment to a pull request",
    "parameters": {
        "type": "object",
        "properties": {
            "pr_number": {"type": "integer", "description": "PR number"},
            "comment": {"type": "string", "description": "Comment text"}
        },
        "required": ["pr_number", "comment"]
    }
}

# Tool implementations
async def create_pull_request(
    title: str,
    body: str,
    head: str,
    base: str = "main",
    labels: Optional[List[str]] = None,
    reviewers: Optional[List[str]] = None,
    settings = None
) -> str:
    """Create a pull request (always as draft for human review)"""
    if not settings or not settings.github_token or not settings.github_repo:
        return "Error: GitHub token and repo must be configured"
    
    # Always add 'ai-generated' label for transparency
    all_labels = labels or []
    if "ai-generated" not in all_labels:
        all_labels.append("ai-generated")
    
    client = GitHubClient(settings.github_token, settings.github_repo)
    result = await client.create_pull_request(
        title=title,
        body=f"🤖 **AI-Generated PR**\n\n{body}\n\n---\n*This PR was created by BB Agent Manager and requires human review before merging.*",
        head=head,
        base=base,
        draft=settings.create_draft_prs,  # Controlled by config
        labels=all_labels,
        reviewers=reviewers
    )
    
    return str(result)

async def close_issue(
    issue_number: int,
    comment: Optional[str] = None,
    reason: str = "completed",
    settings = None
) -> str:
    """Close an issue (only if auto_close_issues is enabled)"""
    if not settings or not settings.github_token or not settings.github_repo:
        return "Error: GitHub token and repo must be configured"
    
    if not settings.auto_close_issues:
        return f"Auto-close disabled. Please manually close issue #{issue_number}"
    
    client = GitHubClient(settings.github_token, settings.github_repo)
    result = await client.close_issue(issue_number, comment, reason)
    return str(result)

async def get_pr_status(pr_number: int, settings = None) -> str:
    """Get PR status"""
    if not settings or not settings.github_token or not settings.github_repo:
        return "Error: GitHub token and repo must be configured"
    
    client = GitHubClient(settings.github_token, settings.github_repo)
    result = await client.get_pr_status(pr_number)
    return str(result)

async def add_pr_comment(pr_number: int, comment: str, settings = None) -> str:
    """Add comment to PR"""
    if not settings or not settings.github_token or not settings.github_repo:
        return "Error: GitHub token and repo must be configured"
    
    client = GitHubClient(settings.github_token, settings.github_repo)
    result = await client.add_pr_comment(pr_number, comment)
    return str(result)
