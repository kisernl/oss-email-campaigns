# Email Campaign App - Comprehensive Build Checklist

## Project Overview
A React + FastAPI email campaign application with monospace design inspiration. Backend deployed to Railway, frontend runs locally for personal use.

## Phase 1: Project Setup & Backend Foundation

### 1.1 Project Structure Setup ✅
- [ ] **Task**: Create project directory structure
- [ ] **AI Prompt**: "Create a clean project structure with `backend/` and `frontend/` directories. Include basic README files and .gitignore for Python and Node.js"
- [ ] **Testing**: Verify directories exist and .gitignore files are properly configured
- [ ] **Files Created**:
  - `backend/` directory
  - `frontend/` directory
  - `backend/.gitignore`
  - `frontend/.gitignore`
  - Root `README.md`

### 1.2 Backend Environment Setup ✅
- [ ] **Task**: Initialize Python environment and dependencies
- [ ] **AI Prompt**: "Set up Python virtual environment in backend directory. Create requirements.txt with FastAPI, SQLAlchemy, Google Sheets API, and email dependencies. Include development dependencies."
- [ ] **Commands to Run**:
  ```bash
  cd backend
  python -m venv venv
  source venv/bin/activate  # On Windows: venv\Scripts\activate
  pip install -r requirements.txt
  ```
- [ ] **Testing**: pip list shows all required packages installed
- [ ] **Files Created**:
  - `backend/requirements.txt`
  - `backend/venv/` (local, not committed)

### 1.3 Backend Environment Configuration ✅
- [ ] **Task**: Create environment file for local development
- [ ] **AI Prompt**: "Create a .env.example file with all required environment variables for local development. Include SMTP settings, Google Sheets API, and database configuration."
- [ ] **Manual Setup**: Copy .env.example to .env and fill in actual credentials
- [ ] **Testing**: Environment variables load correctly in Python
- [ ] **Files Created**:
  - `backend/.env.example`
  - `backend/.env` (local, not committed)

### 1.4 Database Models & Configuration ✅
- [ ] **Task**: Create SQLAlchemy models and database configuration
- [ ] **AI Prompt**: "Create SQLAlchemy models for Campaign and EmailSend entities. Include database.py with SQLite configuration. Add proper relationships and indexes."
- [ ] **Testing**:
  - Models create tables successfully
  - Database connection works
  - Basic CRUD operations function
- [ ] **Files Created**:
  - `backend/app/__init__.py`
  - `backend/app/database.py`
  - `backend/app/models.py`
  - `backend/app/schemas.py`

### 1.5 Google Sheets Service ✅
- [ ] **Task**: Implement Google Sheets integration
- [ ] **AI Prompt**: "Create a Google Sheets service class that can read email addresses from sheets, validate sheet access, and mark emails as sent. Include error handling and proper authentication using service account credentials."
- [ ] **Testing**:
  - Connect to test Google Sheet
  - Read email addresses successfully
  - Mark emails as sent
  - Handle invalid sheet IDs gracefully
- [ ] **Files Created**:
  - `backend/app/services/__init__.py`
  - `backend/app/services/google_sheets.py`
  - `backend/credentials.json` (local, not committed)

### 1.6 Email Service Implementation ✅
- [ ] **Task**: Create SpaceMail SMTP email service
- [ ] **AI Prompt**: "Create an email service class for sending plain text emails via SpaceMail SMTP. Include connection testing, email personalization with recipient names, and proper error handling."
- [ ] **Testing**:
  - SMTP connection test passes
  - Send test email successfully
  - Handle SMTP errors gracefully
  - Email personalization works
- [ ] **Files Created**:
  - `backend/app/services/email_service.py`

### 1.7 FastAPI Endpoints ✅
- [ ] **Task**: Create API endpoints for campaigns and sheet preview
- [ ] **AI Prompt**: "Create FastAPI endpoints for campaign CRUD operations, Google Sheet preview, and health checks. Include proper error handling, request validation, and CORS configuration for local frontend."
- [ ] **Testing**:
  - All endpoints return correct status codes
  - Request validation works
  - Error responses are properly formatted
  - CORS headers allow frontend access
