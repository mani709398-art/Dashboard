# Consumables & Toners Tracking Dashboard

A comprehensive web-based dashboard for tracking consumables and toners inventory with login-wise activity tracking, stock management, and analytics.

## Features

### 📦 Consumables Dashboard
- Total items in stock overview
- Low stock alerts with visual indicators
- Recent pick/stow activity tracking
- Item movement history
- Stock distribution by category (pie chart)
- Top items by stock (bar chart)

### 🖨️ Toner Dashboard
- Printer-wise toner availability
- Location-wise stock (P1 IT Cage, HRV Backside, RF Cage)
- Remaining toner count with color coding
- Usage trend visualization
- Stock by toner color breakdown

### 📋 Activity Dashboard
- Who picked/stowed items tracking
- Timestamp and quantity logging
- Item type filtering (Consumable/Toner)
- User-wise transaction summary
- Daily activity trends (30-day view)
- Date range search with CSV export

## Tech Stack

- **Frontend**: Streamlit
- **Database**: SQLite
- **Visualization**: Plotly
- **Data Processing**: Pandas

## Installation

1. Clone or download the project files

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Initialize the database (optional - auto-initialized on first run):
```bash
python database.py
```

4. Run the application:
```bash
streamlit run app.py
```

## Usage

1. **Login**: Select a user from the dropdown in the sidebar and click "Login"
2. **Navigate**: Use the sidebar radio buttons to switch between dashboards
3. **Pick/Stow Operations**: 
   - Login first to enable pick/stow functionality
   - Select item, enter quantity, and click the appropriate button
4. **View History**: Use the "Item History" tab to track movements
5. **Export Data**: Use the Search tab in Activity Dashboard to export CSV reports

## Database Schema

### Users
- id, username, full_name, department, created_at

### Consumables
- id, item_name, category, current_stock, min_stock_level, unit, location, last_updated

### Toners
- id, toner_model, printer_model, color, current_stock, min_stock_level, location, last_updated

### Activity Log
- id, user_id, item_type, item_id, item_name, action_type, quantity, notes, timestamp

## Sample Data

The application comes pre-loaded with sample data including:
- 5 sample users (Admin, John Doe, Jane Smith, Mike Wilson, Sarah Jones)
- 15 consumable items across various categories
- 15 toner types for different printers
- 50 sample activity records

## File Structure

```
├── app.py              # Main Streamlit application
├── database.py         # Database operations and schema
├── requirements.txt    # Python dependencies
├── README.md          # Documentation
└── tracking_dashboard.db  # SQLite database (auto-created)
```

## Screenshots

The dashboard includes:
- Real-time metrics display
- Interactive charts and graphs
- Color-coded status indicators (🟢 OK, 🔴 Low)
- Filterable activity logs
- Expandable location-wise toner views

## License

MIT License - Free to use and modify