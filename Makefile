all: auxitems pyflakes mypy test

auxitems:
	python make_komauxitems

clean:
	rm -rf dist

dist:
	rm -rf dist
	python3 setup.py sdist

pyflakes:
	pyflakes ./pylyskom
	pyflakes ./tests

mypy:
	mypy ./pylyskom

test: pyflakes mypy
	pytest -vv --maxfail 1 ./tests
	tox

smoketest:
	pytest -vv -s --run-smoketests ./tests/smoketests

.PHONY: all auxitems clean dist test smoketest pyflakes mypy
