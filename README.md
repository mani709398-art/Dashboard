# IT Inventory Tracking Dashboard

A Streamlit-based dashboard for tracking IT consumables and toners with persistent cloud storage.

## Features

- 📦 **Consumables Tracking** - Track IT equipment like cables, adapters, peripherals
- 🖨️ **Toner Management** - Monitor toner inventory across locations
- 👥 **User Management** - Admin panel for user management with passwords
- 📊 **Analytics** - Visual charts and statistics
- 📜 **Activity Log** - Track all pick/stow operations with before/after counts
- 📥 **Export to Excel** - Download inventory reports

## Persistent Storage Setup (Supabase)

To ensure your data persists across Streamlit Cloud reboots, you need to set up a free PostgreSQL database using Supabase:

### Step 1: Create a Supabase Account

1. Go to [https://supabase.com](https://supabase.com)
2. Click "Start your project" and sign up (free tier available)
3. Create a new project (choose a strong password)

### Step 2: Get Your Database URL

1. In your Supabase dashboard, go to **Project Settings** (gear icon)
2. Click on **Database** in the left sidebar
3. Scroll down to **Connection string** section
4. Copy the **URI** connection string (it looks like):
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres
   ```
5. Replace `[YOUR-PASSWORD]` with the password you set when creating the project

### Step 3: Configure Streamlit Cloud Secrets

1. Go to your Streamlit Cloud dashboard
2. Click on your deployed app
3. Go to **Settings** → **Secrets**
4. Add the following secret:

```toml
DATABASE_URL = "postgresql://postgres:YOUR_PASSWORD@db.YOUR_PROJECT_REF.supabase.co:5432/postgres"
```

5. Click **Save**
6. Reboot your app

### Step 4: Verify Setup

After rebooting, your app will:
1. Automatically create all required tables in Supabase
2. Insert sample data (only if tables are empty)
3. All future changes will persist across reboots

## Local Development

For local development, the app uses SQLite (no setup required):

```bash
# Clone the repository
git clone <your-repo-url>
cd "Ton & Con"

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

## File Structure

```
├── app.py              # Main Streamlit application
├── database.py         # Database module (SQLite/PostgreSQL)
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string for Supabase | For production only |

## Default Admin Users

| Username | Full Name | Default Password |
|----------|-----------|------------------|
| gmanisel | Maniselvam G | MAA4@123 |
| saswith | Aswitha S | MAA4@123 |
| ddink | Dinesh Kumar | MAA4@123 |

## Locations Tracked

- P1 IT Cage
- HRV Backside
- RF Cage
- P3 IT Cage

## Troubleshooting

### Data not persisting after reboot?

1. Check if `DATABASE_URL` is correctly set in Streamlit secrets
2. Verify the Supabase password is correct (no special characters issues)
3. Check Streamlit Cloud logs for connection errors

### Connection errors?

1. Ensure your Supabase project is active (free tier pauses after inactivity)
2. Check if the database password contains special characters (may need URL encoding)
3. Verify the connection string format

### Tables not created?

The app automatically creates tables on startup. If issues persist:
1. Check Supabase SQL Editor for any errors
2. Try running the app locally first to verify the code

## Support

For issues or feature requests, please create an issue in the GitHub repository.

## License

MIT License