

pytest:
	python -m pytest tests/

wheel:
	venv/bin/python setup.py develop
	venv/bin/python setup.py sdist
	venv/bin/python setup.py bdist_wheel

wheel-push:
	bash wheel-push.sh

pypi-package: wheel wheel-push


