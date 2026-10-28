.PHONY: validate test guard

validate: test guard

test:
	python3 -m unittest discover -s tests

guard:
	python3 -m versionguard check
