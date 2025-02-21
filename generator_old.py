from github import Github, UnknownObjectException
import re

# Replace with your GitHub username and personal access token
github_username = "Clod"
github_token = ""


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

g = Github(github_token)
user = g.get_user(github_username)
rawRepos = user.get_repos()
printableRepos = []

project_categories = {} # You could categorize projects if you want

print("Fetching repositories one by one...")

with open("Portfolio.md", "w+") as portfolio_file:
    for repo in rawRepos:
        # if repo.fork: # Skip forked repositories
        #     continue
        user.get_repos()
        repo_name = repo.name
        print(f"Fetching {repo_name}...")
        repo_description = repo.description if repo.description else "No description provided."
        repo_url = repo.html_url
        try:
            repo_readme = repo.get_readme().decoded_content.decode('utf-8')
            # Correct image links in README in case they point to local files
            # repo_readme = correct_github_readme_image_links_extended(repo_readme, github_username, repo_name)
        except UnknownObjectException:
            repo_readme = "No README found."
        # Get repository's language
        repo_language = repo.language
        print(f"Language: {repo_language}")
        if (repo_language == "Python" or repo_language == "Jupyter Notebook"):
            repo_language = "Python / Jupyter Notebook"
        
        project = {
            'title': repo_name,
            'description': repo_description,
            'url': repo_url,
            'readme': repo_readme,
            'language': repo_language
        }
        
        printableRepos.append(project) 
        
        output_content = ''
        output_content += f"<center><h1 style='color: #0000FF;'>{project['language']}</h1></center>\n\n"
        output_content += f"{project['readme']}\n\n"
        output_content += f"### Located at: [{project['title']}]({project['url']})\n"
        output_content += "---\n"
        output_content += "---\n"
        output_content += "---\n"
        output_content += "---\n"
        output_content += f"\n"
        
        # Write to file
        portfolio_file.write(output_content)
        print(f"Wrote {project['title']} to Portfolio.md")

# print(printableRepos)

print("Starting to write to Portfolio.md")

# Order repos by language
# printableRepos.sort(key=lambda x: x['language'])

# readme_content = "# My GitHub Project Index\n\nWelcome! This is an index of my public GitHub projects.\n\n"

# for project in printableRepos:
#     readme_content += f"<center><h1 style='color: #0000FF;'>{project['language']}</h1></center>\n\n"
#     print(f"Writing {project['title']}")
#     readme_content += f"{project['readme']}\n\n"
#     readme_content += f"### Located at: [{project['title']}]({project['url']})\n"
#     readme_content += "---\n"
#     readme_content += "---\n"
#     readme_content += "---\n"
#     readme_content += "---\n"
#     readme_content += f"\n"
    
# print("**********************Last updated: [Script run date - you can add this dynamically]")
# readme_content += "\n---\n*********************Last updated: [Script run date - you can add this dynamically]*\n"

# # Save to README.md
# with open("Portfolio.txt", "w") as readme_file:
#     readme_file.write(readme_content)

print("Portfolio.md generated successfully!")
