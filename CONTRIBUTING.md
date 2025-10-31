# Contributing to Multimodal RAG System

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## 🤝 Code of Conduct

This project adheres to a Code of Conduct that all contributors are expected to follow. Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Docker & Docker Compose
- Git
- Tesseract OCR

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/multimodal-rag.git
   cd multimodal-rag
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -e .  # Install in editable mode
   ```

4. **Install pre-commit hooks**
   ```bash
   pre-commit install
   ```

5. **Set up environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

6. **Start development services**
   ```bash
   docker-compose up -d qdrant mongo redis
   ```

7. **Run tests**
   ```bash
   pytest tests/ -v
   ```

## 📝 Development Workflow

### Branch Strategy

- `main` - Production-ready code
- `develop` - Integration branch for features
- `feature/*` - Feature branches
- `bugfix/*` - Bug fix branches
- `hotfix/*` - Urgent fixes for production

### Making Changes

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write code following our style guide
   - Add tests for new functionality
   - Update documentation as needed

3. **Run quality checks**
   ```bash
   make lint      # Run linters
   make format    # Format code
   make test      # Run tests
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

   **Commit Message Format:**
   ```
   <type>: <description>

   [optional body]

   [optional footer]
   ```

   **Types:**
   - `feat`: New feature
   - `fix`: Bug fix
   - `docs`: Documentation changes
   - `style`: Code style changes (formatting, etc.)
   - `refactor`: Code refactoring
   - `test`: Adding or updating tests
   - `chore`: Maintenance tasks

5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request**
   - Go to the original repository
   - Click "New Pull Request"
   - Select your branch
   - Fill out the PR template

## 🎨 Code Style

### Python Style Guide

We follow PEP 8 with some modifications:

- **Line length**: 100 characters
- **Formatting**: Black (automatic)
- **Import sorting**: isort
- **Linting**: flake8
- **Type checking**: mypy

### Code Quality Tools

```bash
# Format code
black src/ tests/
isort src/ tests/

# Check linting
flake8 src/ tests/ --max-line-length=100

# Type checking
mypy src/ --ignore-missing-imports
```

### Docstrings

Use Google-style docstrings:

```python
def function_name(arg1: str, arg2: int) -> bool:
    """
    Brief description of the function.

    More detailed description if needed.

    Args:
        arg1: Description of arg1
        arg2: Description of arg2

    Returns:
        Description of return value

    Raises:
        ValueError: When something goes wrong
    """
    pass
```

## 🧪 Testing

### Running Tests

```bash
# All tests
pytest tests/ -v

# Unit tests only
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# Specific test file
pytest tests/unit/test_embedder.py -v

# With coverage
pytest tests/ --cov=src --cov-report=html
```

### Writing Tests

- Place unit tests in `tests/unit/`
- Place integration tests in `tests/integration/`
- Use descriptive test names
- Follow AAA pattern (Arrange, Act, Assert)

Example:
```python
def test_embedder_creates_correct_dimension():
    # Arrange
    embedder = Embedder(model_name="test-model")
    
    # Act
    embedding = embedder.embed_single("test text")
    
    # Assert
    assert len(embedding) == 384
```

### Test Coverage

- Aim for >80% code coverage
- All new features must include tests
- Critical paths must have integration tests

## 📚 Documentation

### Code Documentation

- All public functions/classes must have docstrings
- Complex logic should have inline comments
- Use type hints for all function signatures

### API Documentation

- API endpoints automatically documented via OpenAPI
- Add clear descriptions to endpoint docstrings
- Include example requests/responses

### README Updates

- Update README.md when adding new features
- Keep examples up to date
- Update configuration documentation

## 🔍 Pull Request Process

### PR Checklist

Before submitting a PR, ensure:

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] Commit messages follow convention
- [ ] No merge conflicts with develop
- [ ] PR description is clear and complete

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How was this tested?

## Checklist
- [ ] Tests pass locally
- [ ] Code follows style guide
- [ ] Documentation updated
- [ ] No breaking changes (or documented)

## Related Issues
Fixes #123
```

### Review Process

1. **Automated checks** must pass (CI/CD)
2. **Code review** by at least one maintainer
3. **Testing** in development environment
4. **Approval** required before merge
5. **Squash and merge** into develop

## 🐛 Reporting Bugs

### Before Submitting

- Check existing issues
- Check documentation
- Try latest version
- Gather reproduction steps

### Bug Report Template

```markdown
**Describe the bug**
Clear description of what the bug is.

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
- OS: [e.g. Ubuntu 22.04]
- Python version: [e.g. 3.10]
- Docker version: [e.g. 24.0.0]

**Additional context**
Any other context about the problem.
```

## 💡 Feature Requests

### Proposing Features

1. **Check existing issues** for similar requests
2. **Open a discussion** before implementation
3. **Provide clear use cases**
4. **Consider scope and complexity**

### Feature Request Template

```markdown
**Feature Description**
Clear and concise description.

**Use Case**
Why is this feature needed?

**Proposed Solution**
How should it work?

**Alternatives Considered**
Other approaches you've considered.

**Additional Context**
Mockups, examples, etc.
```

## 🔐 Security

### Reporting Security Issues

**DO NOT** open public issues for security vulnerabilities.

Instead:
1. Email security@example.com
2. Include description and reproduction steps
3. Wait for response before disclosure

### Security Best Practices

- Never commit API keys or secrets
- Use environment variables for configuration
- Keep dependencies updated
- Follow OWASP guidelines
- Enable security features by default

## 📋 Project Structure

```
multimodal-rag/
├── src/              # Source code
│   ├── api/          # FastAPI application
│   ├── core/         # Core functionality
│   └── workers/      # Background workers
├── tests/            # Test suite
│   ├── unit/         # Unit tests
│   └── integration/  # Integration tests
├── infra/            # Infrastructure configs
├── samples/          # Sample data
└── scripts/          # Utility scripts
```

## 🎯 Priorities

Current focus areas:

1. **Performance optimization**
2. **Test coverage improvement**
3. **Documentation enhancement**
4. **Additional file format support**
5. **Advanced retrieval strategies**

## 📞 Getting Help

- **Documentation**: Check README.md and docs/
- **Discussions**: GitHub Discussions
- **Issues**: GitHub Issues
- **Chat**: [Discord/Slack link]

## 🙏 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Project documentation

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to Multimodal RAG System!** 🚀
