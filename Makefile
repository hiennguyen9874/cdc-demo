help:
	@echo "  migrate-dev                		Run migrate"
	@echo "  migration-dev              		Run migration"

.PHONY: migrate-dev
migrate-dev:
	@echo "--> Migrate"
	COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 docker-compose run webapp alembic revision --autogenerate

.PHONY: migration-dev
migration-dev:
	@echo "--> Migrate"
	COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 docker-compose run webapp alembic upgrade head
