
.PHONY: coverage doc tests test fast one
.DEFAULT: raw

CLIENTS=urllib2client.Urllib2Client pycurlclient.PyCurlClient
-include Makefile.local


coverage:
	@echo "Collect coverage ..."
	-rm .coverage
	coverage run --rcfile=coverage.rc -a `type -p nosetests` -v

	$(foreach client,$(CLIENTS),USE_CLIENT=arango.clients.$(client) \
			INTEGRATION=1 NOSMOKE=1 coverage run \
			--rcfile=coverage.rc -a `type -p nosetests` -v; )

	@echo "Building reports"
	coverage report -m --rcfile=coverage.rc
	coverage html --directory=./coverage --title="Arango Coverage Report" \
		--rcfile=coverage.rc

tests: smoke doctest
	$(foreach client,$(CLIENTS),USE_CLIENT=arango.clients.$(client) INTEGRATION=1 NOSMOKE=1 nosetests -v; )

doctest:
ifdef PYTHON_V2
	$(MAKE) -C docs doctest
endif

test: tests

smoke:
	nosetests -v

one:
	INTEGRATION=1 nosetests -v arango.tests.$(DST)

doc:
	cd docs && make clean && make html && \
		rsync -avz build/html/* -e ssh $(DOCS_HOST)

