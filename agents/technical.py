"""
agents/technical.py

Technical Agent: Analyzes GitHub repository health.

Design decisions:
- Uses GitHub REST API (free tier, no auth needed for demo)
- Falls back gracefully on rate limits
- Returns structured dict matching Quant Agent format
"""

import requests
from datetime import datetime, timezone


def fetch_commits(owner: str, repo: str, per_page: int = 100) -> list:
    """
    Fetches recent commits from GitHub API.
    
    Returns list of commit dicts.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/commits"
    params = {"per_page": per_page}
    headers = {"Accept": "application/vnd.github.v3+json"}
    
    response = requests.get(url, params=params, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    elif response.status_status_code == 403:
        raise ValueError("GitHub API rate limit exceeded. Try again later or use a token.")
    else:
        raise ValueError(f"GitHub API error: {response.status_code}")


def fetch_repo_info(owner: str, repo: str) -> dict:
    """
    Fetches repository metadata: stars, forks, open issues, etc.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}"
    headers = {"Accept": "application/vnd.github.v3+json"}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise ValueError(f"GitHub API error: {response.status_code}")


def fetch_contributors(owner: str, repo: str) -> list:
    """
    Fetches top contributors.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/contributors"
    headers = {"Accept": "application/vnd.github.v3+json"}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        return []  # Some repos hide contributor data


def calculate_commit_frequency(commits: list) -> float:
    """
    Calculates average commits per week from recent commits.
    
    Logic: Look at dates of commits, calculate time span, divide by commits.
    """
    if not commits or len(commits) < 2:
        return 0.0
    
    # Parse commit dates
    dates = []
    for commit in commits:
        date_str = commit["commit"]["committer"]["date"]
        date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        dates.append(date)
    
    # Sort oldest to newest
    dates.sort()
    
    # Time span in days
    time_span_days = (dates[-1] - dates[0]).days
    
    if time_span_days == 0:
        return len(commits)  # All commits today
    
    # Commits per week
    commits_per_week = (len(commits) / time_span_days) * 7
    
    return round(commits_per_week, 2)


def calculate_days_since_commit(commits: list) -> int:
    """
    Days since the most recent commit.
    """
    if not commits:
        return None
    
    latest_date_str = commits[0]["commit"]["committer"]["date"]
    latest_date = datetime.fromisoformat(latest_date_str.replace("Z", "+00:00"))
    
    now = datetime.now(timezone.utc)
    days = (now - latest_date).days
    
    return days


def calculate_health_score(metrics: dict) -> float:
    """
    Composite health score 0-1 based on multiple factors.
    """
    score = 0.0
    
    # Commit frequency (25%)
    freq = metrics.get("commit_frequency", 0)
    if freq >= 10:
        score += 0.25
    elif freq >= 5:
        score += 0.15
    elif freq >= 1:
        score += 0.05
    
    # Contributors (25%)
    contributors = metrics.get("contributor_count", 0)
    if contributors >= 50:
        score += 0.25
    elif contributors >= 20:
        score += 0.15
    elif contributors >= 5:
        score += 0.05
    
    # Issue resolution (25%)
    resolution = metrics.get("issue_resolution_rate", 0)
    if resolution >= 0.8:
        score += 0.25
    elif resolution >= 0.5:
        score += 0.15
    else:
        score += 0.05
    
    # Activity (25%)
    days_since = metrics.get("days_since_commit", 999)
    if days_since <= 7:
        score += 0.25
    elif days_since <= 30:
        score += 0.15
    elif days_since <= 90:
        score += 0.05
    
    return round(score, 4)


def analyze(repo: str) -> dict:
    """
    Main entry point for Technical Agent.
    
    Args:
        repo: "owner/repo" format, e.g. "bitcoin/bitcoin"
    
    Returns:
        Dict with all metrics, confidence, and status.
    """
    try:
        owner, repo_name = repo.split("/")
    except ValueError:
        return {
            "agent": "technical",
            "repo": repo,
            "metrics": {},
            "confidence": 0.0,
            "status": "failed",
            "error": "Invalid repo format. Use 'owner/repo'."
        }
    
    try:
        # Fetch data
        commits = fetch_commits(owner, repo_name)
        repo_info = fetch_repo_info(owner, repo_name)
        contributors = fetch_contributors(owner, repo_name)
        
        # Calculate metrics
        metrics = {
            "total_commits": len(commits),
            "commit_frequency": calculate_commit_frequency(commits),
            "contributor_count": len(contributors),
            "open_issues": repo_info.get("open_issues_count", 0),
            "issue_resolution_rate": 0.0,  # Need more data for this
            "latest_release": repo_info.get("pushed_at", "unknown"),
            "days_since_commit": calculate_days_since_commit(commits),
        }
        
        # Health score
        metrics["health_score"] = calculate_health_score(metrics)
        
        # Confidence based on data quality
        confidence = 0.85 if len(commits) >= 100 else 0.70 if len(commits) >= 50 else 0.50
        
        return {
            "agent": "technical",
            "repo": repo,
            "metrics": metrics,
            "confidence": confidence,
            "status": "complete",
        }
        
    except Exception as e:
        return {
            "agent": "technical",
            "repo": repo,
            "metrics": {},
            "confidence": 0.0,
            "status": "failed",
            "error": str(e)
        }