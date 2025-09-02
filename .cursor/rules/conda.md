# ASAI X Bot - Cursor Rules

## Conda Environment Check

### Python Command Execution Rules
- **CRITICAL**: Before executing any Python-related commands (python, pip, pytest, mypy, ruff, etc.), ALWAYS verify that the current conda environment is set to "asai"
- If the environment is not "asai", provide clear instructions to activate it first
- Check environment with: `conda info --envs` or `echo $CONDA_DEFAULT_ENV`

### Environment Activation Commands
When conda environment is not "asai", provide these activation steps:
```bash
# Activate the asai conda environment
conda activate asai

# Verify activation
echo "Current environment: $CONDA_DEFAULT_ENV"
```

### Python Development Workflow
1. **Environment Check**: Always verify `asai` environment is active
2. **Dependencies**: Use `pip install -r requirements.txt` within asai environment
3. **Testing**: Run `pytest` with coverage: `pytest tests/ --cov=src --cov-report=term-missing`
4. **Linting**: Use `ruff check src tests` and `mypy src --ignore-missing-imports`
5. **Formatting**: Use `ruff format src/ tests/`

### Makefile Integration
- The project includes a Makefile with predefined commands
- All Makefile targets assume the `asai` environment is active
- Common commands:
  - `make test`: Run tests with coverage
  - `make lint`: Run linting checks
  - `make format`: Format code
  - `make all`: Run all checks and tests

### Interpreter Configuration
- Python interpreter path: `$(conda info --base)/envs/asai/bin/python`
- Use this path when configuring Cursor's Python interpreter
- Access via: Cmd+Shift+P → "Python: Select Interpreter"

### Development Scripts
- Main application: `cd src && python run.py`
- Setup script: `./setup_conda.sh` (creates and configures asai environment)
- Deployment: `./deploy-cloud-run.sh`

### Error Prevention
- Never suggest `python` commands without first checking conda environment
- If user reports Python-related errors, first check if `asai` environment is active
- Provide environment activation instructions before any troubleshooting

### Code Quality Standards
- Line length: 127 characters (configured in pyproject.toml)
- Python version: 3.12
- Type checking: mypy with
