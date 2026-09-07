# Data archive website for Two-Element Interferometer located at Gauribidanur radio observatory (RRI). Operational between 180-359 MHz with sampling rate of 1.25GS/s.

Procedure to bring up the data archive webpage
----------------------------------------------

## Clone the github repository

gitclone https://github.com/gnpaneendra/twin_webpage.git ~/.

## Directory structure

twin_webpage/
		/twin_webpage.htm
		/twin_webpage.py
		/static/
		         /rrilogo.png
		         /twin.jpg
		/downloads/
		                 /README.pdf
		                 /twin_data_process_combined.py
		                 /twin_data_process_raw.py

## Details on files

1. twin_webpage.htm: This file contains the deisgn of the webpage and interactions (front-end). languages(html, java). Contained path for the combined data (SOLAR_DATA_GBD/combined/) and raw data (SOLAR_DATA_GBD/raw/)
2. twin_webpage.py: This files suports in the zipping the data and forwarding it (back-end). languages(python). Contains the path for the main data directory in this case (SOLAR_DATA_GBD) and twin_webpage.htm
3. rrilogo.png: RRI logo
4. twin.jpg: Image of the Two-Element Radio Interferometer array
5. README.pdf: introdcues to data and initial processing types
6. twin_data_process_combined.py: Python program to process combined file (single csv)
7. twin_data_process_raw.py: Python program to process the raw individual files (multiple CSV files)

## Addition python packages required to be downloaded

flask

## Initiating/Running the webserve

Through VENV and CONDA

## VENV

python3 -m venv ~/venv_twinweb

source activate ~/venv_twinweb/bin/activate

python3 -m pip install flask

screen -S twin_webpage

python3 ~/twin_webpage/twin_webpage.py

The webiste will be up, and the ip adress will be displayed in the terminal

Exit the screen

ctrl + A
ctrl + D

To list/check the status of the screen 
screen -ls

To re-enter the screen

screen -R twin_webpage

## CONDA

conda create --name twinweb

conda activate twinweb

conda install flask

screen -S twin_webpage

python3 ~/twin_webpage/twin_webpage.py

The webiste will be up, and the ip adress will be displayed in the terminal

Exit the screen

ctrl + A
ctrl + D

To list/check the status of the screen 
screen -ls

To re-enter the screen

screen -R twin_webpage
