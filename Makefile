lint:
	flake8 syntok

type:
	mypy syntok

test:
	pytest syntok

check: lint type test
