# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the ASAI X Bot, a Python application that monitors X (Twitter) for posts with the `#浅井恋乃未` hashtag and automatically forwards them to Discord. The bot runs once daily at 9 AM JST via Cloud Scheduler on Google Cloud Run.

## Development Environment

### Python Environment
**CRITICAL**: Always use the conda environment `asai` for all Python operations.

```bash
# Activate conda environment before any Python commands
conda activate asai

# Verify correct environment
echo $CONDA_DEFAULT_ENV  # should show "asai"
```

### Setup Commands
```bash
# Initial setup (creates conda environment and installs dependencies)
./setup_conda.sh

# Manual setup alternative
conda create -n asai python=3.12 -y
conda activate asai
pip install -r requirements.txt
```

## Common Development Commands

### Local Execution
```bash
conda activate asai
cd src && python run.py
```

### Testing
```bash
# Run all tests with coverage
make test
# or
pytest tests/ --cov=src --cov-report=term-missing

# Fast tests without coverage
make test-fast
# or
pytest tests/ -v

# Run specific test file
pytest tests/test_main.py -v
```

### Code Quality
```bash
# Format code (auto-fix)
make format
# or
ruff format src/ tests/ && ruff check --fix src/ tests/

# Lint without auto-fix
make lint
# or
ruff check src tests

# Security check
make security
# or
bandit -r src/ && safety check

# Type checking
make type-check
# or
ruff check --select=F,E9,W6 src tests

# Run all quality checks
make all
```

## Code Architecture

### Entry Points
- **src/run.py**: Direct execution script for local development
- **src/server.py**: HTTP server for Cloud Run (port 8080)

### Core Application Flow
1. **src/main.py**: Main orchestration logic
   - `fetch_and_forward()`: Core processing function
   - Handles X API fetching, processing, and Discord forwarding
2. **src/config.py**: Environment validation, logging setup, API configuration
3. **src/x_api_client.py**: X API client (`fetch_tweets()`)
4. **src/discord_client.py**: Discord webhook client (`discord_post()`, `get_tweet_url()`)
5. **src/utils.py**: State management and utilities
   - `load_since_id()` / `save_since_id()`: Prevents duplicate processing
   - `build_index()`: Creates lookup indexes for users/media

### State Management
- **Cloud Run**: Uses Google Secret Manager (`asai-x-bot-since-id`)
- **Local**: Uses file `since_id.txt`
- Auto-fallback mechanism for environment portability

### Environment Detection
- Cloud Run environment detected via `K_SERVICE` environment variable
- Same codebase works in both local and cloud environments

## Configuration

### Required Environment Variables
```bash
X_BEARER_TOKEN=your_bearer_token
DISCORD_WEBHOOK_URL=your_webhook_url
QUERY=(#浅井恋乃未) (from:sakurazaka46 OR from:sakura_joqr OR from:anan_mag OR from:Lemino_official)
```

### Optional Environment Variables
```bash
GOOGLE_CLOUD_PROJECT=your_project_id    # For Cloud Run
SINCE_ID_FILE=since_id.txt              # Local state file path
PORT=8080                               # HTTP server port
```

### Setup Configuration
```bash
# Copy and edit environment file
cp example.env .env
# Edit .env with your values
```

## Deployment

### Local Development
Use conda environment and direct execution:
```bash
conda activate asai
cd src && python run.py
```

### Cloud Run Deployment
```bash
# Automated deployment
export PROJECT_ID="your-gcp-project-id"
export REGION="asia-northeast1"
./deploy-cloud-run.sh
```

## Code Style and Tools

### Linting/Formatting
- **Tool**: ruff (unified linting and formatting)
- **Line length**: 127 characters
- **Python version**: 3.12+
- **Quote style**: double quotes

### Security
- **Tool**: bandit for security scanning
- API keys stored in Secret Manager (Cloud) or .env (local)
- No credentials logged or committed

### Testing
- **Framework**: pytest
- **Coverage target**: 83%+ (currently achieved)
- **Mock strategy**: External dependencies (X API, Discord) are mocked
- All core modules have comprehensive test coverage

## Data Processing Flow

1. **Environment validation**: Check required API keys and configuration
2. **State loading**: Read last processed tweet ID from Secret Manager or file
3. **X API query**: Fetch new tweets using `since_id` parameter to avoid duplicates
4. **Data indexing**: Create lookup indexes for users and media
5. **Processing**: Sort tweets chronologically, extract URLs
6. **Discord forwarding**: Send tweet URLs to Discord webhook
7. **State persistence**: Save highest tweet ID for next execution

## Monitoring Query

The bot monitors this X API search query:
```
(#浅井恋乃未) (from:sakurazaka46 OR from:sakura_joqr OR from:anan_mag OR from:Lemino_official)
```

## File Structure Notes

- **Dockerfile**: Container configuration for Cloud Run
- **deploy-cloud-run.sh**: Automated GCP deployment script
- **Makefile**: Development task automation
- **pyproject.toml**: Ruff configuration and project metadata
- **TESTING.md**: Detailed testing documentation
- **.cursor/rules/**: IDE-specific development guidelines