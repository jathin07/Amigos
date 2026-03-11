# Amigos Current Stage and Workflow

## Current Working Stage

- Frontend SPA routing and major pages are implemented.
- Backend Flask APIs and SQLAlchemy models are implemented.
- Frontend-backend integration now includes:
  - `POST /plan-trip`
  - `POST /admin/login`
  - `GET /admin/trip-requests` (token protected)
  - `GET /admin/quick-bookings` (token protected)
  - `GET /itineraries` and `GET /itineraries/<id>` for package data
- Admin dashboard page now exists and consumes protected admin endpoints.

## What Was Added in This Iteration

- Environment-driven frontend API base URL (`frontend/src/config/api.js`).
- Backend request validation for trip and quick booking submissions.
- Health endpoint (`GET /health`) for deployment checks.
- Token-based admin authentication with expiring signed tokens.
- Protected admin read endpoints for lead management.
- Public itinerary read endpoints + admin itinerary create endpoint.
- Frontend package pages now consume itinerary APIs with static fallback.

## Product Workflow (End-to-End)

1. Visitor opens website and browses packages.
2. Package cards are loaded from `/itineraries` when available.
3. Visitor submits `Plan My Trip` form.
4. Backend validates payload and stores `TripRequest`.
5. Admin logs in at `/admin/login`.
6. Admin token is stored in browser local storage.
7. Dashboard fetches `trip-requests` and `quick-bookings` with Bearer token.
8. Admin contacts lead and updates operationally (status update API can be added next).

## Remaining to Fully Complete

- Add admin status update endpoints (`PATCH /admin/trip-requests/:id`, `PATCH /admin/quick-bookings/:id`).
- Add admin UI for creating/editing itineraries.
- Add tests (backend API tests + frontend integration tests).
- Add production config separation and secure secret handling (`.env`/secret manager).
- Add CI pipeline for lint/build/test + deployment.
