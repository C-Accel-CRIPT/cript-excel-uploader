from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import subprocess
import time

from selenium.webdriver.common.by import By

# Specify the path to the ChromeDriver executable
chrome_driver_path = r'C:\Program Files\Google\Chrome\Application\chrome.exe'

# Start the Chrome browser in app mode
driver = webdriver.Chrome()

driver.maximize_window()

driver.get("http://localhost:8001/templates/base.html")

# fill out the form
element = driver.find_element(By.ID, "host-input")
element.send_keys('criptapp.org')

element = driver.find_element(By.ID, "api-token-input")
element.send_keys('this is my super secret token')

element = driver.find_element(By.ID, "project-name")
element.send_keys('my project name')

element = driver.find_element(By.ID, "collection-name")
element.send_keys('my collection')

element = driver.find_element(By.ID, "excel-file-path")
driver.execute_script("arguments[0].removeAttribute('disabled');", element)
element.send_keys('hello world!')

element = driver.find_element(By.ID, "upload-button")

# submit the form
element.click()

# wait and do not close browser so we can see what happened for a bit
time.sleep(1000)
