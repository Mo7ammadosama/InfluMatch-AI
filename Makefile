# ============================================================
# COMPONENT 27: Makefile
# One-command developer shortcuts — InfluMatch.jo
# ============================================================

.PHONY: install init seed run backend frontend test test-unit test-integration \
        clean reset health docker-up docker-down lint

## Install all dependencies
install:
	pip install -r requirements.txt
	@echo "✅ Dependencies installed"

## Initialize database + seed RAG
init:
	python scripts/init_db.py
	python scripts/seed_rag.py
	@echo "✅ Database and RAG initialized"

## Start the full platform (backend + frontend concurrently)
run:
	python scripts/start_all.py

## Start backend only
backend:
	uvicorn influmatch.backend.main:app --reload --port 8000 --host 0.0.0.0

## Start frontend only
frontend:
	streamlit run influmatch/frontend/app.py --server.port 8501 \
		--theme.base dark \
		--theme.primaryColor "#533483" \
		--theme.backgroundColor "#0a0a1a" \
		--theme.secondaryBackgroundColor "#1a1a2e"

## Run all tests with coverage
test:
	pytest influmatch/backend/tests/ -v --tb=short -s \
		--cov=influmatch.backend \
		--cov-report=term-missing \
		--cov-report=html:docs/coverage_report
	@echo "✅ All tests complete"

## Run unit tests only (fast)
test-unit:
	pytest influmatch/backend/tests/unit/ -v --tb=short -s -q

## Run integration tests only
test-integration:
	pytest influmatch/backend/tests/integration/ -v --tb=short -s

## Clean generated files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	rm -f influmatch.db influmatch/influmatch.db
	rm -rf data/chroma_db influmatch/data/chroma_db
	rm -rf docs/coverage_report
	rm -rf logs/*.log
	@echo "✅ Cleaned generated files"

## Full reset — clean + reinitialize
reset: clean init
	@echo "✅ Full platform reset complete"

## Health check
health:
	@curl -s http://localhost:8000/health | python -m json.tool || \
		echo "❌ Backend not running on port 8000"
	@curl -s http://localhost:8501 > /dev/null && \
		echo "✅ Frontend: ONLINE" || echo "❌ Frontend: OFFLINE"

## Docker build + run
docker-up:
	docker-compose up --build -d
	@echo "✅ Docker services started"

docker-down:
	docker-compose down
	@echo "✅ Docker services stopped"

## Lint with ruff (if installed)
lint:
	ruff check influmatch/ --fix || echo "ℹ️  Install ruff: pip install ruff"
