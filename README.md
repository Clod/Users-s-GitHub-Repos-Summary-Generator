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


## Logging
All operations are logged to `portfolio_generator_<timestamp>.log`.
