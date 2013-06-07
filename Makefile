all: test

pyflakes:
	pyflakes ./pylyskom

test: pyflakes
	py.test ./pylyskom

.PHONY: test pyflakes
