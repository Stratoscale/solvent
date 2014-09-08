all: unittest check_convention

clean:
	rm -fr build dist solvent.egg-info

UNITTESTS=$(shell find tests -name 'test*.py' | sed 's@/@.@g' | sed 's/\(.*\)\.py/\1/' | sort)
COVERED_FILES=solvent/*.py
unittest:
	rm -f .coverage*
	-mkdir build
	ln -sf `pwd`/../osmosis/build/cpp/osmosis.bin build/osmosis
	PATH=`pwd`/build:$$PATH PYTHONPATH=`pwd`:`pwd`/../upseto COVERAGE_FILE=`pwd`/.coverage coverage run --parallel-mode --append -m unittest $(UNITTESTS)
	coverage combine
	coverage report --show-missing --rcfile=coverage.config --fail-under=97 --include='$(COVERED_FILES)'

check_convention:
	pep8 . --max-line-length=109

uninstall:
	-yes | sudo pip uninstall solvent
	sudo rm /usr/bin/solvent

install:
	-yes | sudo pip uninstall solvent
	python setup.py build
	python setup.py bdist
	python setup.py bdist_egg
	sudo python setup.py install
	sudo cp solvent.sh /usr/bin/solvent
	sudo chmod 755 /usr/bin/solvent
	sudo cp bash.completion.sh /etc/bash_completion.d/solvent.sh
