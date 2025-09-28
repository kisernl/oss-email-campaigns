# OSS Email Campaigns

A self-hosted email campaign management system with business hours scheduling, configurable delays, and Google Sheets integration. Built with FastAPI Python backend and React TypeScript frontend in a unified monorepo.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Google Sheets API credentials (optional)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd oss-email-campaigns
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your SMTP and configuration settings
   ```

3. **Configure Environment Variables**
   Edit `backend/.env` with your settings:
   ```env
   # Required for email sending
   SMTP_USERNAME=your-email@yourdomain.com
   SMTP_PASSWORD=your-app-password
   DEFAULT_FROM_EMAIL=your-email@yourdomain.com
   
   # Optional: Google Sheets integration
   GOOGLE_CREDENTIALS_FILE=credentials.json
   ```

4. **Database Setup**
   ```bash
   # Initialize database and run migrations
   python migrate_add_business_hours.py
   ```

5. **Start Backend**
   ```bash
   # Use the backend control script
   ./backend.sh start
   # Or from project root:
   ./start-backend.sh
   # Backend runs on http://localhost:8000
   ```

6. **Frontend Setup** (new terminal)
   ```bash
   cd frontend
   npm install
   npm start
   # Frontend runs on http://localhost:3000
   ```

## ⭐ Key Features

### Email Campaign Management
- **Campaign Creation**: Full-featured form with validation
- **Google Sheets Integration**: Direct import of email lists
- **Template Variables**: Dynamic personalization ({{name}}, {{company}}, etc.)
- **Campaign Status Tracking**: Draft, Sending, Completed, Failed states

### Business Hours Scheduling
- **Smart Send Times**: Configure business hours for professional delivery
- **Timezone Support**: Respect recipient timezones for optimal delivery
- **Weekend Handling**: Option to skip weekends for B2B campaigns
- **Queue Management**: Campaigns automatically queue outside business hours

### Anti-Spam Protection
- **Configurable Delays**: Random delays between 1-60 minutes
- **Per-Campaign Settings**: Enable/disable delays individually
- **Smart Logic**: Delays between ALL emails (success and failure)
- **Rate Limiting**: Built-in protection against spam detection

### User Interface
- **Modern Design**: Clean, intuitive interface
- **Responsive Layout**: Works on desktop and mobile
- **Real-time Updates**: Live campaign progress tracking
- **Form Validation**: Comprehensive error handling and feedback

## 📁 Project Structure

```
oss-email-campaigns/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── main.py         # Main application with campaign logic
│   │   ├── models.py       # Database models with business hours
│   │   ├── schemas.py      # API schemas with scheduling
│   │   ├── services/       # Email and Google Sheets services
│   │   └── utils/          # Business hours and scheduling utilities
│   ├── migrate_add_business_hours.py
│   ├── requirements.txt
│   ├── backend.sh          # Backend control script
│   └── .env.example        # Environment configuration template
├── frontend/               # React TypeScript frontend
│   ├── src/
│   │   ├── pages/CreateCampaign.tsx  # Campaign creation with scheduling
│   │   ├── pages/Campaigns.tsx       # Campaign management
│   │   ├── components/     # Reusable UI components
│   │   └── types/index.ts  # TypeScript definitions
│   └── package.json
├── start-backend.sh        # Quick backend start script
├── stop-backend.sh         # Backend stop script
└── README.md
```

## 🔧 Configuration

### Campaign Scheduling Options
Create campaigns with flexible timing:
- **Immediate Send**: Send emails right away
- **Business Hours**: Respect business hours (9 AM - 5 PM)
- **Custom Delays**: Random delays between emails (1-60 minutes)
- **Weekend Handling**: Skip or include weekend delivery

### Environment Variables (.env)
Key settings in `backend/.env`:
```env
# Email Configuration (Required)
SMTP_HOST=smtp.spacemail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@domain.com
SMTP_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@domain.com

# Google Sheets (Optional)
GOOGLE_CREDENTIALS_FILE=credentials.json

