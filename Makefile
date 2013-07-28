.PHONY: clean clean-pyc test publish

all: clean clean-pyc test

clean: clean-pyc
	rm -rf build
	rm -rf dist
	rm -rf *.egg-info
	find . -name '.DS_Store' -exec rm -f {} \;
	find . -name '*~' -exec rm -f {} \;

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} \;
	find . -name '*.pyo' -exec rm -f {} \;

test:
	py.test tests

publish: clean
	python setup.py sdist upload