- [ ] **Files Created**:
  - `backend/app/main.py`

### 1.8 Backend API Testing ✅
- [ ] **Task**: Test all backend functionality locally
- [ ] **Commands to Run**:
  ```bash
  cd backend
  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
  ```
- [ ] **Manual Testing**:
  - [ ] Visit http://localhost:8000/docs (FastAPI docs)
  - [ ] Test /api/health endpoint
  - [ ] Test sheet preview with valid Google Sheet ID
  - [ ] Create test campaign (without sending)
  - [ ] Verify database records created
- [ ] **API Endpoints to Test**:
  - GET / - Root endpoint
  - GET /api/health - Health check
  - GET /api/sheets/{sheet_id}/preview - Sheet preview
  - POST /api/campaigns/ - Create campaign
  - GET /api/campaigns/ - List campaigns
  - GET /api/campaigns/{id} - Get campaign details

## Phase 2: Frontend Development

### 2.1 React App Initialization ✅
- [ ] **Task**: Set up React app with TypeScript and Tailwind
- [ ] **AI Prompt**: "Initialize a React TypeScript app in the frontend directory. Configure Tailwind CSS with a monospace-inspired design system. Include routing with react-router-dom and axios for API calls."
- [ ] **Commands to Run**:
  ```bash
  cd frontend
  npx create-react-app . --template typescript
  npm install axios react-router-dom @types/react-router-dom
  npm install -D tailwindcss postcss autoprefixer
  npx tailwindcss init -p
  ```
- [ ] **Testing**:
  - React app starts successfully
  - Tailwind classes work
  - TypeScript compilation successful
- [ ] **Files Created**:
  - `frontend/src/` (React app structure)
  - `frontend/tailwind.config.js`
  - `frontend/postcss.config.js`

### 2.2 Tailwind Configuration with Monospace Design ✅
- [ ] **Task**: Configure Tailwind with monospace design inspiration
- [ ] **AI Prompt**: "Update Tailwind config with a monospace-inspired design system. Include custom font families (mono stack), extended spacing scale, minimal color palette focusing on grays, and typography utilities for consistent hierarchy."
- [ ] **Testing**:
  - Custom fonts load correctly
  - Color palette renders properly
  - Spacing utilities work as expected
- [ ] **Files Modified**:
  - `frontend/tailwind.config.js`
  - `frontend/src/index.css`

### 2.3 API Service Layer ✅
- [ ] **Task**: Create API service for backend communication
- [ ] **AI Prompt**: "Create a TypeScript API service layer using axios to communicate with the FastAPI backend at localhost:8000. Include proper typing, error handling, and methods for all campaign operations."
- [ ] **Testing**:
  - API calls work with running backend
  - TypeScript types are correct
  - Error handling functions properly
- [ ] **Files Created**:
  - `frontend/src/services/api.ts`
  - `frontend/src/types/index.ts`

### 2.4 Main App Component & Routing ✅
- [ ] **Task**: Create main App component with routing
- [ ] **AI Prompt**: "Create the main App component with react-router-dom routing. Include a minimalist navigation header with monospace typography and routes for campaign creation and history views."
- [ ] **Testing**:
  - Routing works between pages
  - Navigation renders correctly
  - Monospace styling applied properly
- [ ] **Files Created**:
  - `frontend/src/App.tsx`
  - `frontend/src/components/Navigation.tsx`

### 2.5 CreateCampaign Component ✅
- [ ] **Task**: Build campaign creation form with monospace design
- [ ] **AI Prompt**: "Create a CreateCampaign component with a clean, monospace-inspired form design. Include Google Sheet ID input with preview functionality, campaign name, subject, and message fields. Use Tailwind for clean styling with generous whitespace."
- [ ] **Testing**:
  - Form validation works
  - Google Sheet preview functions
  - Campaign creation succeeds
  - Loading states display properly
  - Error messages show correctly
