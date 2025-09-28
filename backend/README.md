# Email Campaign Backend

FastAPI backend for the email campaign application.

## Features

- **Campaign Management**: Create, read, update, delete email campaigns
- **Google Sheets Integration**: Read email lists from Google Sheets
- **Email Service**: Send emails via SMTP with personalization
- **Database**: SQLAlchemy with SQLite (dev) / PostgreSQL (prod)
- **API Documentation**: Auto-generated with FastAPI

## Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your credentials
```

4. Run development server:
```bash
# Easy startup (recommended)
./start.sh

# Stop server
./stop.sh

# Or manual startup/stop
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
pkill -f "uvicorn app.main:app"
```

## API Endpoints

- `GET /` - Root endpoint
- `GET /api/health` - Health check
- `GET /api/sheets/{sheet_id}/preview` - Preview Google Sheet
- `POST /api/campaigns/` - Create campaign
- `GET /api/campaigns/` - List campaigns
- `GET /api/campaigns/{id}` - Get campaign details

## Documentation

Visit http://localhost:8000/docs for interactive API documentation.