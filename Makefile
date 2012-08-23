.PHONY: clean clean-pyc test upload docs

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
	rm -rf tests/__pycache__
	py.test tests
	rm -rf tests/__pycache__

upload: clean
	python setup.py sdist upload

docs:
	cd docs; rm -rf build; clay build
	rm _pages/*.html
	rm -rf _pages/images
	rm -rf _pages/scripts
	rm -rf _pages/styles
	cp -r docs/build/html/* _pages
	cd _pages; git add .; git commit -m "Update pages"; git push origin gh-pages
	git add _pages; git commit -m "Update pages"; git push origin master
