all: unittest check_convention

clean:
	rm -fr build dist solvent.egg-info

UNITTESTS=$(shell find tests -name 'test*.py' | sed 's@/@.@g' | sed 's/\(.*\)\.py/\1/' | sort)
COVERED_FILES=solvent/*.py
unittest:
	rm -f .coverage*
	-mkdir build
	ln -sf `pwd`/../osmosis/build/cpp/osmosis.bin build/osmosis
	PATH=`pwd`/build:$$PATH PYTHONPATH=`pwd`:`pwd`/../upseto COVERAGE_FILE=`pwd`/.coverage python -m coverage run --parallel-mode --append -m unittest $(UNITTESTS)
	python -m coverage combine
	python -m coverage report --show-missing --rcfile=coverage.config --fail-under=94 --include='$(COVERED_FILES)'

check_convention:
	pep8 . --max-line-length=109

uninstall:
	-yes | sudo pip uninstall solvent
	-sudo rm -f /etc/bash_completion.d/solvent.sh
	-sudo rm /usr/bin/solvent

install: uninstall
	python setup.py build
	python setup.py bdist
	python setup.py bdist_egg
	sudo pip install ./
