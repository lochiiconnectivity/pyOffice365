clean-pyc:
	find . -name '*.pyc' -exec rm --force {} +
	find . -name '*.pyo' -exec rm --force {} +
	find . -name '*~' -exec rm --force  {} +

clean-build:
	rm --force --recursive build/
	rm --force --recursive dist/
	rm --force --recursive *.egg-info

test: clean-pyc
	 py.test

test3: clean-pyc
	 py.test-3

coverage:
	 py.test --cov=.

install:
	 python setup.py install

help:
	@echo "    clean-pyc"
	@echo "        Remove python artifacts."
	@echo "    clean-build"
	@echo "        Remove build artifacts."
	@echo "    test"
	@echo "        Run tests."
	@echo "    test3"
	@echo "        Run tests, force python 3."
	@echo "    coverage"
	@echo "        Report on coverage."
	@echo "    install"
	@echo "        Install."
