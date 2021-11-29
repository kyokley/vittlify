.PHONY: build build-dev help list up shell down

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
	docker build \
		  --build-arg BUILDKIT_INLINE_CACHE=1 \
		  --build-arg BUILDKIT_INLINE_CACHE=1 \
		  --tag=kyokley/vittlify \
		  --target=dev \
		  .

up: ## Run vittlify on port 8000
	docker-compose up -d

shell:
	docker-compose run vittlify /bin/bash

down:
	docker-compose down
