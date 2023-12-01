# The Duckbot: A system for automated imaging and manipulation of duckweed
This repository hosts files to build and operate a Duckbot, aka a [Jubilee](https://jubilee3d.com/index.php?title=Main_Page) outfitted for use by plant biologists.

_For more details on buidling a Jubilee for lab automation, check out our [science_jubilee](https://github.com/machineagency/science_jubilee/) repository and its [documentation](https://github.com/machineagency/science_jubilee/)!_

## Quickstart Info
### Installation
- Clone this repositository recursively: `git clone --recursive https://github.com/machineagency/duckbot.git`
    - Note that the `--recursive` flag is necessary as this repository relies on [science_jubilee](https://github.com/machineagency/science_jubilee/) 
- We recommend using python virtual environments to handle dependencies. To do this:
  - Move into the new directory: `cd duckbot`
  - Create a virtual environment named `.venv`: `python3 -m venv .venv`
  - Activate the virtual environment: `source .venv/bin/activate` 
  - You should now see `(.venv)` to the left of your command line prompt! (If you wish to leave the virtual environment, type `deactivate` from any directory)
- Make sure you're using the latest version of pip: `python3 -m pip install --upgrade pip`
- Install the science_jubilee package: `python3 -m pip install -e ./science_jubilee`
- Additional requirements have been separated out into two files to avoid installation issues:
  - First install required packages with `python3 -m pip install -r requirements.txt`
  - Then install additional packages without their dependencies: `python3 -m pip install --no-deps -r requirements-no-dep.txt`
- Installation complete! You can launch your Jupyter environment as usual, e.g. `jupyter lab`
 
### Software
The core of the software is a python interface for the Jubilee, intended to be used in Jupyter notebooks to design and run experiments. As a case study, we contribute 4 Jupyter notebooks designed to walk you through setting up and running a duckweed growth assay. The folders are organized as follows:
- `experiments`: This is where experimental definitions and image data are saved. Take a look at `experiments/GrowthAssayCaseStudy` to see the raw setup file and all collected images.
- `notebooks`: Automated duckweed growth assays are scaffolded across the 4 Jupyter notebooks in this folder. Note that this code is intended to run locally on Jubilee's Raspberry Pi; steps 0 (experimental setup) and 3 (data analysis) can be run without a machine. Auxiliary code (for e.g. calibration and other examples) can be found in the subdirectories.
- `science_jubilee`: Our core implementation for operating the machine is found in the [science_jubilee](https://github.com/machineagency/science_jubilee/) repository.


### Hardware
This repository is designed to be used with a Jubilee platform set up with tools and bedplate for laboratory automation. You can read about Jubilee generally at the [project page](https://jubilee3d.com/index.php?title=Main_Page). Information about specific tools used on the Duckbot can be found on the [Wiki](https://github.com/machineagency/science_jubilee/wiki).

### Wetware and labware
The basic functionality supported by this software is for liquid handling and imaging using up to 6 standard size microplates. 


## Troubleshooting
- If you have issues using the installed packaged in your notebook environment, try adding the python kernel explicitly: `python3 -m ipykernel install --user --name=<insert_name_here>`, where you should replace `<insert_name_here>` with any name you'd like. You can then select this kernel in the top-right of you Jupyter notebook.




