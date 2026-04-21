#!/usr/bin/env python3
import httpx
import json

# Your access token
access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzYzNjc3NjYyLCJpYXQiOjE3NjM2NzQwNjIsImp0aSI6ImMwYWIwMzcyNTQ4MzQwN2ZhN2ZlNjZhMTE5ZWVkNzAwIiwidXNlcl9pZCI6Mjg2LCJjb3JlX3VzZXJfdXVpZCI6ImQ0ZjY2MTRiLTYwNGEtNDI5MS05YWIxLTVlM2NmZTNmM2MzNSIsInVzZXJuYW1lIjoiZ2xpbmQiLCJvcmdhbml6YXRpb25fdXVpZCI6IjQ3ZDdkMDMyLWUwMDgtNDdiYS1hZTNlLWVjYjBjZjYwOWM4ZSIsImlzcyI6IkJ1aWxkbHkifQ.-BpP4SnR4wb3O9be4FuBmXtr2jqBQQCfLL9RPZ7NaHM"

# Fetch issues
response = httpx.get(
    "https://labs-api.buildly.io/release/issue/",
    headers={"Authorization": f"Bearer {access_token}"},
    timeout=30.0
)

if response.status_code == 200:
    issues = response.json()
    print(f"Total issues: {len(issues)}\n")

    # Show structure of first issue
    if issues:
        print("First issue structure:")
        print(json.dumps(issues[0], indent=2))
        print("\n" + "="*80 + "\n")

        # Filter issues assigned to "glind"
        my_issues = [i for i in issues if i.get('assigned_to') == 'glind' or
                     (isinstance(i.get('assigned_to'), dict) and i.get('assigned_to', {}).get('username') == 'glind')]

        if my_issues:
            print(f"Issues assigned to you: {len(my_issues)}\n")
            for issue in my_issues[:10]:
                print(f"- {issue.get('name', 'Untitled')}")
                print(f"  Status: {issue.get('status', 'Unknown')}")
                print(f"  Type: {issue.get('issue_type', 'Unknown')}")
                print()
        else:
            print("No issues directly assigned to 'glind'")
            print("\nChecking all possible assignee formats...")
            # Show sample of assignee fields to understand the structure
            assignees = set()
            for issue in issues[:50]:
                assignee = issue.get('assigned_to')
                if assignee:
                    assignees.add(str(assignee))
            print(f"Sample assignees found: {list(assignees)[:5]}")
else:
    print(f"Error: {response.status_code}")
    print(response.text)
