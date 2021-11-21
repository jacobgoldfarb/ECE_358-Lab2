default: all

all: install run

install:
	pip3 install matplotlib

debug:
	bash runner.bash

run:
	python3 main.py