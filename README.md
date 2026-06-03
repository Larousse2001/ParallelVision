# Parallel Vision

Plateforme de traitement parallele d images avec benchmarking.

## Fonctionnalites
- Upload multiple d images depuis le frontend React
- Traitements OpenCV: redimensionnement, niveaux de gris, contours, histogramme, detection de visages
- Architecture parallele multi-processus et multi-thread
- IPC: pipes, shared memory, message queue
- Synchronisation: barbier endormi et philosophes dineurs
- Benchmarking exporte en CSV

## Structure
- backend/: API FastAPI, workers et IPC
- frontend/: React + Material UI
- docs/: diagrammes et rapport technique

## API
- POST /upload
- POST /start
- GET /status
- GET /results
- GET /benchmark?run=1

## Lancer en local (sans Docker)
### Backend
1. Installer les dependances
   - `pip install -r backend/requirements.txt`
2. Demarrer le serveur
   - `uvicorn app.main:app --host 0.0.0.0 --port 8000`

### Frontend
1. Installer les dependances
   - `npm install`
2. Demarrer le serveur
   - `npm run dev`

## Lancer avec Docker
- `docker compose up --build`

Frontend: http://localhost:5173
Backend: http://localhost:8000

## Variables d environnement backend
- `PP_PROCESSES` (defaut: 8)
- `PP_THREADS` (defaut: 8)
- `PP_CPU_TOKENS` (defaut: 4)
- `PP_GPU_TOKENS` (defaut: 2)
- `PP_WAITING_ROOM` (defaut: 256)
- `PP_RESIZE_WIDTH` (defaut: 256)
- `PP_RESIZE_HEIGHT` (defaut: 256)
- `PP_HIST_BINS` (defaut: 16)

## Documentation
- Diagrammes: docs/diagrams.md
- Rapport technique: docs/rapport-technique.md
