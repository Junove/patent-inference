.PHONY: test test-backend test-frontend

test: test-backend test-frontend

test-backend:
	cd backend && uv run pytest

test-frontend:
	@if [ -f frontend/package.json ]; then cd frontend && npm test; else echo "No frontend/package.json yet; skipping."; fi
