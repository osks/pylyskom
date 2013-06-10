all: test

auxitems:
	python make_komauxitems

pyflakes:
	pyflakes ./pylyskom

test: pyflakes
	py.test ./pylyskom

.PHONY: auxitems test pyflakes
