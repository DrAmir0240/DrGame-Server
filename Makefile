ENV ?= dev
COMPOSE_FILE = docker-compose.$(ENV).yml

# ── Colors ────────────────────────────────────
CYAN  = \033[0;36m
RESET = \033[0m

.PHONY: help build build-no-cache up up-build down restart \
        logs logs-app logs-db logs-redis shell db-shell redis-shell \
        migrate migrate-create migrate-down migrate-history \
        backup restore ps clean fclean

# ── Default target ────────────────────────────
help:
	@echo ""
	@echo "$(CYAN)DrGame ERP — Available commands$(RESET)"
	@echo ""
	@echo "  make build              Build images (ENV=dev|prod)"
	@echo "  make up                 Start containers in background"
	@echo "  make down               Stop and remove containers"
	@echo "  make restart            Restart all containers"
	@echo "  make logs               Follow all logs"
	@echo "  make logs-app           Follow app logs only"
	@echo "  make logs-db            Follow db logs only"
	@echo "  make logs-redis         Follow redis logs only"
	@echo "  make shell              Open bash shell in app container"
	@echo "  make db-shell           Open psql in db container"
	@echo "  make redis-shell        Open redis-cli in redis container"
	@echo "  make migrate            Run python manage.py migrate"
	@echo "  make migrate-create app= Create new Django migration (makemigrations)"
	@echo "  make backup             Dump database to ./backup/"
	@echo "  make restore f=         Restore DB from file (f=filename)"
	@echo "  make ps                 Show running containers"
	@echo "  make clean              Remove stopped containers"
	@echo "  make fclean             Remove containers + volumes (DANGER)"
	@echo ""
	@echo "  ENV=dev (default) | ENV=prod"
	@echo ""

# ── Build ─────────────────────────────────────
build:
	docker compose -f $(COMPOSE_FILE) build

build-no-cache:
	docker compose -f $(COMPOSE_FILE) build --no-cache

# ── Up / Down / Restart ───────────────────────
up:
	docker compose -f $(COMPOSE_FILE) up -d

up-build:
	docker compose -f $(COMPOSE_FILE) up -d --build

down:
	docker compose -f $(COMPOSE_FILE) down

restart:
	docker compose -f $(COMPOSE_FILE) restart

# ── Logs ──────────────────────────────────────
logs:
	docker compose -f $(COMPOSE_FILE) logs -f

logs-app:
	docker compose -f $(COMPOSE_FILE) logs -f app

logs-db:
	docker compose -f $(COMPOSE_FILE) logs -f db

logs-redis:
	docker compose -f $(COMPOSE_FILE) logs -f redis

# ── Shell ─────────────────────────────────────
shell:
	docker exec -it drgame_app bash

db-shell:
	docker exec -it drgame-db psql -U $${POSTGRES_USER} -d $${POSTGRES_DB}

redis-shell:
	docker exec -it drgame-redis redis-cli

# ── Migrations (Django) ───────────────────────
migrate:
	docker exec -it drgame_app python manage.py migrate

migrate-create:
	@if [ -z "$(app)" ]; then echo "Usage: make migrate-create app='app_name'"; exit 1; fi
	docker exec -it drgame_app python manage.py makemigrations $(app)

migrate-down:
	@if [ -z "$(app)" ] || [ -z "$(name)" ]; then echo "Usage: make migrate-down app='app_name' name='migration_name'"; exit 1; fi
	docker exec -it drgame_app python manage.py migrate $(app) $(name)

migrate-history:
	docker exec -it drgame_app python manage.py showmigrations

# ── Backup / Restore ──────────────────────────
backup:
	@mkdir -p ./backup
	docker exec drgame-db pg_dump -U $${POSTGRES_USER} $${POSTGRES_DB} \
		> ./backup/backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "$(CYAN)Backup saved to ./backup/$(RESET)"

restore:
	@if [ -z "$(f)" ]; then echo "Usage: make restore f=backup/filename.sql"; exit 1; fi
	docker exec -i drgame-db psql -U $${POSTGRES_USER} -d $${POSTGRES_DB} < $(f)
	@echo "$(CYAN)Restore done from $(f)$(RESET)"

# ── Status ────────────────────────────────────
ps:
	docker compose -f $(COMPOSE_FILE) ps

# ── Cleanup ───────────────────────────────────
clean:
	docker compose -f $(COMPOSE_FILE) rm -f

fclean:
	@echo "WARNING: This will delete all volumes and data!"
	@read -p "Are you sure? [y/N] " confirm && [ "$$confirm" = "y" ]
	docker compose -f $(COMPOSE_FILE) down -v
	docker image prune -f
