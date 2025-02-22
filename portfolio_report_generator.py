import requests
import base64, os, re
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("portfolio_generator.log"),
        logging.StreamHandler()
    ]
)
import argparse

# Set up argument parser
parser = argparse.ArgumentParser(description="Generate a portfolio report from GitHub repositories.")
parser.add_argument("--username", required=True, help="GitHub username")
parser.add_argument("--token", required=True, help="GitHub access token")
args = parser.parse_args()

username = args.username
access_token = args.token

# GitHub API URL to fetch user repositories
repos_url = f"https://api.github.com/users/{username}/repos"

# Headers with authentication
headers = {
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

# Add dry run argument
parser.add_argument("--dry-run", action="store_true", help="Run in dry-run mode without writing to Portfolio.md")

# If not dry run and Portfolio.md exists, rename it
if not args.dry_run and os.path.exists("Portfolio.md"):
    os.rename("Portfolio.md", "Portfolio_old.md")

if args.dry_run:
    print("Running in dry-run mode. No changes will be written to Portfolio.md.")
    portfolio_file = open(os.devnull, 'w')  # Write to null device
else:
    portfolio_file = open("Portfolio.md", "w+")
    try:
        # Fetch the list of repositories
        repos_response = requests.get(repos_url, headers=headers, timeout=10)
        repos_response.raise_for_status()  # Raise an exception for HTTP errors
        
        if repos_response.status_code == 401:  # Unauthorized
            print("Error: Invalid GitHub access token. Please check your token and try again.")
            exit(1)
            
        repos = repos_response.json()

        if not repos:
            print(f"No public repositories found for user '{username}'.")
        else:
            total_repos = len(repos)
            processed_repos = 0
            # Iterate over each repository
            for repo in repos:
                if repo['private']:
                    print(f"Skipping private repository: {repo['name']}")
                    continue
                    
                processed_repos += 1
                repo_name = repo['name']
                print(f"\nProcessing repository {processed_repos}/{total_repos}: {repo_name}")
                portfolio_file.write(f"\nRepository: {repo_name}\n")
                # Construct the URL to fetch the README
                readme_url = f"https://api.github.com/repos/{username}/{repo_name}/readme"

                try:
                    # Fetch the README file
                    readme_response = requests.get(readme_url, headers=headers)
                    readme_response.raise_for_status()
                    readme_data = readme_response.json()

                    # The content is base64 encoded
                    encoded_content = readme_data['content']
                    # Decode the base64 content
                    readme_content = base64.b64decode(encoded_content).decode('utf-8')
                    print("README.md content:\n")
                    # print(readme_content)
                    # portfolio_file.write(f'\n{readme_content}\n')
                    branch = input(f"Enter branch name for {repo_name} (default: main): ") or "main"
                    readme_content_images = correct_github_readme_image_links_extended(readme_content, username, repo_name, branch)
                    portfolio_file.write(f'\n{readme_content_images}\n')
                except requests.exceptions.HTTPError as http_err:
                    if readme_response.status_code == 404:
                        print("No README.md found.")
                    else:
                        print(f"HTTP error occurred: {http_err}")
                except Exception as err:
                    print(f"An error occurred: {err}")
    except requests.exceptions.HTTPError as http_err:
        if repos_response.status_code == 404:
            print(f"User '{username}' not found.")
        else:
            print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")
    
    print(f"\nSummary: Processed {processed_repos} repositories out of {total_repos} total.")
