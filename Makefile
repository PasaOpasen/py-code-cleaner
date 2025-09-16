

pytest:
	python -m pytest tests/

venv:
	python3 -m venv venv
	venv/bin/pip install -r requirements-dev.txt

