OpenAutomatedFarm
=================

Introduction
------------

The goal of this project is to help users grow plants. Keeping plants
alive can be a lot of work and we think that technology can help us
with that. We want to create a system that is flexible and extensible,
so that it can be used to water your cactus once a month but also to
produce food for hundreds of people.

Concept
-------

We try to design a modular system. Sensors and Actuators will be
connected to arduinos that serve as an abstraction layer and all the
regulating algorithms run on a PC (like the beagle bone black or
raspberry pi). A shared database will provide information on ideal
environment settings.

Used Hardware
-------------

We use the arduino family of microcontroller boards with costume
shields and a beagle bone black as PC. Alternativly other PC
hardware can be used.

Used Software
-------------

* For programming the arduinos:
[Ino](http://inotool.org/)
* For designing printed circuit boards (pcb):
[Kicad](http://www.kicad-pcb.org/)
* As database we use:
[MariaDB](https://mariadb.org/)
* For the web-ui:
[Pyramid](http://www.pylonsproject.org/),
[Sqlalchemy](www.sqlalchemy.org/)
[redis-py](https://github.com/andymccurdy/redis-py)
[pyserial](http://pyserial.sourceforge.net/)
* The preffered programming language is:
[Python 3](www.python.org)


Getting Started
---------------

1) Create a virtual python environment

	./setup_virtualenv.sh
	source env34/bin/activate

2) Initialize the database(s)

	initialize_FarmGUI_db

3) Start the workers

	measurement_scheduler &
	measurement_logger &
	periphery_controller_manager &
	periphery_controller_worker /dev/ttyACM0

4) Run pserve

	pserve development.ini --reload

5) start hacking :)

