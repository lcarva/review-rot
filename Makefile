
deps:
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install .

CONFIG ?= ~/.reviewrot.yaml

run:
	review-rot -c $(CONFIG) -f json --debug | tee docs/data.json

view:
	cd docs && python -m http.server 8000

build:
	podman build -t review-rot:local .

fmt:
	@pip -q install black && black bin/review-rot .

.PHONY: deps run view build fmt
