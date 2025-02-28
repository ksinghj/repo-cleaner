#!/usr/bin/env python3
"""
GitHub Repository Cleaner

A tool to help you delete multiple GitHub repositories with a simple checklist interface.
"""

import os
import sys
import time
import getpass
import requests
from typing import List, Dict, Any
import questionary
from questionary.prompts.checkbox import Separator
from rich.console import Console
from rich.progress import Progress, TextColumn, BarColumn, SpinnerColumn
from rich import print as rprint

console = Console()

# GitHub API base URL
GITHUB_API_URL = "https://api.github.com"


def get_github_token() -> str:
    """
    Get the GitHub personal access token from environment or user input.
    """
    token = os.environ.get("GITHUB_TOKEN")
    
    if not token:
        console.print("\n[bold yellow]GitHub Personal Access Token not found in environment.[/bold yellow]")
        console.print("You need a token with 'delete_repo' scope.")
        console.print("Get one at: https://github.com/settings/tokens/new")
        token = getpass.getpass("Enter your GitHub Personal Access Token: ")
    
    return token


def get_user_info(token: str) -> Dict[str, Any]:
    """
    Get user information from GitHub API.
    """
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        response = requests.get(f"{GITHUB_API_URL}/user", headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error authenticating with GitHub:[/bold red] {str(e)}")
        sys.exit(1)


def get_repositories(token: str, username: str) -> List[Dict[str, Any]]:
    """
    Get all repositories for the authenticated user.
    """
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    repositories = []
    page = 1
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]Fetching repositories...[/bold blue]"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    ) as progress:
        fetch_task = progress.add_task("Downloading", total=None)
        
        while True:
            try:
                response = requests.get(
                    f"{GITHUB_API_URL}/user/repos",
                    headers=headers,
                    params={"per_page": 100, "page": page, "sort": "updated"}
                )
                response.raise_for_status()
                repos_page = response.json()
                
                if not repos_page:
                    break
                    
                repositories.extend(repos_page)
                page += 1
                
                # Update progress
                progress.update(fetch_task, total=len(repositories) + 100, completed=len(repositories))
                
            except requests.exceptions.RequestException as e:
                console.print(f"[bold red]Error fetching repositories:[/bold red] {str(e)}")
                return repositories
    
    return repositories


def delete_repository(token: str, owner: str, repo: str) -> bool:
    """
    Delete a single repository.
    """
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        response = requests.delete(
            f"{GITHUB_API_URL}/repos/{owner}/{repo}",
            headers=headers
        )
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error deleting {owner}/{repo}:[/bold red] {str(e)}")
        return False


def main():
    console.print("[bold green]GitHub Repository Cleaner[/bold green]")
    console.print("This tool helps you delete multiple GitHub repositories at once.\n")
    
    # Get GitHub token and authenticate
    token = get_github_token()
    
    # Get user info
    user_info = get_user_info(token)
    username = user_info["login"]
    
    console.print(f"[bold green]Successfully authenticated as:[/bold green] {username}")
    
    # Get repositories
    repositories = get_repositories(token, username)
    
    if not repositories:
        console.print("[bold yellow]No repositories found.[/bold yellow]")
        return
    
    console.print(f"[bold green]Found {len(repositories)} repositories.[/bold green]")
    
    # Create repository choices for the checklist
    repo_choices = [
        {
            "name": f"{repo['name']} ({repo['description'] or 'No description'}) - Last updated: {repo['updated_at'][:10]}",
            "value": repo['name'],
            "checked": False
        }
        for repo in repositories
    ]
    
    # Add a separator at the top with instructions
    repo_choices.insert(0, Separator(" Use SPACE to toggle selection "))
    
    # Show repository selection checklist with simplified instructions
    selected_repos = questionary.checkbox(
        "Select repositories to delete:",
        choices=repo_choices,
        instruction="Press SPACE to toggle selection"
    ).ask()
    
    if not selected_repos:
        console.print("[bold yellow]No repositories selected for deletion.[/bold yellow]")
        return
    
    # Confirm deletion
    console.print("[bold red]WARNING: This action cannot be undone![/bold red]")
    confirm = questionary.confirm(
        f"Are you sure you want to delete {len(selected_repos)} repositories?",
        default=False
    ).ask()
    
    if not confirm:
        console.print("[bold yellow]Operation cancelled.[/bold yellow]")
        return
    
    # Delete selected repositories
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold red]Deleting repositories...[/bold red]"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    ) as progress:
        delete_task = progress.add_task("Deleting", total=len(selected_repos))
        
        for repo_name in selected_repos:
            success = delete_repository(token, username, repo_name)
            
            # Small delay to avoid API rate limits
            time.sleep(0.5)
            
            progress.update(delete_task, advance=1)
    
    console.print("[bold green]Operation completed successfully![/bold green]")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Operation cancelled by user.[/bold yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred:[/bold red] {str(e)}")
        sys.exit(1)