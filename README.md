# 🏭 IT Inventory Tracking Dashboard

A real-time web dashboard for tracking Consumables & Toners inventory with multi-user support.

## ✨ Features

- 📦 **Consumables Inventory** - Track IT equipment & accessories
- 🖨️ **Toner Inventory** - Track printer toners & cartridges
- 🔄 **Pick/Stow Operations** - Real-time stock updates
- 📊 **Charts & Analytics** - Visual stock distribution
- 👥 **Multi-User Support** - Admin and regular user roles
- 📥 **Export to Excel** - Download inventory data
- 📋 **Activity Log** - Complete transaction history
- 🔐 **Password Protection** - Secure admin access

## 🚀 Deploy to Internet (FREE)

### Option 1: Render.com (Recommended - Easiest)

1. **Create GitHub Repository:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```
   - Go to https://github.com/new
   - Create new repository
   - Push your code:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
   git branch -M main
   git push -u origin main
   ```

2. **Deploy on Render:**
   - Go to https://render.com
   - Sign up with GitHub
   - Click **"New +"** → **"Web Service"**
   - Connect your GitHub repository
   - Settings:
     - **Build Command:** `pip install -r requirements.txt`
     - **Start Command:** `streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true`
   - Click **"Create Web Service"**

3. **Your app will be live at:** `https://your-app-name.onrender.com`

---

### Option 2: Streamlit Community Cloud (Easiest but Limited)

1. Push code to GitHub (same as above)
2. Go to https://share.streamlit.io
3. Click **"New app"** → Select your repo → Deploy
4. Get URL: `https://your-app.streamlit.app`

---

### Option 3: Railway.app

1. Go to https://railway.app
2. Sign up with GitHub
3. Click **"New Project"** → **"Deploy from GitHub repo"**
4. Select your repository
5. Railway auto-detects settings from Procfile

---

## 💻 Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
streamlit run app.py

# Run on network (access from other devices)
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

## 📁 Project Structure

```
├── app.py              # Main Streamlit application
├── database.py         # Database functions
├── requirements.txt    # Python dependencies
├── Procfile           # Deployment configuration
├── runtime.txt        # Python version for deployment
├── .gitignore         # Git ignore file
└── README.md          # This file
```

## 👤 Default Admin Users

| Username | Password |
|----------|----------|
| gmanisel | MAA4@123 |
| ddink    | MAA4@123 |
| saswith  | MAA4@123 |

## 📱 Access from Mobile

The dashboard is fully responsive and works on mobile browsers. Simply access the URL from any device.

## 🔒 Security Note

For production use, consider:
- Changing default admin passwords
- Using environment variables for sensitive data
- Implementing HTTPS (automatically handled by Render/Railway)

## 📞 Support

For issues or feature requests, contact IT team.