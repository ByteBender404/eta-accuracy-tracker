# Render Deployment Guide

This project is prepared for deployment to [Render](https://render.com/) as two separate services: a Web Service for the FastAPI backend and a Static Site for the React + Vite frontend.

## 1. Deploy the Backend (FastAPI)

1. Log into your Render dashboard and click **New +** -> **Web Service**.
2. Connect your GitHub repository.
3. Configure the service:
   - **Name:** `eta-tracker-backend` (or similar)
   - **Environment:** `Python 3`
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Expand **Advanced** and add the following Environment Variables:
   - `PYTHON_VERSION`: `3.10.0` (or your preferred compatible Python version).
   - `FRONTEND_URL`: Leave this empty for now, we will fill it in after deploying the frontend.
5. Click **Create Web Service**. Wait for the deployment to finish and note the backend's external URL (e.g., `https://eta-tracker-backend.onrender.com`).

## 2. Deploy the Frontend (React + Vite)

1. In the Render dashboard, click **New +** -> **Static Site**.
2. Connect the same GitHub repository.
3. Configure the site:
   - **Name:** `eta-tracker-frontend`
   - **Root Directory:** `frontend`
   - **Build Command:** `npm install && npm run build`
   - **Publish Directory:** `frontend/dist` (Vite's default output folder).
4. Expand **Advanced** and add the following Environment Variable:
   - `VITE_API_URL`: Paste the backend URL from step 1, appending `/api` at the end (e.g., `https://eta-tracker-backend.onrender.com/api`).
5. Expand **Redirects/Rewrites** and add a rule to support client-side routing (React Router):
   - **Source:** `/*`
   - **Destination:** `/index.html`
   - **Status:** `200`
6. Click **Create Static Site**.

## 3. Finalize Backend Configuration (CORS)

For security, the backend CORS is configured to only allow requests from the designated frontend URL. 

1. Once the frontend is deployed, copy its external URL (e.g., `https://eta-tracker-frontend.onrender.com`).
2. Go back to your backend service settings on Render.
3. Navigate to the **Environment** tab.
4. Set the `FRONTEND_URL` environment variable to your frontend's URL. (You can also allow multiple origins by separating them with a comma).
5. The backend will automatically restart and enforce the new CORS policy.

You're done! Your ETA Tracker is now live.
