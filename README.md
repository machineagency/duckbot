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

## Hardware
This set of scripts is designed to be used in conjunction with a Jubilee automation platform set up with tools and bedplate for laboratory automation. You can read about Jubilee generally at https://jubilee3d.com/index.php?title=Main_Page , and details about the set-up specifics for the duckweed growth assay workflow can be found in the paper describing our work (TO BE ADDED)

## Software
The core of the software is a set of 4 Jupyter notebooks designed to walk you through setting up and running a duckweed growth assay. These are supported by a set of 'utils' containing methods accessed within the notebooks, as well as 'ConfigFiles' defining specific variables referred to within the notebooks. You can read more about the nobteooks and how to use them in the wiki of this Github project. 

The scripts are set up with the assumption that you will fork this github repo and then create clones on any computers you want to use as part of your workflow. The Jubilee machine itself is controlled through an on-board raspberry pi computer but you'll likely want to analyse the date on another computer. So there is a folder structure set up in this repo to house image files and experimental set up config files. 

## Wetware and labware
The basic experimental structure supported by this software is X different duckweed genotypes x Y different media compositions, and then measuring growth rates in frond area over time. The default set up is that plants are grown in individual wells of 24-well plates. There are 5 available plate positions on the machine allowing for maximum 120 samples. The duckweed and media can be transferred into these experimental plates from any labware that can fit in the profile of a microplate and has walls that are low enough to allow the Jubilee tool arm to fully dip inside. 


