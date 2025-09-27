.PHONY: dev run test docker

dev:
	pip install -r requirements.txt

run:
	uvicorn src.infer:app --host 0.0.0.0 --port 8080

test:
	python scripts/download_datasets.py --dest data/
	python src/train.py --task classify --small

docker:
	docker build -t cv-agentic-saas-mvp:local .
