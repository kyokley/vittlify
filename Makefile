.PHONY: build build-dev help list up shell down attach

DEFAULT_DOCKER_COMPOSE_ARGS=-f docker-compose.yml
PROD_DOCKER_COMPOSE_ARGS=${DEFAULT_DOCKER_COMPOSE_ARGS} -f compose/docker-compose.prod.yml
DEV_DOCKER_COMPOSE_ARGS=${DEFAULT_DOCKER_COMPOSE_ARGS} -f compose/docker-compose.dev.yml

help: ## This help
	@grep -F "##" $(MAKEFILE_LIST) | grep -vF '@grep -F "##" $$(MAKEFILE_LIST)' | sed -E 's/(:).*##/\1/' | sort

list: ## List all targets
	@make -qp | awk -F':' '/^[a-zA-Z0-9][^$$#\/\t=]*:([^=]|$$)/ {split($$1,A,/ /);for(i in A)print A[i]}'

build-prod: ## Build API container with production requirements
	docker-compose ${PROD_DOCKER_COMPOSE_ARGS} build --parallel

build-dev: ## Build API container with dev/test requirements
	docker-compose ${DEV_DOCKER_COMPOSE_ARGS} build --parallel

up-dev: ## Run vittlify on port 8000
	docker-compose ${DEV_DOCKER_COMPOSE_ARGS} up -d

up-prod:
	docker-compose ${PROD_DOCKER_COMPOSE_ARGS} up -d

shell: up-dev ## Open a shell into a running vittlify container
	docker-compose ${DEV_DOCKER_COMPOSE_ARGS} exec vittlify /bin/bash

db-up:
	docker-compose ${DEV_DOCKER_COMPOSE_ARGS} up -d postgres

db-shell: db-up
	docker-compose exec postgres /bin/bash

down:
	docker-compose down

fresh: ## Reload a fresh copy of the application
	docker-compose ${DEV_DOCKER_COMPOSE_ARGS} down -v
	docker-compose ${DEV_DOCKER_COMPOSE_ARGS} up -d
	sleep 3
	docker-compose exec vittlify /bin/bash -c 'python manage.py migrate'

attach:
	docker attach $$(docker ps -qf name=vittlify_vittlify_1)

tests: build-dev ## Run tests
	docker-compose ${DEV_DOCKER_COMPOSE_ARGS} run vittlify /bin/bash -c 'python manage.py test'

check-migrations: build-dev ## Check for missing migrations
	docker-compose ${DEV_DOCKER_COMPOSE_ARGS} run vittlify /bin/bash -c 'python manage.py makemigrations --check'

publish: build-prod ## Publish container image to dockerhub
	docker push kyokley/vittlify
	docker push kyokley/vittlify-node

export SOCKET=/tmp/vittlify-pgdump-socket

db-reload: dropdb createdb ## Dump db for loading locally
	echo SOCKET=${SOCKET}
	echo ALMAGEST_SSH_SERVER=${ALMAGEST_SSH_SERVER}
	ssh -q -M -S $$SOCKET -fnNT -L 5632:localhost:5632 $$ALMAGEST_SSH_SERVER 2>&1 >/dev/null
	docker run \
        --rm -it \
        --net=host \
        -e "PGTZ=America/Chicago" \
        -v "$$HOME/.pgpass:/root/.pgpass" \
        --entrypoint "pg_dump" \
        kyokley/psql \
        -U postgres -h localhost -p 5632 -d postgres | docker run \
        --rm -i \
        --net=host \
        -v "$$HOME/.pgpass:/root/.pgpass" \
        kyokley/psql \
        -U postgres -h localhost postgres
	ssh -q -S $$SOCKET -O exit $$ALMAGEST_SSH_SERVER 2>&1 >/dev/null
