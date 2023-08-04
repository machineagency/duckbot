# Duckbot: Jubilee for Science
This repository hosts files to build and operate a Duckbot, aka a [Jubilee](https://jubilee3d.com/index.php?title=Main_Page) outfitted for use by plant biologists.

_Check out the [Wiki](https://github.com/machineagency/duckbot/wiki) to get started! Documentation is ongoing._

## Quickstart Info
### Installation
This code is intended to run locally on Jubilee's Raspberry Pi.
- Clone this repositository: `git clone https://github.com/machineagency/duckbot.git`
- We recommend using python virtual environments to handle dependencies. To do this:
  - Move into the new directory: `cd duckbot`
  - Create a virtual environment named `.venv`: `python3 -m venv .venv`
  - Activate the virtual environment: `source .venv/bin/activate` 
  - You should now see `(.venv)` to the left of your command line prompt! (If you wish to leave the virtual environment, type `deactivate`)
- Install the python requirements within the virtual environment: `python3 -m pip install -e .`

### Hardware
This repository is designed to be used with a Jubilee platform set up with tools and bedplate for laboratory automation. You can read about Jubilee generally at the [project page](https://jubilee3d.com/index.php?title=Main_Page). Information about specific tools used on the Duckbot can be found on the [Wiki](https://github.com/machineagency/duckbot/wiki).

### Software
The core of the software is a python interface for the Jubilee, intended to be used in Jupyter notebooks to design and run experiments. As a case study, we contribute 4 Jupyter notebooks designed to walk you through setting up and running a duckweed growth assay.

### Wetware and labware
The basic functionality supported by this software is for liquid handling and imaging using up to 6 standard size microplates. 


