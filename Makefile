default: all

all: install run

install:
	pip3 install matplotlib
	pip3 install numba

debug:
	bash runner.bash

run:
	python3 main.py