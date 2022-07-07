# Duckbot: Jubilee for Science
This repository hosts files to build and operate a Duckbot, aka a Jubilee outfitted for use by plant biologists.

Documentation to come!

## Installation
- Clone this repositository: `git clone https://github.com/machineagency/duckbot.git`
- We recommend using python virtual environments to handle dependencies. To do this:
  - Move into the new directory: `cd duckbot`
  - Create a virutal environment named `.venv`: `python3 -m venv .venv`
  - Activate the virtual environment: `source .venv/bin/activate` 
  - You should now see `(.venv)` to the left of your command line prompt! (If you wish to leave the virtual environment, type `deactivate`)
- Install the python requirements within the virtual environment: `python3 -m pip install -r requirements.txt`
  - _Note_: If you are using a Raspberry Pi (e.g. the Pi already on your Jubilee), installing opencv can be finicky. You may have to install additional packages).

