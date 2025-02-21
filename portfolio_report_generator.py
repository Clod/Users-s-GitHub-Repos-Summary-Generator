import requests
import base64, os, re

# Prompt for the GitHub username
username = input("Enter the GitHub username: ")

# Your personal access token (keep this secure)
access_token = input("Enter the GitHub access token: ")

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

# If file Portfolio.md exists, rename it to Portfolio_old.md
if os.path.exists("Portfolio.md"):
    os.rename("Portfolio.md", "Portfolio_old.md")

with open("Portfolio.md", "w+") as portfolio_file:
    try:
        # Fetch the list of repositories
        repos_response = requests.get(repos_url, headers=headers)
        repos_response.raise_for_status()  # Raise an exception for HTTP errors
        repos = repos_response.json()

        if not repos:
            print(f"No public repositories found for user '{username}'.")
        else:
            # Iterate over each repository
            for repo in repos:
                repo_name = repo['name']
                print(f"\nRepository: {repo_name}")
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
                    readme_content_images = correct_github_readme_image_links_extended(readme_content, username, repo_name)
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
