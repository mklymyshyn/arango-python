
.PHONY: coverage doc tests test fast one
.DEFAULT: raw

CLIENTS=urllib2client.Urllib2Client pycurlclient.PyCurlClient
-include Makefile.local


coverage:
	@echo "Starting ..."
	INTEGRATION=1 nosetests -v \
		--cover-html \
		--cover-html-dir=./coverage \
		--with-coverage --cover-package=arango

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

