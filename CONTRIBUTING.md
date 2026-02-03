# 👥 Team Collaboration Guide

Guidelines for team members working on CropSense.

---

## 📋 Before You Start

1. Read [README.md](README.md) - Project overview
2. Read [SETUP.md](SETUP.md) - Installation guide
3. Understand project structure
4. Get OpenWeatherMap API key

---

## 🌿 Git Branching Strategy

We use a simple branching model:

```
main (stable, production-ready)
 ├── feature/model-optimization
 ├── feature/web-interface
 ├── feature/api-endpoint
 └── bugfix/performance-issue
```

### Branch Naming

- `feature/description` - New features
- `bugfix/description` - Bug fixes
- `docs/description` - Documentation
- `refactor/description` - Code improvements
- `hotfix/critical-issue` - Urgent fixes

---

## 📝 Workflow Steps

### 1. Create Feature Branch

```bash
# Update main first
git pull origin main

# Create and checkout new branch
git checkout -b feature/your-feature-name

# Verify you're on new branch (should show your branch name)
git branch
```

### 2. Make Changes

```bash
# Edit files
# Create new files
# Delete old files

# View changes
git status
```

### 3. Test Your Changes

```bash
# Run tests
python test_integration.py

# Run interactive test
python interactive_test.py

# If you added dependencies:
pip freeze > requirements.txt
git add requirements.txt
```

### 4. Commit Changes

```bash
# Stage all changes
git add .

# Or stage specific files
git add src/models/train_rf.py
git add requirements.txt

# Commit with descriptive message
git commit -m "Add Random Forest model optimization"

# See commit history
git log --oneline
```

### 5. Push to GitHub

```bash
# Push your branch
git push origin feature/your-feature-name

# Verify it's on GitHub by visiting:
# https://github.com/yourusername/cropsense
```

### 6. Create Pull Request (PR)

On GitHub:

1. Go to your repository
2. Click "Compare & pull request" button
3. Add title: "Add Random Forest optimization"
4. Add description:
   ```
   ## Changes
   - Optimized RF model hyperparameters
   - Improved accuracy from 99.50% to 99.55%
   
   ## Testing
   - Ran test_integration.py ✅
   - Ran interactive_test.py ✅
   
   ## Related Issues
   Closes #123
   ```
5. Click "Create pull request"

### 7. Code Review & Merge

- Team members review your code
- Respond to feedback
- Make requested changes:
  ```bash
  # Make changes
  git add .
  git commit -m "Address review feedback"
  git push origin feature/your-feature-name
  ```
- Once approved, merge to main
- Delete feature branch

---

## 📋 Commit Message Guidelines

### Good Commit Messages

✅ **Good:**
```
Add weather API integration

- Integrate OpenWeatherMap API
- Handle API errors gracefully
- Add mock mode for testing
- Tests: test_integration.py passes
```

✅ **Also Good:**
```
Fix ensemble model accuracy issue
```

### Bad Commit Messages

❌ **Bad:**
```
fixed stuff
```

❌ **Also Bad:**
```
asdf
```

### Format

```
<type>: <subject>

<body>

<footer>
```

**Types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `style:` - Code style (no logic change)
- `refactor:` - Code restructuring
- `test:` - Adding tests
- `chore:` - Maintenance

**Examples:**
```
feat: Add crop cycle duration feature

docs: Update README with API setup

fix: Handle missing .env file gracefully

refactor: Simplify ensemble prediction logic
```

---

## 🚀 Common Workflows

### Adding a New Feature

```bash
git checkout -b feature/new-feature
# Make changes
# Test: python interactive_test.py
git add .
git commit -m "feat: Add new feature"
git push origin feature/new-feature
# Create PR on GitHub
```

### Fixing a Bug

```bash
git checkout -b bugfix/issue-description
# Fix the bug
# Test: python test_integration.py
git add .
git commit -m "fix: Resolve issue"
git push origin bugfix/issue-description
# Create PR on GitHub
```

