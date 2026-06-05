# AMWAL

Asset Management and Wealth Analytics Lab - Django + PostgreSQL + React (Vite).

## Docker

docker compose up --build

- Client: http://localhost:5173 (owner / amwal123)
- Backend: http://localhost:5173/admin/properties (admin / amwal123)
- API: http://localhost:8000

## Demo users

owner, admin, pmanager, analyst, viewer - password amwal123

## Local SQLite dev

cd backend
set USE_SQLITE=1
python manage.py migrate
python manage.py seed_amwal
python manage.py runserver

cd frontend
npm install
npm run dev