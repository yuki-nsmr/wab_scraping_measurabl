# wab_scraping_measurabl
Script for Measurabl

Read Me

This is the repository to download all the meter readings into Measurabl.

1. How to use

(1) Modify "DOWNLOAD_PATH" in the script below.
meter_list.ipynb
get_meter_readings.ipynb

(2) Run meter_list.ipynb

(3) Run get_meter_readings.ipynb

(4) You can get final output in a directory "datapoint_list". 


2. Directory tree

├─config.json
├─download_meter
├─download_meter_readings
├─out_meter
├─out_meter_readings
├─chromedriver.exe
├─get_meter_readings.py
├─meter_list.py
└─measurabl_sites_meter.xlsx

[Directory]
* datapoint_list
Combined meter reading data by utility; electric, fuel, district and water.

* download_datapoint
Individual reading data by meter of the asset

* download_meter
Invidiaul meter list by asset

* meter_list
Combined meter list


[Script]

meter_list.ipynb
get_meter_readings.ipynb


[Master file]
measurabl_sites_meter.xlsx

