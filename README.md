# Portfolio Report Generator

This script generates a professional portfolio report from your GitHub repositories, combining all your public repository READMEs into a single Markdown file.

## Features
- Processes public repositories
- Corrects image links in README files to use raw GitHub URLs
- Supports multiple branches (main or custom per repository)
- Dry-run mode for testing without file changes
- Progress tracking with repository counts
- Automatic handling of repository pagination
- Detailed logging for debugging
- Token validation and permission checking
- Horizontal separators between repository sections

## Requirements
- Python 3.8+
- requests library (install via `pip install requests`)
- GitHub Personal Access Token with `repo` scope

## GitHub Token Requirements
Your GitHub token must:
1. Start with `ghp_`
2. Be exactly 40 characters long
3. Have the `repo` scope enabled
4. Not be expired

To create a token:
1. Go to GitHub > Settings > Developer settings > Personal access tokens
2. Click "Generate new token"
3. Select the `repo` scope
4. Copy the token (you won't be able to see it again)

## Usage

Basic usage:
```bash
python portfolio_report_generator.py --username YOUR_GITHUB_USERNAME --token YOUR_GITHUB_TOKEN
```

Dry-run mode (test without writing files):
```bash
python portfolio_report_generator.py --username YOUR_GITHUB_USERNAME --token YOUR_GITHUB_TOKEN --dry-run
```

## Output
- Portfolio_<timestamp>.md - The generated portfolio file
- portfolio_generator_<timestamp>.log - Detailed operation log
- Portfolio_old_<timestamp>.md - Backup of previous portfolio (if exists)

## Error Handling
The script handles common errors including:
- Invalid token format/length
- Missing README files
- Private repositories (skipped)
- Archived repositories (skipped)
- HTTP errors with detailed logging
- Token permission verification

## Logging
All operations are logged to `portfolio_generator_<timestamp>.log` with:
- Timestamps
- Error details
- Repository processing status
- Token verification results
- Progress tracking

## Example Output Structure
```markdown
Repository: repo1

[README content with corrected image links]

---

Repository: repo2

[README content with corrected image links]

---
```

## Development
To install development requirements:
```bash
pip install -r requirements.txt
```
