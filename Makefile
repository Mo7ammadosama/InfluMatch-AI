.PHONY: install install-frontend backend frontend test docker-up docker-down clean

## Install backend dependencies
install:
	pip install -r requirements.txt

## Install frontend dependencies
install-frontend:
	cd frontend_next && npm install

## Run the FastAPI backend on http://localhost:8000
backend:
	uvicorn app.main:app --reload --port 8000

## Run the Next.js frontend on http://localhost:3000
frontend:
	cd frontend_next && npm run dev

## Run the test suite
test:
	pytest

## Run the backend with Docker
docker-up:
	docker compose up --build -d

docker-down:
	docker compose down

## Remove caches
clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	rm -rf .pytest_cache
