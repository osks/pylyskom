all: auxitems test pyflakes

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

test:
	pytest -vv --maxfail 1 ./tests
	tox

smoketest:
	pytest -vv -s --run-smoketests ./tests/smoketests

.PHONY: all auxitems clean dist test smoketest pyflakes