# Application Settings
ENVIRONMENT=development
DEBUG=true
CORS_ORIGINS=http://localhost:3000

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production

# Database
DATABASE_URL=sqlite:///./email_campaigns.db
```

## 🎯 How Campaign Scheduling Works

### Business Hours Logic
1. **Campaign Creation**: User configures business hours and timezone
2. **Queue Management**: Campaigns outside business hours are queued
3. **Smart Delivery**: Emails sent only during configured business hours
4. **Weekend Handling**: Option to skip weekends for B2B campaigns

### Delay System
1. **Email Processing**: System processes each email in sequence
2. **Delay Application**: After each email (success or failure):
   - Skip delay for last email
   - Apply random delay between configured min/max
   - Continue to next email

**Example with business hours (9 AM - 5 PM) and 2-4 minute delays:**
```
Campaign created at 8:30 AM → ⏳ Queued until 9:00 AM
9:00 AM - Email 1: ✅ Sent → ⏳ Wait 3 minutes
9:03 AM - Email 2: ❌ Failed → ⏳ Wait 2 minutes  
9:05 AM - Email 3: ✅ Sent → ⏳ Wait 4 minutes
...continues within business hours
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
python -m pytest  # Run tests
./test-integration.sh  # Integration tests
```

### Frontend Tests
```bash
cd frontend
npm test  # Jest tests
./test-integration.sh  # UI integration tests
```

## 🚀 Deployment

### Production Ready
Both backend and frontend are production-ready:

**Backend Options:**
- **Render**: Recommended (includes PostgreSQL)
- **Railway**: Great for Python apps
- **and more...**

**Frontend Options:**
Note: currently no authentication is implemented
- **Local Only**: Run `npm run build` and serve locally
With proper authentication you could deploy to any of the following:
- **Vercel**: Build with `npm run build` and deploy
- **Netlify**: Automatic builds from Git
- **Render Static Sites**: Part of same infrastructure
- **and more...**

**Database:**
- **Development**: SQLite (included)
- **Production**: PostgreSQL (auto-provisioned on most platforms)
- **and more...**

### Environment Variables for Production
Set these in your hosting platform:
- `ENVIRONMENT=production`
- `DATABASE_URL=postgresql://...` (auto-set by most platforms)
- `SMTP_USERNAME`, `SMTP_PASSWORD` (your email credentials)
- `SECRET_KEY` (generate a secure key)
- `CORS_ORIGINS=https://your-frontend-url.com`

## 📋 Development

### Backend Control Scripts
```bash
# All-in-one backend control (recommended)
./backend.sh start    # Start the server
./backend.sh stop     # Stop the server
./backend.sh restart  # Restart the server
./backend.sh status   # Check if running

# Alternative methods (from project root)
./start-backend.sh    # Start backend
./stop-backend.sh     # Stop backend
```

### Development Workflow
```bash
# Start development environment
./backend.sh start          # Terminal 1: Start backend
cd frontend && npm start    # Terminal 2: Start frontend

# Check logs
tail -f backend.log         # Monitor backend logs

# Database management
python migrate_add_business_hours.py  # Run migrations
```

### Adding Features
1. **Backend**: Add API endpoints in `app/main.py`
2. **Frontend**: Add React components in `src/pages/` or `src/components/`
3. **Database**: Create migration scripts for schema changes
4. **Types**: Update TypeScript interfaces in `frontend/src/types/`

### Debugging
- **Backend logs**: Check console output during email sending
- **Frontend**: React DevTools and browser console
- **Database**: Use SQLite browser to inspect campaign data

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

MIT License - see LICENSE file for details.

## 🔗 Links

- **Backend API**: http://localhost:8000/docs (Swagger UI)
- **Frontend App**: http://localhost:3000
- **Google Sheets Setup**: [backend/GOOGLE_SHEETS_SETUP.md](backend/GOOGLE_SHEETS_SETUP.md)

## Want to support?
Leave a star! 🌟