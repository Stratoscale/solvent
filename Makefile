all: unittest check_convention

clean:
	rm -fr build dist solvent.egg-info

UNITTESTS=$(shell find tests -name 'test*.py' | sed 's@/@.@g' | sed 's/\(.*\)\.py/\1/' | sort)
COVERED_FILES=solvent/*.py
unittest:
	rm -f .coverage*
	-mkdir build
	ln -sf `pwd`/../osmosis/build/cpp/osmosis.bin build/osmosis
	PATH=`pwd`/build:$$PATH PYTHONPATH=`pwd`:`pwd`/../upseto COVERAGE_FILE=`pwd`/.coverage python2 -m coverage run --append -m unittest $(UNITTESTS)
	python2 -m coverage combine
	python2 -m coverage report --show-missing --rcfile=coverage.config --fail-under=80 --include='$(COVERED_FILES)'

check_convention:
	pep8 . --max-line-length=109

uninstall:
	-sudo python2 -m pip uninstall -y solvent

install: uninstall
	sudo python2 -m pip install -r requirements.txt 
	sudo python2 -m pip install .
