run-collector:
	python3 collector.py

run-api:
	python3 api.py

clean-db:
	echo "drop schema public cascade; create schema public" | psql postgresql://test:test@localhost:5432/test

