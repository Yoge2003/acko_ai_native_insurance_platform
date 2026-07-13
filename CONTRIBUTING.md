# Contributing Guidelines

We welcome contributions to the ACKO AI Native Insurance Platform. Please follow these guidelines:

---

## 🌲 1. Branch Strategy & PR Procedures

1. **Active Branches**:
   * All active development occurs on the `develop` branch.
   * `main` is reserved exclusively for stable releases.
2. **Process**:
   * Fork the repository and create your feature branch: `git checkout -b feature/awesome-feature`
   * Implement changes conforming to class architectures.
   * Verify all integration and unit tests pass locally before committing.
   * Submit your Pull Request against `develop`.

---

## 🎨 2. Code Standards

* **PEP 8 Linting**: Run `flake8` or `black` to format files before submitting a PR.
* **Docstrings**: Document all python modules, classes, and methods using Google style.
* **Type Hints**: Parameter list variables and return values must contain strict type hints.

---

## 🧪 3. Running Verification Suite

Before submitting a Pull Request, ensure that all tests pass:
```bash
python run_tests.py
```
PRs that break existing integration or unit tests will be rejected.