### Updating Documentation

```bash
git checkout -b docs/update-readme
# Edit README.md or other docs
git add docs/
git commit -m "docs: Update installation instructions"
git push origin docs/update-readme
# Create PR
```

### Syncing with Main

```bash
# Fetch latest changes
git fetch origin

# Rebase your branch on main
git rebase origin/main

# If conflicts occur, resolve them manually
# Then continue rebase
git rebase --continue

# Force push your rebased branch
git push origin feature/your-feature --force-with-lease
```

---

## ⚠️ Important Rules

### DO ✅

- ✅ Create feature branch for each change
- ✅ Write descriptive commit messages
- ✅ Test before pushing
- ✅ Pull latest before starting work
- ✅ Use `.env` for API keys
- ✅ Add to `.gitignore` for sensitive files
- ✅ Update `requirements.txt` after `pip install`
- ✅ Review your own code before PR

### DO NOT ❌

- ❌ Commit to `main` directly
- ❌ Commit `.env` file
- ❌ Commit `*.pkl` model files
- ❌ Commit `__pycache__` directories
- ❌ Force push to main
- ❌ Commit incomplete code
- ❌ Use vague commit messages
- ❌ Ignore failing tests

---

## 🔀 Resolving Conflicts

If you get merge conflicts:

```bash
# Update your branch
git fetch origin
git rebase origin/main

# See conflicting files
git status

# Open conflicting files and manually resolve
# Markers: <<<<<<<, =======, >>>>>>>

# After fixing
git add .
git rebase --continue
git push origin feature/your-feature --force-with-lease
```

---

## 🛑 Undoing Changes

### Undo Last Commit (not pushed)

```bash
git reset --soft HEAD~1
```

### Undo Last Commit (already pushed)

```bash
git revert HEAD
git push origin feature/your-feature
```

### Discard Local Changes

```bash
git checkout -- filename.py
```

### Reset Branch to Main

```bash
git fetch origin
git reset --hard origin/main
```

---

## 📊 Code Quality Checklist

Before creating PR, ensure:

- [ ] Code follows project style
- [ ] No hardcoded values
- [ ] No unused imports
- [ ] Docstrings for functions
- [ ] Comments for complex logic
- [ ] Tests pass
- [ ] No API keys or secrets
- [ ] `.env` in .gitignore
- [ ] `.pkl` files in .gitignore
- [ ] Commit message is descriptive

---

## 🐛 Reporting Issues

When reporting bugs:

```markdown
## Description
What's the issue?

## Steps to Reproduce
1. ...
2. ...
3. ...

## Expected Behavior
What should happen?

## Actual Behavior
What actually happened?

## Environment
- OS: Windows 10 / macOS 12 / Ubuntu 20.04
- Python: 3.9.x
- Error message: (paste exact error)

## Screenshots
(if applicable)
```

---

## ✨ Feature Requests

When suggesting features:

```markdown
## Title
Brief description

## Problem
What problem does this solve?

## Proposed Solution
How should it work?

## Benefits
Why is this useful?

## Example Usage
```python
# How would you use it?
recommender.new_feature()
```
```

---

## 📚 Reference

| Command | Purpose |
|---------|---------|
| `git status` | Check current state |
| `git log --oneline` | View commit history |
| `git diff` | See changes in files |
| `git branch` | List all branches |
| `git fetch` | Get latest from server |
| `git pull` | Fetch + merge from server |
| `git push` | Send commits to server |
| `git merge` | Combine branches |
| `git rebase` | Reapply commits on top |
| `git stash` | Temporarily save changes |

---

## 🆘 Need Help?

1. Check existing GitHub Issues
2. Ask in discussions/comments
3. Create new issue with details
4. Ask team members

---

**Last Updated:** February 3, 2026  
**Happy Contributing!** 🚀
