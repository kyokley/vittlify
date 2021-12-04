.PHONY: build build-dev help list up shell down attach

help: ## This help
	@grep -F "##" $(MAKEFILE_LIST) | grep -vF '@grep -F "##" $$(MAKEFILE_LIST)' | sed -E 's/(:).*##/\1/' | sort

list: ## List all targets
	@make -qp | awk -F':' '/^[a-zA-Z0-9][^$$#\/\t=]*:([^=]|$$)/ {split($$1,A,/ /);for(i in A)print A[i]}'

build: ## Build API container with production requirements
	docker build \
		  --build-arg BUILDKIT_INLINE_CACHE=1 \
		  --tag=kyokley/vittlify \
		  --target=prod \
		  .

build-dev: ## Build API container with dev/test requirements
	docker-compose build --parallel

build-node: ## Build node container
	docker-compose build vittlify-node

up: ## Run vittlify on port 8000
	docker-compose up -d

shell: up ## Open a shell into a running vittlify container
	docker-compose exec vittlify /bin/bash

db-up:
	docker-compose up -d postgres

db-shell: db-up
	docker-compose exec postgres /bin/bash

down:
	docker-compose down

fresh: ## Reload a fresh copy of the application
	docker-compose down -v
	docker-compose up -d
	sleep 3
	docker-compose exec vittlify /bin/bash -c 'python manage.py migrate'

attach:
	docker attach $$(docker ps -qf name=vittlify_vittlify_1)
