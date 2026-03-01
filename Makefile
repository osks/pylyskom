all: auxitems pyflakes test

auxitems:
	uv run python make_komauxitems

clean:
	rm -rf dist

dist:
	rm -rf dist
	uv build

pyflakes:
	uv run --with pyflakes pyflakes ./pylyskom ./tests

test: pyflakes
	uv run --with pytest pytest -vv --maxfail 1 ./tests

test-e2e:
	bash e2e/run.sh

.PHONY: all auxitems clean dist test test-e2e pyflakes
