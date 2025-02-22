import requests
import base64
import os
import re
import logging
import argparse
from datetime import datetime

def setup_logging():
    """Configure logging for the application"""
    logging.basicConfig(
        level=logging.DEBUG,  # Changed to DEBUG for more detailed logging
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("portfolio_generator.log"),
            logging.StreamHandler()
        ]
    )
def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Generate a portfolio report from GitHub repositories.")
    parser.add_argument("--username", required=True, help="GitHub username")
    parser.add_argument("--token", required=True, help="GitHub access token")
    parser.add_argument("--dry-run", action="store_true", help="Run in dry-run mode without writing to Portfolio.md")
    return parser.parse_args()

def get_github_headers(access_token):
    """Generate headers for GitHub API requests"""
    return {
        'Authorization': f'token {access_token}',
        'Accept': 'application/vnd.github.v3+json'
    }

def correct_github_readme_image_links_extended(repo_readme, github_username, repo_name, branch="main"):
    """
    Corrects LOCAL image references in both Markdown and HTML <img> tags
    in a GitHub README to raw GitHubusercontent URLs.  Handles paths with and without './' prefix,
    and now EXCLUDES already absolute URLs in HTML <img> tags.

    Args:
        repo_readme (str): The content of the README file as a string.
        github_username (str): Your GitHub username.
        repo_name (str): The repository name.
        branch (str): The branch name where images are located (default: "main").

    Returns:
        str: The corrected README content with updated image links.
    """

    corrected_readme = repo_readme

    # 1. Correct Markdown image links (no changes needed here):
    corrected_readme = re.sub(
        r"!\[(.*?)\]\(\.\/(.*?)\)",
        rf"![\1](https://raw.githubusercontent.com/{github_username}/{repo_name}/{branch}/\2)",
        corrected_readme
    )

    # 2. Correct HTML <img> tag src attributes, ONLY for LOCAL paths:
    if "src=\"" in corrected_readme: # Check if HTML <img> tags might be present
        corrected_readme = re.sub(
            r'<img.*?src="(?!https?:\/\/)(\.\/)?(.*?)"',  # Regex to find HTML <img> tags with LOCAL src paths (not starting with http:// or https://)
            rf'<img src="https://raw.githubusercontent.com/{github_username}/{repo_name}/{branch}/\2"', # Replacement with raw GitHub URL
            corrected_readme
        )

    return corrected_readme

def setup_output_file(dry_run=False):
    """Set up the output file with timestamped name"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"Portfolio_{timestamp}.md"
    
    if not dry_run and os.path.exists(output_filename):
        os.rename(output_filename, f"Portfolio_old_{timestamp}.md")
    
    if dry_run:
        logging.info("Running in dry-run mode. No changes will be written to file.")
        return open(os.devnull, 'w')  # Write to null device
    
    logging.info(f"Writing output to {output_filename}")
    return open(output_filename, "w+")

def get_branch_selection():
    """Prompt user for branch selection mode"""
    branch_mode = input("Use 'main' branch for all repositories? (y/n): ").lower()
    if branch_mode == 'y':
        logging.info("Using 'main' branch for all repositories")
        return "main"
    logging.info("You'll be prompted for branch for each repository")
    return None
def process_repositories(username, access_token, portfolio_file, default_branch=None):
    """Process all repositories for the given user"""
    headers = get_github_headers(access_token)
    repos_url = f"https://api.github.com/users/{username}/repos"
    all_repos = []
    page = 1
    
    try:
        while True:
            params = {'page': page, 'per_page': 100}
            repos_response = requests.get(repos_url, headers=headers, params=params, timeout=10)
            repos_response.raise_for_status()
            
            if repos_response.status_code == 401:  # Unauthorized
                logging.error("Invalid GitHub access token. Please check your token and try again.")
                return
                
            repos = repos_response.json()
            if not repos:
                break
                
            all_repos.extend(repos)
            page += 1
            
            # Debug logging
            logging.debug(f"Fetched page {page-1} with {len(repos)} repositories")
            
        repos = all_repos
        
        if not repos:
            logging.info(f"No public repositories found for user '{username}'.")
            return
        
        total_repos = len(repos)
        processed_repos = 0
        
        for repo in repos:
            # Debug logging for repository info
            logging.debug(f"Processing repo: {repo['name']} - Private: {repo['private']} - Fork: {repo['fork']}")
            
            # Debug logging for repository info
            logging.debug(f"Processing repo: {repo['name']} - Private: {repo['private']} - Fork: {repo['fork']} - Archived: {repo.get('archived', False)}")
            
            if repo['private']:
                logging.info(f"Skipping private repository: {repo['name']}")
                continue
                
            if repo.get('archived', False):
                logging.info(f"Skipping archived repository: {repo['name']}")
                continue
                
            processed_repos += 1
            repo_name = repo['name']
            logging.info(f"Processing repository {processed_repos}/{total_repos}: {repo_name}")
            portfolio_file.write(f"\nRepository: {repo_name}\n")
            
            process_repository(username, repo_name, headers, portfolio_file, default_branch)
            
        logging.info(f"Summary: Processed {processed_repos} repositories out of {total_repos} total.")
        
    except requests.exceptions.HTTPError as http_err:
        if repos_response.status_code == 404:
            logging.error(f"User '{username}' not found.")
        else:
            logging.error(f"HTTP error occurred: {http_err}")
    except Exception as err:
        logging.error(f"An error occurred: {err}")

def process_repository(username, repo_name, headers, portfolio_file, default_branch=None):
    """Process a single repository"""
    logging.debug(f"Attempting to process repository: {repo_name}")
    readme_url = f"https://api.github.com/repos/{username}/{repo_name}/readme"
    logging.debug(f"README URL: {readme_url}")
    
    try:
        readme_response = requests.get(readme_url, headers=headers)
        logging.debug(f"README response status: {readme_response.status_code}")
        readme_response.raise_for_status()
        readme_data = readme_response.json()
        logging.debug(f"README data retrieved successfully for {repo_name}")
        
        encoded_content = readme_data['content']
        readme_content = base64.b64decode(encoded_content).decode('utf-8')
        
        branch = default_branch
        if branch is None:
            branch = input(f"Enter branch name for {repo_name} (default: main): ") or "main"
            
        readme_content_images = correct_github_readme_image_links_extended(
            readme_content, username, repo_name, branch)
        portfolio_file.write(f'\n{readme_content_images}\n')
        
    except requests.exceptions.HTTPError as http_err:
        if readme_response.status_code == 404:
            logging.info("No README.md found.")
        else:
            logging.error(f"HTTP error occurred: {http_err}")
    except Exception as err:
        logging.error(f"An error occurred: {err}")

def main():
    """Main function to execute the portfolio generation"""
    setup_logging()
    args = parse_arguments()
    
    default_branch = get_branch_selection()
    portfolio_file = setup_output_file(args.dry_run)
    
    process_repositories(args.username, args.token, portfolio_file, default_branch)
    portfolio_file.close()

if __name__ == "__main__":
    main()
