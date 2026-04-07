# Deploy Guide: Vercel + Render

This setup deploys:
- `frontend` on Vercel (React + Vite)
- `Backend` on Render (FastAPI)

## 1) Prepare accounts and secrets

Create these first:
- Render account
- Vercel account
- MongoDB Atlas cluster + connection string
- Groq API key

Keep these values ready:
- `MONGODB_URL`
- `GROQ_API_KEY`

---

## 2) Deploy backend on Render

This repo includes `render.yaml` for the backend service.

1. Push your repo to GitHub.
2. In Render: **New** -> **Blueprint**.
3. Select your repo.
4. Render detects `render.yaml` and proposes `blogy-api`.
5. Continue and create the service.
6. Open the created service -> **Environment** and set:
   - `GROQ_API_KEY` (required)
   - `MONGODB_URL` (required)
   - `CORS_ORIGINS` (temporarily set to `https://your-frontend.vercel.app,http://localhost:5173`)
   - Optional keys if you use them:
     - `SERPAPI_KEY`
     - `HASHNODE_API_TOKEN`
     - `HASHNODE_PUBLICATION_ID`
7. Deploy and wait for status **Live**.
8. Copy backend URL, for example:
   - `https://blogy-api.onrender.com`
9. Verify:
   - Visit `https://blogy-api.onrender.com/health`
   - You should get JSON with `status: "healthy"`.

Important config check for this repo:
- Do not set Render root directory to `Backend`.
- Keep it at repo root so startup uses `Backend.core.main:app` exactly as in `render.yaml`.

---

## 3) Deploy frontend on Vercel

1. In Vercel: **Add New...** -> **Project**.
2. Import the same GitHub repo.
3. Set **Root Directory** to `frontend`.
4. Vercel should detect Vite automatically.
5. Add env var:
   - `VITE_API_URL` = your Render backend URL (for example `https://blogy-api.onrender.com`)
6. Deploy.
7. Copy the Vercel URL, for example:
   - `https://your-app.vercel.app`

---

## 4) Final CORS update (important)

After frontend deploy, go back to Render and update:
- `CORS_ORIGINS=https://your-app.vercel.app,http://localhost:5173`

Then redeploy backend (or trigger restart).

---

## 5) Smoke test checklist

1. Open Vercel app URL.
2. Login/signup works.
3. Create a blog and confirm API calls succeed.
4. Check browser network tab:
   - Requests should go to Render URL from `VITE_API_URL`.
5. Check Render logs for backend errors.

---

## 6) Recommended free-tier notes

- Render free web services sleep after inactivity; first request can be slow (cold start).
- MongoDB Atlas free tier is enough for initial usage.
- If latency becomes an issue later, first upgrade Render instance or move to a no-sleep backend.

---

## 7) Optional domain mapping

If you attach custom domains:
- Update `CORS_ORIGINS` with the custom frontend domain.
- Keep local dev origin if needed.

---

## 🔧 Troubleshooting

### Issue: 422 Error on Signup/Login from Vercel

**Cause:** Frontend missing `VITE_API_URL` environment variable, defaulting to `http://localhost:8000`.

**Fix:**
1. Go to Vercel dashboard → Your project
2. Settings → Environment Variables
3. Ensure `VITE_API_URL` is set to your Render backend URL:
   ```
   VITE_API_URL=https://blogy-api-q1q9.onrender.com
   ```
   *(Replace with your actual Render URL)*
4. **Redeploy** the frontend (Deployments → Redeploy)
5. Test signup again

**To Verify:**
- Open browser DevTools → Network tab
- Check signup request URL
- It should go to `https://blogy-api-xxx.onrender.com/auth/signup`
- NOT `http://localhost:8000/auth/signup`

---

### Issue: CORS Error after fixing API URL

**Cause:** Backend's `CORS_ORIGINS` doesn't include your Vercel frontend URL.

**Fix (Render Dashboard):**
1. Go to your `blogy-api` service
2. Environment → Edit `CORS_ORIGINS`
3. Add your Vercel URL:
   ```
   CORS_ORIGINS=https://your-app.vercel.app,http://localhost:5173
   ```
4. **Redeploy** the backend
5. Wait 2-3 minutes, then test again

**CORS Regex** (already configured):
- `CORS_ALLOW_ORIGIN_REGEX=https://.*\.vercel\.app` ✓
