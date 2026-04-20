# Amigos Project - Production Roadmap & TODOs

To transform Amigos Tourism into a production-grade travel CRM and operations platform, the following logical, phased roadmap has been defined. This prioritizes data integrity and security first, followed by operational features and advanced automation.

---

## Phase 1: Foundation & Data Integrity (High Priority)
*Goal: Fix existing bugs, secure the admin portal, and prepare the database for scaling.*
- [x] **Fix Lead Data Loss**: Add `preferred_destination` column to the `Lead` model and update `frontend/src/pages/BookingForm.jsx` to map the destination input to this field.
- [x] **Database-Backed Admin Auth**:
    - [x] Implement password hashing (Bcrypt/Argon2) in the `Admin` model.
    - [x] Update `admin_routes.py` to authenticate against the `Admin` table instead of `.env` hardcoded variables.
- [x] **Standardize Auditing**: Add `created_at` and `updated_at` (with server-side default and on-update triggers) to all SQLAlchemy models.
- [x] **Database Migration Strategy**: Initialize Flask-Migrate (Alembic) to handle schema changes and prepare for the move from SQLite to PostgreSQL.
- [x] **Input Validation Layer**: Integrate Marshmallow schemas for ALL models (Leads, Packages, Finance, Customers, Bookings, Tasks) to validate incoming JSON.

---

## Phase 2: CRM Core Expansion (Operations)
*Goal: Implement the Lead-to-Booking lifecycle and task assignments.*
- [x] **Lead Conversion Logic**: Robust `POST /admin/lead/<id>/convert` endpoint that:
    - [x] Checks for existing customers by phone/email to prevent duplication.
    - [x] Creates a `Booking` linked to the connected `Lead` and `Customer`.
    - [x] Maps travel dates from frontend modal to booking record.
    - [x] Sets `Lead` status to `Confirmed`.
    - [x] **Automation**: Automatically generates a "Review Itinerary" task upon successful conversion.
- [x] **Task Management System (Operations)**:
    - [x] Build API and UI for the `Task` model to track granular operations (e.g., "Book Hotel," "Send Itinerary") linked to specific Leads.
- [x] **Enhanced Admin Dashboard UI**:
    - [x] Fixed conversion button visibility (shows for pending/contacted leads).
    - [x] Replaced primitive `prompt()` with a **Conversion Modal** to capture price and specific trip dates.

---

## Phase 3: Financial & Analytical Intelligence
*Goal: Track profitability and provide high-level business insights.*
- [ ] **Finance Model Refinement**: Link `TripFinance` directly to a `Booking` rather than just a `Lead` to ensure revenue is exclusively tied to confirmed sales.
- [ ] **Automated Profit Calculation**: Move profit computation logic from the frontend to the backend `TripFinance` model (using SQLAlchemy `@hybrid_property` or `before_flush` listeners) to ensure database-level consistency.
- [ ] **Analytics API**: Create `GET /admin/stats` to return:
    - [ ] Conversion Rate (Leads → Bookings).
    - [ ] Total Revenue vs. Total Profit for the current month.
    - [ ] Lead volume grouped by source or type.

---

## Phase 4: Frontend Modernization & UX
*Goal: Improve performance, state handling, and interactive feedback.*
- [ ] **Data Fetching Migration**: Replace manual `useEffect` fetching with TanStack Query (React Query) for caching, background re-fetching, caching invalidation, and better error states.
- [ ] **Centralized API Client**: Refactor `api.js` to handle global error toasts (e.g., 401 Unauthorized redirects) and inject Auth tokens automatically via interceptors.
- [ ] **Interactive Feedback**: Implement a comprehensive "Toast" system (e.g., `react-hot-toast` or `sonner`) for all admin layout actions (Update Lead, Build Staff, Delete Package).
- [ ] **Multi-Step Booking Form**: Refactor `BookingForm.jsx` into a stepped wizard to provide an optimal and premium customer UX.

---

## Phase 5: Advanced Automation & Document Handling
*Goal: Automate manual tasks and centralize file assets.*
- [ ] **Blob Storage Integration**: Setup AWS S3 (or Cloudflare R2) infrastructure for:
    - [ ] Uploading Destination and Package images.
    - [ ] Storing and serving generated user Itineraries.
- [ ] **PDF Generation Engine**: 
    - [ ] Create an HTML/CSS template to represent beautiful Trip Itineraries.
    - [ ] Implement an endpoint `GET /admin/booking/<id>/itinerary` that generates and serves a PDF buffer using tools like WeasyPrint or ReportLab.
- [ ] **Asynchronous Task Queue (Recommended)**:
    - [ ] Setup Redis + Celery to handle PDF generation and Email notifications (using SendGrid or SMTP) so the core API response times remain low.
- [ ] **Itinerary Emailer**: Automatically compose and email the generated PDF outline to the customer when the booking is marked as `Confirmed`.

---

## Phase 6: Infrastructure & Deployment
*Goal: Ensure the system architecture is resilient and ready for production traffic.*
- [ ] **PostgreSQL Migration**: Migrate production deployment from SQLite (currently development-bound) to a managed PostgreSQL cluster.
- [ ] **Dockerization**: Output `Dockerfile` and `docker-compose.yml` specs for the Flask API, Redis, and decoupled Celery workers.
- [ ] **Production Web Server**: Configure `Gunicorn` with asynchronous workers for the Flask app to optimally handle concurrent requests.
- [ ] **CI/CD Pipeline**: Setup GitHub Actions workflow to auto-deploy the Vite React frontend to Vercel/Netlify and the Flask backend to a Cloud Platform provider (AWS, Render, Railway).
- [ ] **Security Audit**: Lock down CORS specifically to the registered production domain and verify all Admin endpoints invoke the `admin_required` checks reliably.

---

### Completed Modules (Phase 0)
- [x] Initial Refactor of AdminDashboard for Leads (`Lead` model migration).
- [x] Admin Packages Management (CRUD).
- [x] Destinations Catalog Management (CRUD).
- [x] Staff Management & Lead Handling Assignments. 
- [x] Basic Trip Financial Logging inside `AdminFinance.jsx`.
