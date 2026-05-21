# Hosting Plan: Amigos Application

This plan outlines the steps to deploy the **Amigos** application, consisting of a Flask backend and a Vite/React frontend, using Render (Backend/Database) and Vercel (Frontend).

## 1. Database Setup (Render)

Render offers a managed PostgreSQL service which is ideal for the Flask backend.

1.  Log in to [Render](https://dashboard.render.com/).
2.  Click **New +** and select **PostgreSQL**.
3.  **Name:** `amigos-db`
4.  **Database:** `amigos`
5.  **User:** `amigos_user`
6.  Select the **Free** tier (or appropriate tier for production).
7.  Once created, copy the **Internal Database URL** (for backend use if on Render) and **External Database URL** (for local migrations/testing).

## 2. Backend Deployment (Render)

The backend will be hosted as a **Web Service**.

### Configuration
1.  Click **New +** and select **Web Service**.
2.  Connect your GitHub/GitLab repository.
3.  **Name:** `amigos-backend`
4.  **Language:** `Python`
5.  **Root Directory:** `backend` (or leave empty if you want to run from repo root)
    > [!NOTE]
    > Since `requirements.txt` is in the root, it might be easier to leave Root Directory empty and adjust commands.
6.  **Build Command:** `pip install -r ../requirements.txt` (if Root Directory is `backend`) or `pip install -r requirements.txt` (if Root Directory is root).
7.  **Start Command:** `gunicorn -w 4 -b 0.0.0.0:$PORT "backend.run:app"` (from root) or `gunicorn -w 4 -b 0.0.0.0:$PORT run:app` (from `backend` folder).

### Environment Variables
Add the following in the Render Dashboard under **Environment**:
- `DATABASE_URL`: Your Render PostgreSQL URL.
- `SECRET_KEY`: A long, random string.
- `FRONTEND_ORIGIN`: `https://your-app-name.vercel.app` (The URL provided by Vercel later).
- `PYTHON_VERSION`: `3.11.x` (or your preferred version).

## 3. Frontend Deployment (Vercel)

Vercel is optimized for Vite/React applications.

1.  Log in to [Vercel](https://vercel.com/).
2.  Click **Add New...** -> **Project**.
3.  Import your repository.
4.  **Project Name:** `amigos-frontend`
5.  **Framework Preset:** `Vite` (automatically detected).
6.  **Root Directory:** `frontend`
7.  **Build Command:** `npm run build`
8.  **Output Directory:** `dist`

### Environment Variables
Add the following in the Vercel Dashboard:
- `VITE_API_BASE_URL`: `https://amigos-backend.onrender.com` (The URL provided by Render).

## 4. Post-Deployment Checklist

### Database Migrations
Once the backend is live, you need to run migrations. You can do this via Render's **Shell** or by connecting locally using the **External Database URL**:
```bash
# In the Render Shell (if available) or locally:
export DATABASE_URL="your_external_db_url"
flask db upgrade
```
*Alternatively, `run.py` has `db.create_all()` which will create tables if they don't exist, but using Flask-Migrate is better for future changes.*

### CORS Verification
Ensure that `FRONTEND_ORIGIN` in Render matches the actual Vercel URL. If you use a custom domain later, update this variable.

### Google Service Credentials
If your app uses Google Sheets (based on `credentials.json` found in your project):
1.  In Render, go to **Environment** -> **Secret Files**.
2.  Create a file named `credentials.json` and paste the content of your local `credentials.json`.
3.  Ensure your code points to the correct path (Render mounts secret files at a specific location or you can use an absolute path).

## Summary Table

| Service | Platform | Environment Variables |
| :--- | :--- | :--- |
| **Database** | Render | - |
| **Backend** | Render | `DATABASE_URL`, `FRONTEND_ORIGIN`, `SECRET_KEY` |
| **Frontend** | Vercel | `VITE_API_BASE_URL` |
