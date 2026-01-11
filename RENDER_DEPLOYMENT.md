# Render Deployment Guide for Blood Sense AI

This guide will walk you through deploying Blood Sense AI to Render (free tier).

## Prerequisites

✅ GitHub account with your code pushed (already done!)
✅ Render account (free) - https://render.com

## Deployment Architecture

Your app will be deployed as two separate services on Render:
- **Backend**: Flask API (Web Service)
- **Frontend**: React app (Static Site)

---

## Step 1: Sign Up for Render

1. Go to https://render.com
2. Click **"Get Started for Free"**
3. Sign up with your GitHub account
4. Authorize Render to access your GitHub repositories

---

## Step 2: Deploy Backend (Flask API)

### 2.1 Create New Web Service

1. From Render Dashboard, click **"New +"** → **"Web Service"**
2. Connect to your GitHub repository:
   - Select **"Avinash-Patil-"** repository
3. Configure the service:
   - **Name**: `bloodsense-backend`
   - **Region**: Choose closest to you (e.g., Oregon)
   - **Branch**: `main`
   - **Root Directory**: Leave blank
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && gunicorn app:app --bind 0.0.0.0:$PORT`

### 2.2 Set Environment Variables

Scroll down to **"Environment Variables"** and add:

| Key | Value |
|-----|-------|
| `PYTHON_VERSION` | `3.10.11` |
| `JWT_SECRET_KEY` | Click "Generate" or enter: `your-super-secret-key-change-this-in-production` |
| `FLASK_ENV` | `production` |

### 2.3 Select Plan

- Choose **"Free"** plan
- Click **"Create Web Service"**

### 2.4 Wait for Deployment

- Render will start building your backend
- This takes 5-10 minutes on first deployment
- Watch the logs for any errors
- Once you see "Build succeeded", your backend is live!

### 2.5 Get Your Backend URL

- You'll see a URL like: `https://bloodsense-backend.onrender.com`
- **Copy this URL** - you'll need it for frontend setup
- Test it by visiting: `https://bloodsense-backend.onrender.com/api/health`
- You should see: `{"status": "healthy", ...}`

---

## Step 3: Update Frontend Configuration

### 3.1 Update Environment File

Before deploying the frontend, update the backend URL:

1. Open: `frontend/.env.production`
2. Replace with your actual backend URL:
   ```
   REACT_APP_API_URL=https://your-actual-backend-url.onrender.com
   ```
   (Replace `your-actual-backend-url` with the URL from Step 2.5)

### 3.2 Push Updated Frontend Config

```bash
# In your project directory
git add frontend/.env.production
git commit -m "Update production API URL"
git push origin main
```

---

## Step 4: Deploy Frontend (React App)

### 4.1 Create New Static Site

1. From Render Dashboard, click **"New +"** → **"Static Site"**
2. Select your **"Avinash-Patil-"** repository
3. Configure the site:
   - **Name**: `bloodsense-frontend`
   - **Branch**: `main`
   - **Root Directory**: Leave blank
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Publish Directory**: `frontend/build`

### 4.2 Add Rewrite Rule

Scroll to **"Redirects/Rewrites"** and add:

- **Source**: `/*`
- **Destination**: `/index.html`
- **Action**: `Rewrite`

This ensures React Router works properly.

### 4.3 Deploy

- Choose **"Free"** plan
- Click **"Create Static Site"**
- Wait 3-5 minutes for build to complete

### 4.4 Get Your Frontend URL

- You'll see a URL like: `https://bloodsense-frontend.onrender.com`
- This is your live application URL!

---

## Step 5: Test Your Deployed Application

### 5.1 Test Backend

Visit: `https://your-backend.onrender.com/api/health`

Expected response:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "timestamp": "..."
}
```

### 5.2 Test Frontend

1. Visit: `https://your-frontend.onrender.com`
2. You should see the Blood Sense AI login page
3. Try logging in with demo credentials
4. Test uploading an image
5. Verify model predictions work

---

## Step 6: Configure CORS (if needed)

