all: test

auxitems:
	python make_komauxitems

pyflakes:
	pyflakes ./pylyskom
	pyflakes ./tests

test: pyflakes
	py.test --maxfail 1 ./tests

.PHONY: auxitems test pyflakes
