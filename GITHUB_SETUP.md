# 🚀 Push to GitHub - Setup Instructions

Your local Git repository is ready! Now follow these steps to push to GitHub:

## Step 1: Create a GitHub Repository

1. Go to **https://github.com/new**
2. Repository name: `development-leads-finder` (or your preferred name)
3. Description: "AI-powered development opportunity lead finder with Google Sheets integration"
4. Choose **Public** or **Private** (your preference)
5. **DO NOT initialize with README** (we already have one)
6. Click **Create repository**

## Step 2: Copy Your Repository URL

After creating, you'll see a page with your repo URL like:
```
https://github.com/YOUR_USERNAME/development-leads-finder.git
```

## Step 3: Add Remote and Push

Run these commands in your terminal:

```bash
cd /Users/koushikramalingam/Desktop/Anil_Project

# Add GitHub as remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/development-leads-finder.git

# Verify remote was added
git remote -v

# Push to GitHub (first time)
git branch -M main
git push -u origin main
```

## Step 4: Verify on GitHub

- Go to your GitHub repository URL
- You should see all your files there ✅
- Check the README is showing properly

## Future Commits

After this, whenever you make changes:

```bash
# Commit your changes
git add .
git commit -m "Description of what changed"

# Push to GitHub
git push
```

## Important: Credentials NOT in GitHub ✅

Your `.gitignore` file protects these sensitive files:
- ✅ `google_credentials.json` - NOT pushed
- ✅ `.env` with API keys - NOT pushed
- ✅ `data/` folder - NOT pushed

This is correct for security! 🔒

---

## Need Help?

If you get an authentication error, use Personal Access Token (PAT):
1. Go to https://github.com/settings/tokens
2. Create new token (classic) with `repo` scope
3. Use token as password when prompted

---

**After pushing to GitHub, reply "Done!" and we'll continue with Tasks 2-5 🎯**