- [ ] **Files Created**:
  - `frontend/src/components/CreateCampaign.tsx`

### 2.6 CampaignList Component ✅
- [ ] **Task**: Build campaign history with grid layout
- [ ] **AI Prompt**: "Create a CampaignList component with a clean grid layout displaying campaign cards. Use monospace typography for data-focused presentation, include status indicators, progress bars, and campaign statistics."
- [ ] **Testing**:
  - Campaigns load and display correctly
  - Grid layout is responsive
  - Status indicators work
  - Progress bars show accurate data
- [ ] **Files Created**:
  - `frontend/src/components/CampaignList.tsx`

### 2.7 Frontend Integration Testing ✅
- [ ] **Task**: Test complete frontend functionality
- [ ] **Commands to Run**:
  ```bash
  cd frontend
  npm start
  ```
- [ ] **Manual Testing Checklist**:
  - [ ] App loads at http://localhost:3000
  - [ ] Navigation between pages works
  - [ ] Create campaign form renders correctly
  - [ ] Google Sheet preview works with valid ID
  - [ ] Form validation prevents invalid submissions
  - [ ] Campaign creation works end-to-end
  - [ ] Campaign history displays properly
  - [ ] Responsive design works on different screen sizes

## Phase 3: Complete System Testing

### 3.1 End-to-End Workflow Testing
- [ ] **Both Services Running**:
  - Backend: http://localhost:8000
  - Frontend: http://localhost:3000
- [ ] **Complete Workflow Test**:
  - [ ] Create Google Sheet with email addresses
  - [ ] Use Sheet ID in frontend form
  - [ ] Preview shows correct email count
  - [ ] Create and send campaign successfully
  - [ ] Verify emails sent via SMTP
  - [ ] Check Google Sheet updated with "Sent" status
  - [ ] View campaign in history with correct stats

### 3.2 Error Handling Testing
- [ ] **Invalid Inputs**:
  - [ ] Invalid Google Sheet ID
  - [ ] Malformed email addresses in sheet
  - [ ] SMTP connection failures
  - [ ] Missing required form fields
- [ ] **Edge Cases**:
  - [ ] Empty Google Sheets
  - [ ] Sheets with no email column
  - [ ] Very long email lists
  - [ ] Special characters in email content

### 3.3 Performance Testing
- [ ] **Load Testing**:
  - [ ] Test with 100+ email addresses
  - [ ] Multiple concurrent campaigns
  - [ ] Large email content
- [ ] **Frontend Performance**:
  - [ ] Page load times acceptable
  - [ ] Form interactions responsive
  - [ ] Large campaign lists render smoothly

## Phase 4: Production Preparation

### 4.1 Environment Configuration
- [ ] **Task**: Set up production environment variables
- [ ] **Railway Deployment Prep**:
  - [ ] Create railway.toml
  - [ ] Add Dockerfile for backend
  - [ ] Configure PostgreSQL database URL
  - [ ] Set production SMTP settings
- [ ] **Files Created**:
  - `railway.toml`
  - `backend/Dockerfile`

### 4.2 Security & Validation
- [ ] **Security Checklist**:
  - [ ] Environment variables not committed
  - [ ] API endpoints have proper validation
  - [ ] CORS configured correctly
  - [ ] SQL injection protection (SQLAlchemy ORM)
  - [ ] Email content sanitization
- [ ] **Input Validation**:
  - [ ] Google Sheet ID format validation
  - [ ] Email address validation
  - [ ] Campaign name length limits
  - [ ] Message content size limits

### 4.3 Documentation
- [ ] **Project Documentation**:
  - [ ] Update README with setup instructions
  - [ ] Document API endpoints
  - [ ] Add environment variable documentation
  - [ ] Create deployment guide
