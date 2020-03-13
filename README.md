# wab_scraping_measurabl
This is the repository to download all the meter readings into Measurabl.
Measurabl is a ESG software for commercial real estate. (https://www.measurabl.com/)
It helps to keep track of asset information, meter information, usage amount, utility cost etc as well as to create reports.  

## Usage

(1) Run meter_list.ipynb

(2) Run get_meter_readings.ipynb

(3) Get final output in a directory "out_meter_readings"


## Directory tree
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

### Directory

* download_meter
Invidiaul meter list by asset.

* download_meter_readings
Individual reading data by meter of the asset.

* out_meter
Combined meter list. Output of meter_list.py

* out_meter_readings
Combined meter reading data by utility; electric, fuel, district and water.
Output of get_meter_readings.py

### Script

meter_list.ipynb
get_meter_readings.ipynb

### Master file
measurabl_sites_meter.xlsx

