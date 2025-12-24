# Django Richmond College Scout Management System

## Local Development with Docker Compose
1. Copy the sample environment file: `cp .env.example .env` and adjust secrets as needed.
2. Build and start the stack: `docker compose up --build`.
3. Access the app at http://localhost:8000 once the containers report healthy.
4. Run one-off commands (e.g. createsuperuser) with `docker compose exec web python manage.py createsuperuser`.
5. Stop the stack with `docker compose down` (add `--volumes` to clear local data).