- [ ] **Code Documentation**:
  - [ ] Add docstrings to Python functions
  - [ ] Add TypeScript interface documentation
  - [ ] Comment complex business logic

## Phase 5: Deployment & Final Testing

### 5.1 Railway Deployment
- [ ] **Deploy to Railway**:
  - [ ] Connect GitHub repository
  - [ ] Add PostgreSQL service
  - [ ] Configure environment variables
  - [ ] Deploy and test production backend
- [ ] **Production Testing**:
  - [ ] Health check endpoint responds
  - [ ] Database connection works
  - [ ] Google Sheets API functions
  - [ ] SMTP sending works
  - [ ] API endpoints respond correctly

### 5.2 Final System Validation
- [ ] **Production Backend + Local Frontend**:
  - [ ] Update frontend API URL to Railway backend
  - [ ] Test complete workflow with production backend
  - [ ] Verify all functionality works
  - [ ] Performance acceptable
- [ ] **Final Acceptance Testing**:
  - [ ] Create real campaign with test emails
  - [ ] Verify end-to-end email delivery
  - [ ] Confirm Google Sheets integration
  - [ ] Test error scenarios
  - [ ] Validate all features working

## AI Coding Agent Prompts Reference

### Backend Development Prompts
1. **Project Structure**: "Create a clean Python FastAPI project structure with proper separation of concerns, including models, services, and API routes."
2. **Database Models**: "Design SQLAlchemy models for an email campaign system with Campaign and EmailSend entities, including proper relationships and indexes."
3. **Google Sheets Integration**: "Implement a robust Google Sheets service using the Google Sheets API to read email lists and update send status."
4. **Email Service**: "Create a professional email service class with SMTP integration, error handling, and email personalization capabilities."
5. **API Endpoints**: "Build comprehensive FastAPI endpoints with proper validation, error handling, and documentation for an email campaign system."

### Frontend Development Prompts
1. **React Setup**: "Initialize a modern React TypeScript application with clean architecture, routing, and state management."
2. **Tailwind Design System**: "Create a monospace-inspired design system using Tailwind CSS with clean typography, minimal colors, and generous whitespace."
3. **API Integration**: "Build a type-safe API service layer for React using axios with proper error handling and TypeScript interfaces."
4. **Campaign Forms**: "Design clean, user-friendly forms for email campaign creation with validation, preview functionality, and loading states."
5. **Data Display**: "Create responsive, data-focused components for displaying campaign history and statistics with monospace design aesthetics."

## Testing Commands Reference

### Backend Testing
```bash
# Start backend development server
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Test API endpoints
curl http://localhost:8000/api/health
curl http://localhost:8000/docs  # API documentation
```

### Frontend Testing
```bash
# Start frontend development server
cd frontend
npm start

# Run TypeScript check
npm run build

# Test in browser
open http://localhost:3000
```

### Integration Testing
```bash
# Start both services
# Terminal 1: Backend
cd backend && uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend && npm start

# Test complete workflow in browser
```

## Success Criteria
- [ ] Backend API responds correctly to all endpoints
- [ ] Frontend loads and functions without errors
- [ ] Google Sheets integration reads and updates sheets
- [ ] Email sending works via SpaceMail SMTP
- [ ] Campaign creation and management functions end-to-end
- [ ] Monospace design inspiration properly implemented
- [ ] Application ready for production deployment
- [ ] All error cases handled gracefully
- [ ] Performance acceptable for personal use
- [ ] Code is clean, documented, and maintainable

---

**Next Steps**: Start with Phase 1.1 - Project Structure Setup

---

This comprehensive checklist provides:

1. **Detailed task breakdown** with clear deliverables
2. **AI coding agent prompts** for each major component
3. **Testing procedures** for validation at each step
4. **Commands to run** for setup and testing
5. **File tracking** to know what should be created
6. **Success criteria** for each phase
7. **Reference sections** for quick lookup