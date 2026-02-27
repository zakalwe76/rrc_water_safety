# Fly.io Deployment Guide - GitHub Actions Method

## Overview

This guide shows you how to deploy to Fly.io using **GitHub Actions** (automatic deployment), which means:
- ✅ No need to install flyctl locally
- ✅ Automatic deployments on every push to GitHub
- ✅ Deployment from GitHub's servers, not your laptop
- ✅ Simple and maintainable

## What We've Set Up

Two files have been created in your repository:

1. **`.github/workflows/fly-deploy.yml`** - GitHub Actions workflow (auto-deployment)
2. **`fly.toml`** - Fly.io configuration file

## Prerequisites

1. **GitHub Account** - You already have one
2. **Fly.io Account** - You'll create this (requires credit card for verification, but won't be charged)
3. **Your code in GitHub** - Push your current code to GitHub

---

## Step-by-Step Deployment

### Step 1: Ensure Code is on GitHub

If your code isn't already on GitHub:

```bash
# Initialize git if needed
git init

# Add all files
git add .

# Commit
git commit -m "Prepare for Fly.io deployment"

# Create a new repository on GitHub (go to github.com and create new repo)
# Then connect it:
git remote add origin https://github.com/YOUR_USERNAME/rrc_water_safety.git
git branch -M main
git push -u origin main
```

If your code is already on GitHub, just make sure the new files are committed and pushed:

```bash
git add .github/workflows/fly-deploy.yml fly.toml
git commit -m "Add Fly.io deployment configuration"
git push
```

---

### Step 2: Create Fly.io Account

