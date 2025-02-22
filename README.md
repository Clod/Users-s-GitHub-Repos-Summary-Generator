# Portfolio Report Generator

This script generates a portfolio report from your GitHub repositories.

## Features
- Processes public repositories
- Corrects image links in README files
- Supports multiple branches
- Dry-run mode for testing
- Progress tracking

## Usage

```bash
python portfolio_report_generator.py --username YOUR_GITHUB_USERNAME --token YOUR_GITHUB_TOKEN [--dry-run]
```

## Requirements
- Python 3.x
- requests library

## Configuration
Create a `config.ini` file with your GitHub credentials:

```ini
[GITHUB]
username = your_username
token = your_token
```

## Logging
All operations are logged to `portfolio_generator.log`.
