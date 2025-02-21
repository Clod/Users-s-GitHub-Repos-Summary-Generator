import requests

# Prompt for the GitHub username
# username = input("Enter the GitHub username: ")
username = "Clod"

# GitHub API URL to fetch user repositories
repos_url = f"https://api.github.com/users/{username}/repos"

headers = {'Authorization': 'token '}
repos_response = requests.get(repos_url, headers=headers)

try:
    # Fetch the list of repositories
    # repos_response = requests.get(repos_url)
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

            # Construct the URL to fetch the README
            readme_url = f"https://api.github.com/repos/{username}/{repo_name}/readme"

            try:
                # Fetch the README file
                readme_response = requests.get(readme_url)
                readme_response.raise_for_status()
                readme_data = readme_response.json()

                # The content is base64 encoded
                readme_content = requests.utils.unquote(readme_data['content'])
                print("README.md content:\n")
                print(readme_content)
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
