project_dir := .
bot_dir := ./src/bot
translations_dir := ./translations

.PHONY: i18n
i18n:
	pybabel extract --input-dirs='$(bot_dir)' -o '$(translations_dir)/messages.pot'
	pybabel init -i $(translations_dir)/messages.pot -d $(translations_dir) -D messages -l ru
	pybabel init -i $(translations_dir)/messages.pot -d $(translations_dir) -D messages -l en

.PHONY: i18n-compile
i18n-compile:
	pybabel compile -d $(translations_dir) -D messages

.PHONY: i18n-update
i18n-update:
	pybabel extract --input-dirs='$(bot_dir)' -o '$(translations_dir)/messages.pot'
	pybabel update -i $(translations_dir)/messages.pot -d $(translations_dir) -D messages

.PHONY: prod-build
prod-build:
	docker compose -f docker/docker-compose-prod.yaml up -d --build

.PHONY: prod-logs
prod-logs:
	docker compose -f docker/docker-compose-prod.yaml logs -f

.PHONY: dev-db
dev-db:
	docker compose -f docker/docker-compose-dev.yaml up -d postgres redis

.PHONY: dev-build
dev-build:
	docker compose -f docker/docker-compose-dev.yaml up -d --build bot

.PHONY: dev-logs
dev-logs:
	docker compose -f docker/docker-compose-dev.yaml logs -f

.PHONY: dev-down
dev-down:
	docker compose -f docker/docker-compose-dev.yaml down

.PHONY: run
run:
	python3 src/main.py