1. Go to https://fly.io/app/sign-up
2. Sign up with GitHub (easiest - auto-links your repos)
3. **Credit card required** for verification (won't be charged on free tier)
4. Complete verification

---

### Step 3: Install Fly CLI (One-time Setup)

Even though deployments will be from GitHub, we need flyctl for the **initial app creation**.

**For Windows (PowerShell as Administrator):**
```powershell
iwr https://fly.io/install.ps1 -useb | iex
```

**Or download installer:**
- Go to https://fly.io/docs/hands-on/install-flyctl/
- Download Windows installer
- Run installer
- Restart your terminal

**Verify installation:**
```bash
flyctl version
```

---

### Step 4: Login to Fly.io

```bash
flyctl auth login
```

This will open a browser window - authorize the connection.

---

### Step 5: Create the App on Fly.io

From your project directory:

```bash
cd "C:\Users\WilliamTrotter\OneDrive - Veracode\Veracode Internal Initiatives\code_projects\rrc_water_safety"

# Create the app (uses fly.toml configuration)
flyctl apps create rrc-water-safety
```

**Note:** The app name must be globally unique. If `rrc-water-safety` is taken, try:
- `rrc-water-safety-app`
- `reading-rowing-club-water`
- `rrc-water-conditions`

If name is taken, update the `app = "..."` line in `fly.toml` to match your chosen name.

---

### Step 6: Get Your Fly.io API Token

```bash
flyctl auth token
```

This will output a token like: `fo1_abc123def456...`

**Copy this token** - you'll need it in the next step.

---

### Step 7: Add Token to GitHub Secrets

1. Go to your GitHub repository
2. Click **Settings** (top tab)
3. Click **Secrets and variables** → **Actions** (left sidebar)
4. Click **New repository secret**
5. Name: `FLY_API_TOKEN`
6. Value: Paste the token from Step 6
7. Click **Add secret**

---

### Step 8: Initial Deployment (From Local Machine)

Do the first deployment manually to make sure everything works:

```bash
flyctl deploy
```

This will:
- Build your Docker image
- Push it to Fly.io
- Deploy your app
- Give you a URL

**Expected output:**
```
==> Verifying app config
--> Verified app config
==> Building image
...
==> Pushing image to fly
...
==> Creating release
--> Release v1 created
--> Checking health...
  ✓ Machine xxx is healthy

Visit your newly deployed app at https://rrc-water-safety.fly.dev/
```

---

### Step 9: Test Your Deployment

Open the URL provided (something like `https://rrc-water-safety.fly.dev/`)

Test the API:
```bash
curl https://rrc-water-safety.fly.dev/api/conditions
```

You should see your water safety data!

---

### Step 10: Verify GitHub Actions is Set Up

1. Go to your GitHub repository
2. Click the **Actions** tab
3. You should see the "Deploy to Fly.io" workflow

Now, every time you push to the `main` branch, it will automatically deploy!

---

## Testing Automatic Deployment

Make a small change and push:

```bash
# Make a small change (e.g., update README)
echo "# Deployed on Fly.io" >> README.md

# Commit and push
git add README.md
git commit -m "Test automatic deployment"
git push

# Watch it deploy
# Go to: https://github.com/YOUR_USERNAME/rrc_water_safety/actions
# You'll see the deployment running in real-time
```

---

## Your App URLs

After deployment, you'll have:

- **Main App:** `https://rrc-water-safety.fly.dev/`
- **API Endpoint:** `https://rrc-water-safety.fly.dev/api/conditions`

---

## Free Tier Details

Your `fly.toml` is configured for the free tier:

```toml
[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 256
```

**Free tier includes:**
- Up to 3 shared-cpu-1x VMs (256MB RAM each)
- 160 GB outbound data transfer
- Your app uses 1 VM = well within free limits

**Important settings:**
```toml
auto_stop_machines = false  # Keeps your app always running
auto_start_machines = false
min_machines_running = 1    # Always 1 machine active = no cold starts!
```

---

## Monitoring Your App

### View Logs
```bash
flyctl logs
```

### View App Status
```bash
flyctl status
```

### SSH into Container (for debugging)
```bash
flyctl ssh console
```

### View Metrics
Go to: https://fly.io/dashboard/YOUR_USERNAME/rrc-water-safety

---

## Updating Your App

Just push to GitHub:

```bash
# Make changes to your code
# e.g., edit app.py

git add .
git commit -m "Update water safety logic"
git push

# GitHub Actions automatically deploys!
# Watch at: https://github.com/YOUR_USERNAME/rrc_water_safety/actions
```

---

## Configuration Changes

### Change Region (Optional)
Current region: `lhr` (London Heathrow - best for UK)

Other UK/Europe options:
- `lhr` - London, UK (current)
- `ams` - Amsterdam, Netherlands
- `fra` - Frankfurt, Germany

Edit `fly.toml`:
```toml
primary_region = "lhr"
```

### Change Memory (If Needed)
If you need more memory:

Edit `fly.toml`:
```toml
[[vm]]
  memory_mb = 512  # Increase to 512MB (still free tier)
```

Then deploy:
```bash
flyctl deploy
```

---

## Custom Domain (Optional)

### Add Custom Domain

1. **Buy a domain** (e.g., `rowing.readingrowingclub.com`)

2. **Add to Fly.io:**
```bash
flyctl certs add rowing.readingrowingclub.com
```

3. **Add DNS records** (at your domain provider):
```
Type: CNAME
Name: rowing
Value: rrc-water-safety.fly.dev
```

4. **Automatic HTTPS** - Fly.io handles SSL automatically!

---

## Troubleshooting

### Deployment Fails in GitHub Actions

**Check the logs:**
1. Go to GitHub → Actions tab
2. Click on the failed run
3. Expand the deploy step to see error

**Common issues:**
- Token expired: Generate new token and update GitHub secret
- Docker build failure: Check Dockerfile syntax
- Memory limit: Increase in fly.toml

### App Not Starting

**Check logs:**
```bash
flyctl logs
```

**Common issues:**
- External APIs not reachable (should work - check logs for HTTP errors)
- Port misconfiguration (should be 5000 in both Dockerfile and fly.toml)

### "App name already taken"

Change app name in `fly.toml`:
```toml
app = "rrc-water-safety-2"  # Change to unique name
```

Then:
```bash
flyctl apps create rrc-water-safety-2
flyctl deploy
```

---

## Scaling (If Needed in Future)

### Add More VMs (Still Free!)
```bash
flyctl scale count 2  # Add a second VM for redundancy
```

### Scale Memory
```bash
flyctl scale memory 512  # Increase to 512MB
```

---

## Cost Management

### Check Usage
```bash
flyctl scale show
```

### Monitor Billing
Go to: https://fly.io/dashboard/YOUR_USERNAME/billing

**Free tier limits:**
- 3 VMs × 256MB = free
- Your app (1 VM × 256MB) = **$0/month**

---

## Maintenance

### Update Docker Image
Changes to Dockerfile automatically deploy via GitHub Actions.

### View Deployments
```bash
flyctl releases
```

### Rollback (If Needed)
```bash
flyctl releases list
flyctl rollback v2  # Roll back to version 2
```

---

## Security Best Practices

✅ **Already configured:**
- HTTPS forced
- Secure token storage in GitHub Secrets
- No sensitive data in repository

**Additional recommendations:**
- Rotate Fly.io token periodically
- Monitor access logs
- Keep Docker base image updated

---

## Local Development

Your local development workflow remains the same:

```bash
# Local testing
docker-compose up

# Test locally
curl http://localhost:5000/api/conditions

# When ready, commit and push
git add .
git commit -m "New feature"
git push  # Auto-deploys to Fly.io!
```

---

## Summary Checklist

- [ ] Code pushed to GitHub
- [ ] Fly.io account created (with credit card verification)
- [ ] flyctl installed locally
- [ ] Logged into Fly.io (`flyctl auth login`)
- [ ] App created on Fly.io (`flyctl apps create`)
- [ ] API token generated and added to GitHub Secrets
- [ ] Initial deployment successful (`flyctl deploy`)
- [ ] App accessible at fly.dev URL
- [ ] GitHub Actions workflow running
- [ ] Automatic deployments working

---

## Quick Reference Commands

```bash
# Login
flyctl auth login

# Check status
flyctl status

# View logs
flyctl logs

# Deploy manually (if needed)
flyctl deploy

# SSH into container
flyctl ssh console

# View releases
flyctl releases

# Scale up
flyctl scale count 2
flyctl scale memory 512

# Get help
flyctl help
```

---

## Support

- **Fly.io Docs:** https://fly.io/docs/
- **Community Forum:** https://community.fly.io/
- **Status Page:** https://status.fly.io/

---

## What's Next?

After deployment:

1. **Share the URL** with Reading Rowing Club members
2. **Bookmark it** for easy access
3. **Set up monitoring** (optional - use UptimeRobot to get alerts if down)
4. **Add to club website** (embed or link)

Your app is now live, automatically updating, and costs **$0/month**! 🎉

---

## Differences from Local

| Aspect | Local | Fly.io Production |
|--------|-------|-------------------|
| **URL** | localhost:5000 | rrc-water-safety.fly.dev |
| **HTTPS** | No | Yes (automatic) |
| **Uptime** | When you run it | 24/7 |
| **Access** | Only you | Anyone on internet |
| **Updates** | docker-compose up | git push (auto-deploy) |
| **Cost** | $0 | $0 (free tier) |

---

Need help with any step? Let me know where you are in the process!
