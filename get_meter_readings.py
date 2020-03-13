# coding: utf-8
# Get Meter Readings for all the meters
import urllib3
import pandas as pd
import glob
import urllib.request as req
import certifi
import re
import time
import datetime
import os
import json
from selenium import webdriver
import chromedriver_binary
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests

# Config
HOME_URL = 'https://app.measurabl.com/' # ログインサイト

# login info
json_file = open('config.json', 'r')    # ファイルを開く
json_obj  = json.load(json_file)    # JSONを読み込む
USER = json_obj['login']['USER']
PW = json_obj['login']['PASSWORD']

# Master (Asset name & the number of meters)
df = pd.read_excel('measurabl_sites_meter.xlsx')

# PATH
DOWNLOAD_PATH = json_obj['download']['METER_READINGS_PATH']
OUT_PATH = os.path.join(os.path.curdir, "out_meter_readings")
OUT_METER = os.path.join(os.path.curdir, "out_meter")

TODAY_ISO = datetime.date.today().isoformat()


def get_meter_list():
    """
    Read meter list and return as dataframe
    """
    f = sorted(os.listdir(OUT_METER))[-1]
    df = pd.read_csv(os.path.join(OUT_METER, f))
    return df


def init_selenium():
    """
    指定したフォルダにダウンロードできるように設定（Windows環境）
    Setting the option of Chrome
    """
    chop = webdriver.ChromeOptions()
    prefs = {"download.default_directory" : DOWNLOAD_PATH}
    chop.add_experimental_option("prefs",prefs)
    chop.add_argument('--ignore-certificate-errors') #SSLエラー対策
    driver = webdriver.Chrome(options = chop)

    return driver


def create_datapoint_list(n, i, df_meter, category):
    """
    Read a latest downloaded file
    n: name of asset
    i: count number, larger or equal to 1
    df_meter: meter_list
    category: "Electric" or "Gas" or "Hot Water" or "Water"
    """
    creation_times = [(f, os.path.getctime(os.path.join(DOWNLOAD_PATH, f))) for f in os.listdir(DOWNLOAD_PATH) if f.endswith(".csv")]
    creation_times.sort(key=lambda x: x[1])  # sort by creation time
    latest_file = creation_times[-1][0]

    df = pd.read_csv(os.path.join(DOWNLOAD_PATH, latest_file))
    df['Asset_name'] = n

    # Read meter name
    meters = list(df_meter[(df_meter['Asset_name'] == n) & (df_meter['Type'].str.contains(category))]['Name'])
    df['Meter_name'] = meters[i]
    df['Category'] = category
    return df


def remove_glob(pathname, recursive=True):
    for p in glob.glob(pathname, recursive=recursive):
        if os.path.isfile(p):
            os.remove(p)


def download_meter_readings(n, target, df_meter, category):
    """
    n: the name of asset
    taget: e, f, d, w
    category: "Electric" or "Gas" or "Hot Water" or "Water"
    """
    df_meter = get_meter_list()

    df_target = pd.DataFrame()
    for i in range(target):
        # Click meter name in the table
        time.sleep(2)

        # ページ上部にエラーがある場合、電気のテーブルが見えない場合があるので、Utilityまで移動する。
        element = driver.find_element_by_xpath("//*[@id='contentBody']/div/div/div[2]/div/site-utilities/h3")
        actions = ActionChains(driver)
        actions.move_to_element(element)
        actions.perform()

        if category == "Electric":
            elem = '//*[@id="electricMeters"]/div[2]/div/table/tbody/tr[' + str(i+1) + ']/td[2]/span'
        elif category == "Gas":
            elem = '//*[@id="fuelMeters"]/div[2]/div/table/tbody/tr[' + str(i+1) + ']/td[2]/span'
        elif category == "Hot Water":
            elem = '//*[@id="districtMeters"]/div[2]/div/table/tbody/tr[' + str(i+1) + ']/td[2]/span'
        elif category == "Water":
            elem = '//*[@id="waterMeters"]/div[2]/div/table/tbody/tr[' + str(i+1) + ']/td[2]/span'

        driver.find_element_by_xpath(elem).click()
        time.sleep(2)

        # 画面をスクロールしないとダウンロードボタンが画面上に現れないことがあるため、スクロールする
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Choose "Full History"
        # エレメントを取得
        period_elem = driver.find_element_by_name('consistencyGraphSelect')
        # 取得したエレメントをSelectタグに対応したエレメントに変化させる
        period_select_element = Select(period_elem)
        # 選択したいvalueを指定する
        period_select_element.select_by_value('Full History')

        driver.find_element_by_xpath('//*[@id="meterReadings"]/div[1]/div/button').click()    # Download data
        driver.find_element_by_xpath("//*[@id='meterProfile']/div/div[1]/button/i").click()    # click × icon to close the individual meter page
        time.sleep(3)

        df_= create_datapoint_list(n, i, df_meter, category)    # Read data
        df_target = df_target.append(df_)
    return df_target


def convert_to_datetime(df):
    """
    convert data type from object to datetime
    """
    df['Period Start'] = pd.to_datetime(df['Period Start'])
    df['Period End'] = pd.to_datetime(df['Period End'])
    return df


