all: test

test:
	py.test ./pylyskom

.PHONY: test
