# wab_scraping_measurabl
Script for Measurabl

Read Me

This is the repository to download all the meter readings into Measurabl.

1. How to use

(1) Run meter_list.ipynb

(2) Run get_meter_readings.ipynb

(3) Get final output in a directory "out_meter_readings"


2. Directory tree
<pre>
.
├─config.json
├─download_meter
├─download_meter_readings
├─out_meter
├─out_meter_readings
├─chromedriver.exe
├─get_meter_readings.py
├─meter_list.py
└─measurabl_sites_meter.xlsx
</pre>

[Directory]

* download_meter
Invidiaul meter list by asset.

* download_meter_readings
Individual reading data by meter of the asset.

* out_meter
Combined meter list. Output of meter_list.py

* out_meter_readings
Combined meter reading data by utility; electric, fuel, district and water.
Output of get_meter_readings.py

[Script]

meter_list.ipynb
get_meter_readings.ipynb


[Master file]
measurabl_sites_meter.xlsx

