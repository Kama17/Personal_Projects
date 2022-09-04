import json
from selenium import webdriver
import pandas as pd
from openpyxl import load_workbook

driver = webdriver.Edge('Path to the msedgedriver')
driver.get("URL to the university login page")
driver.find_element_by_id("username").send_keys("xxxx")
driver.find_element_by_id ("password").send_keys("xxxx")
driver.find_element_by_name("Proceed1").click()
driver.get("URL to the lab webside")
driver.implicitly_wait(5)
driver.switch_to.frame("htmlactivity_iframe")

sensor_elapsed = driver.find_element_by_id("sensor-elapsed").text
sensor_reading = driver.find_element_by_id("sensor-reading").text
sensor_temp = driver.find_element_by_id("sensor-temp").text
sensor_date = driver.find_element_by_id("sensor-date").text

book = load_workbook('Path to the Excle spreatshee')
sheet = book.worksheets[0]
sheet.append([sensor_elapsed,sensor_reading,sensor_temp,sensor_date])
book.save('Path to the Excle spreatsheet')

driver.quit()