If you get CORS errors in the browser console:

1. Go to your backend service on Render
2. Add environment variable:
   - **Key**: `FRONTEND_URL`
   - **Value**: `https://your-frontend.onrender.com`
3. Update `backend/app.py` to use this in CORS config
4. Push changes to trigger redeploy

---

## Common Issues & Solutions

### Issue: Backend Build Fails

**Error**: `Could not find a version that satisfies the requirement tensorflow...`

**Solution**: 
- Render's free tier has limited resources
- TensorFlow may take time to install
- Check build logs for specific errors
- May need to optimize dependencies

### Issue: Frontend Shows "Failed to Connect"

**Cause**: Backend URL not set correctly

**Solution**:
1. Verify `frontend/.env.production` has correct backend URL
2. Rebuild frontend on Render
3. Check browser console for actual API URL being called

### Issue: Cold Starts (30s delay)

**Explanation**: Free tier services "spin down" after 15 minutes of inactivity

**Solution**: 
- Accept the delay (it's normal for free tier)
- Or upgrade to paid plan ($7/month) for always-on service
- First request after inactivity will be slow, subsequent ones are fast

### Issue: Upload Doesn't Work

**Cause**: File upload limits or CORS

**Solution**:
1. Check Render logs for errors
2. Verify CORS is configured for your frontend URL
3. Check file size limits (Render free tier: 100MB max)

---

## Monitoring Your Deployment

### View Logs

**Backend Logs:**
1. Go to Render Dashboard
2. Click on `bloodsense-backend`
3. Click **"Logs"** tab
4. See real-time application logs

**Frontend Logs:**
1. Click on `bloodsense-frontend`
2. Check build logs for any issues

### Monitor Usage

- Free tier includes:
  - 750 hours/month (plenty for testing)
  - 100GB bandwidth
  - Services spin down after 15min inactivity

---

## Updating Your Deployment

Render automatically redeploys when you push to GitHub!

```bash
# Make changes to your code
git add .
git commit -m "Your update message"
git push origin main

# Render automatically detects the push and redeploys!
```

**Manual Deploy:**
- Go to service on Render Dashboard
- Click **"Manual Deploy"** → **"Deploy latest commit"**

---

## Free Tier Limitations

✅ **What's Included:**
- Free backend API deployment
- Free frontend static site
- Automatic HTTPS/SSL
- Custom domains (optional)
- Automatic deployments from GitHub

⚠️ **Limitations:**
- Services spin down after 15min inactivity (30s wake-up time)
- Limited to 512MB RAM per service
- 100GB bandwidth/month
- Shared CPU resources

💡 **If You Need More:**
- Upgrade to paid plan: $7/month
- Always-on services (no cold starts)
- More RAM and CPU
- Priority support

---

## Your Deployment URLs

After completing all steps, you'll have:

- **Frontend (Public URL)**: `https://bloodsense-frontend.onrender.com`
- **Backend API**: `https://bloodsense-backend.onrender.com`
- **Health Check**: `https://bloodsense-backend.onrender.com/api/health`

Share the frontend URL with anyone to access your Blood Sense AI application!

---

## Next Steps After Deployment

1. ✅ Test all features thoroughly
2. ✅ Share the frontend URL with users/testers
3. ✅ Monitor logs for any errors
4. ✅ Set up custom domain (optional)
5. ✅ Add database for persistent storage (optional - future enhancement)

---

## Need Help?

- **Render Documentation**: https://render.com/docs
- **Render Community**: https://community.render.com
- **GitHub Issues**: Create issue in your repo

---

## Quick Reference Commands

```bash
# View deployment status
# (Use Render Dashboard)

# Force redeploy
# Render Dashboard → Manual Deploy → Deploy latest commit

# View logs
# Render Dashboard → Your Service → Logs tab

# Update code and auto-deploy
git add .
git commit -m "Update"
git push origin main
```

---

**🎉 Congratulations! Your Blood Sense AI application is now deployed and accessible worldwide!**