# 準備として、ダウンロード先のフォルダの中を空にする
pathname = os.path.join(DOWNLOAD_PATH, "*.csv")
remove_glob(pathname)

# driver = webdriver.Chrome()
driver = init_selenium()
driver.get(HOME_URL)
driver.implicitly_wait(3) # 画面に要素がロードされるまで3秒待つ（ページを開いた直後には指定したい要素が読み込まれないことがあるため）

# ログインする
elem = driver.find_element_by_id("user_email")
elem.clear()
elem.send_keys(USER)

elem = driver.find_element_by_id("user_password")
elem.clear()
elem.send_keys(PW)

# ログインボタンを選択して、クリックする
elem = driver.find_element_by_xpath("//button[@type='submit'][@class=' btn btn-success']")
elem.click()

# オリエンテーションの画面が出るまで10秒待つ
time.sleep(10)

# オリエンテーションのポップアップが出るので、escapeで閉じる
webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()

# driver = webdriver.Chrome()
df_electric_datapoint = pd.DataFrame()
df_fuel_datapoint = pd.DataFrame()
df_district_datapoint = pd.DataFrame()
df_water_datapoint = pd.DataFrame()
texts = []
for u, n, e, f, d, w in zip(df['URL'], df['Name'], df['Electric'], df['Fuel'], df['District'], df['Water']):
    driver.get(u)
    driver.implicitly_wait(10) # 画面に要素がロードされるまで3秒待つ（ページを開いた直後には指定したい要素が読み込まれないことがあるため）
    print(n, " -- start")

    # Electric
    if e > 0:
        time.sleep(2)
        df_e = download_meter_readings(n, e, df_meter, category="Electric")
        time.sleep(2)
        df_electric_datapoint = df_electric_datapoint.append(df_e)

    # Fuel
    if f > 0:
        time.sleep(2)
        # 画面をスクロールしないとFuelテーブルが画面上に現れないため、スクロールする
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        df_f = download_meter_readings(n, f, df_meter, category="Gas")
        time.sleep(2)
        df_fuel_datapoint = df_fuel_datapoint.append(df_f)

    # District
    if d > 0:
        time.sleep(2)
        # ページ上部にエラーが表示されていると、画面をスクロールしないとDistrictテーブルが画面上に現れないため、スクロールする
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        df_d = download_meter_readings(n, d, df_meter, category="Hot Water")
        time.sleep(2)
        df_district_datapoint = df_district_datapoint.append(df_d)

    # Water
    if w > 0:
        time.sleep(2)
        # Waterタブが画面上に現れるように、スクロールアップする
        element = driver.find_element_by_xpath("//*[@id='contentBody']/div/div/div[2]/div/site-utilities/div/sub-nav/nav/ul")
        actions = ActionChains(driver)
        actions.move_to_element(element)
        actions.perform()

        # Waterタブをクリック
        driver.find_element_by_xpath("//*[@id='contentBody']/div/div/div[2]/div/site-utilities/div/sub-nav/nav/ul/li[2]").click()

        df_w = download_meter_readings(n, w, df_meter, category="Water")
        time.sleep(2)
        df_water_datapoint = df_water_datapoint.append(df_w)

        print("-- done!")
print("All done!")

# Store dataframes
df_electric_datapoint = convert_to_datetime(df_electric_datapoint)
df_electric_datapoint = df_electric_datapoint[['Asset_name', 'Category', 'Meter_name', 'Period Start', 'Period End',
                                               'Usage (kWh)', 'Spend (JPY)', 'Demand (kW)',  'Demand Spend (JPY)']]
df_electric_datapoint.to_csv(os.path.join(OUT_PATH, "data_electric_point_{}.csv".format(TODAY_ISO)), index=False)

df_fuel_datapoint = convert_to_datetime(df_fuel_datapoint)
df_fuel_datapoint = df_fuel_datapoint[['Asset_name', 'Category', 'Meter_name', 'Period Start', 'Period End',
                                       'Usage (GJ)', 'Usage (m³)', 'Usage (thm)', 'Spend (JPY)']]
df_fuel_datapoint.to_csv(os.path.join(OUT_PATH, "data_fuel_point_{}.csv".format(TODAY_ISO)), index=False)

df_district_datapoint = convert_to_datetime(df_district_datapoint)
df_district_datapoint = df_district_datapoint[['Asset_name', 'Category', 'Meter_name', 'Period Start',
                                               'Period End', 'Usage (GJ)', 'Spend (JPY)']]
df_district_datapoint.to_csv(os.path.join(OUT_PATH, "data_district_point_{}.csv".format(TODAY_ISO)), index=False)

df_water_datapoint = convert_to_datetime(df_water_datapoint)
df_water_datapoint = df_water_datapoint[[ 'Asset_name', 'Meter_name', 'Category', 'Period Start', 'Period End',
                                         'Usage (m³)', 'Spend (JPY)']]
df_water_datapoint.to_csv(os.path.join(OUT_PATH, "data_water_point_{}.csv".format(TODAY_ISO)), index=False)

print("Meter reading list has been created.")
