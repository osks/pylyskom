all: auxitems test pyflakes

auxitems:
	python make_komauxitems

pyflakes:
	pyflakes ./pylyskom
	pyflakes ./tests

test:
	pytest -vv --maxfail 1 ./tests
	tox

.PHONY: all auxitems test pyflakes
