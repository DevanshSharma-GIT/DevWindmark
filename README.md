# DevWindmark

DevWindmark is a full-stack application for a UK electricity buyer reviewing January 2026 day-ahead wind generation. It joins Elexon national wind outturn (FUELHH, fuelType=WIND) with the latest WINDFOR forecast available at a configurable D-1 decision cutoff, then reports forecast error, MAE, RMSE, bias, coverage, and time-of-day accuracy in MW.

Main features: executive dashboard, forecast explorer, accuracy charts, procurement-context notes without price or volume claims, and a documented methodology including the cutoff assumption.

## How to run locally

Preferred:

```bash
docker compose up --build
```

Frontend: http://localhost:8080  
Backend: http://localhost:8000  
API docs: http://localhost:8000/docs  

Stop with `docker compose down`.

Without Docker, from the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
cd backend && PYTHONPATH=. python -m app.cli refresh && PYTHONPATH=. uvicorn app.main:app --reload --port 8000
```

In another terminal:

```bash
cd frontend
npm install
npm run dev
```

Then open http://localhost:5173. The Vite proxy forwards `/api` to http://127.0.0.1:8000.

Refresh January 2026 data at any time with `cd backend && PYTHONPATH=. python -m app.cli refresh`. If Elexon is unavailable and no cache exists, the API uses a labelled demonstration dataset.

## Hosted application link

Deployment pending

## Links

- Portfolio: https://devanshportfolio-rho.vercel.app
- GitHub: https://github.com/DevanshSharma-GIT
- LinkedIn: https://www.linkedin.com/in/devansh-sharma-9713a8292/

## Acknowledgment

AI tools, including GitHub Copilot, were used during development.
