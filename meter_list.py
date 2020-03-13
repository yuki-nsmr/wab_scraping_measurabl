# coding: utf-8
# Create Meter List of All Assets
import urllib3
import pandas as pd
import glob
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
DOWNLOAD_PATH = json_obj['download']['METER_PATH']
OUT_PATH = os.path.join(os.path.curdir, "out_meter")

TODAY_ISO = datetime.date.today().isoformat()


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


def create_meter_list(n):
    """
    n: name of asset
    """
    creation_times = [(f, os.path.getctime(os.path.join(DOWNLOAD_PATH, f))) for f in os.listdir(DOWNLOAD_PATH) if f.endswith(".csv")]
    creation_times.sort(key=lambda x: x[1])  # sort by creation time
    latest_file = creation_times[-1][0]

    df = pd.read_csv(os.path.join(DOWNLOAD_PATH, latest_file))
    df['Asset_name'] = n
    df['Meter_count'] = [i+1 for i in range(len(df))]
    return df


def remove_glob(pathname, recursive=True):
    for p in glob.glob(pathname, recursive=recursive):
        if os.path.isfile(p):
            os.remove(p)


# Empty the content of the folder
pathname = os.path.join(DOWNLOAD_PATH, "*.csv")
remove_glob(pathname)

# driver = webdriver.Chrome()
driver = init_selenium() # ダウンロードしたときに指定のフォルダにファイルが保存されるように
driver.get(HOME_URL)
driver.implicitly_wait(3) # 画面に要素がロードされるまで3秒待つ（ページ読み込みに時間がかかるため）.

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

df_meter = pd.DataFrame()
for u, n, e, f, d, w in zip(df['URL'], df['Name'], df['Electric'], df['Fuel'], df['District'], df['Water']):
    driver.get(u)
    driver.implicitly_wait(10) # 画面に要素がロードされるまで3秒待つ
    print(n, " -- start")

    if e > 0:
        time.sleep(2)
        driver.find_element_by_xpath("//*[@id='electricMeters']/div[1]/div/button").click()
        time.sleep(2)
        df_= create_meter_list(n)
        # df_ = pd.read_excel("")
        df_meter = df_meter.append(df_)

    # Fuel
    if f > 0:
        time.sleep(2)
        # 画面をスクロールしないとダウンロードボタンが画面上に現れないため、スクロールする
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        driver.find_element_by_xpath("//*[@id='fuelMeters']/div[1]/div/button").click()
        time.sleep(2)
        df_= create_meter_list(n)
        df_meter = df_meter.append(df_)

    # District
    if d > 0:
        time.sleep(2)
        # 画面をスクロールしないとダウンロードボタンが画面上に現れないこともあるため、スクロールする
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        driver.find_element_by_xpath("//*[@id='districtMeters']/div[1]/div/button").click()
        time.sleep(2)
        df_= create_meter_list(n)
        df_meter = df_meter.append(df_)

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
        time.sleep(2)
        # 画面をスクロールしないとダウンロードボタンが画面上に現れないためこともあるためスクロールする
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        driver.find_element_by_xpath("//*[@id='waterMeters']/div[1]/div/button").click()
        time.sleep(2)
        df_ = create_meter_list(n)
        df_meter = df_meter.append(df_)

    print("-- done!")


df_meter = df_meter[['Asset_name', 'Meter_count', 'Name', 'Type', 'Serving', 'Readings', 'Last Reading Period']]
df_meter.to_csv(os.path.join(OUT_PATH, "meter_list_{}.csv".format(TODAY_ISO)), index=False)
print("Meter list has been created.")
