
.PHONY: coverage
.DEFAULT: raw

-include Makefile.local

export INTEGRATION=1


coverage:
	@echo "Starting ..."
	INTEGRATION=1 nosetests -v \
		--cover-html \
		--cover-html-dir=./coverage \
		--with-coverage --cover-package=arango

tests:
	INTEGRATION=1 nosetests -v

test: tests

fast:
	nosetests -v

one:
	INTEGRATION=1 nosetests -v arango.tests.$(DST)

doc:
	cd docs && make clean && make html && \
		rsync -avz build/html/* -e ssh $(DOCS_HOST)

%:
	@echo Test: "$*"
	@echo
	@echo "$*" | sed 's#(##g; s#)##g;' | \
		awk '{printf("%s.%s", $$2, $$1)}' | \
		sed 's#.Test#:Test#g'
	@echo