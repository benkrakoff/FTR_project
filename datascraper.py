import os
import sys
import selenium
import time
import shutil
from datetime import datetime as dt
from datetime import timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def main(argv):
	"""
	Webscraper for data from PJM Data Miner, works with Chrome.
	-------
	run the command
	py datascraper.py downloads_dir destination_dir start_date end_date

	downloads_dir is the path to the folder Chrome downloads to
	destination_dir is the path to the folder to store the data

	start_date is the date to start collecting data - must be given as MM/DD/YYYY
	end_date is the date to stop collecting data (inclusive)
	"""

	download_folder = argv[1]
	destination_folder = argv[2]
	start_date = dt.strptime(argv[3],'%m/%d/%Y')
	end_date = dt.strptime(argv[4], '%m/%d/%Y')

	#Open up webdriver
	driver = webdriver.Chrome()
	driver.get('https://dataminer2.pjm.com/feed/da_hrl_lmps')

	#XML Paths to desired objects on page
	box1_XPATH = "/html/body/app-root/main/dm-feed/div/div[2]/feed-grid/div/div[1]/datepicker-list/div/div[2]/div/input"
	box2_XPATH = "/html/body/app-root/main/dm-feed/div/div[2]/feed-grid/div/div[1]/datepicker-list/div/div[3]/div/input"
	submit_XPATH = "/html/body/app-root/main/dm-feed/div/div[2]/feed-grid/div/div[1]/datepicker-list/div/div[4]/button[1]"
	export_XPATH = "/html/body/app-root/main/dm-feed/div/div[2]/feed-grid/div/div[1]/div/dm-feed-download-link/a/span"
	end_time_XPATH = '/html/body/app-root/main/dm-feed/div/div[2]/feed-grid/div/div[1]/datepicker-list/div/div[3]/timepicker/div/div/button[2]'

	#Find elements on web page
	delay = 30 #seconds
	box1 = WebDriverWait(driver,delay).until(EC.presence_of_element_located((By.XPATH, box1_XPATH)))
	box2 = WebDriverWait(driver,delay).until(EC.presence_of_element_located((By.XPATH, box2_XPATH)))
	end_time_button = WebDriverWait(driver,delay).until(EC.element_to_be_clickable((By.XPATH, end_time_XPATH)))   
	submit_button = WebDriverWait(driver,delay).until(EC.presence_of_element_located((By.XPATH, submit_XPATH)))
	export_button = WebDriverWait(driver,delay).until(EC.presence_of_element_located((By.XPATH, export_XPATH)))
	
	#Lower end time to 23:45
	end_time_button.click()

	args = [download_folder,destination_folder,driver, box1, box2, submit_button, export_button]

	current_date = start_date

	while current_date <= end_date:
		print("Downloading data for " + current_date.strftime('%m/%d/%Y'))
		download(current_date,*args)
		current_date += timedelta(days=1)

def download(date, download_folder, destination_folder, driver, box1, box2, submit_button, export_button):

	#Input dates
	box1.clear()
	box1.send_keys(date.strftime('%m/%d/%Y'))
	box2.clear()
	box2.send_keys(date.strftime('%m/%d/%Y'))

	time.sleep(1) #Wait for buttons to be clickable
	submit_button.click()
	export_button.click()

	#Wait 1 minute for download to finish
	start_time = time.mktime(time.gmtime())
	while time.mktime(time.gmtime()) - start_time < 60:
		if 'da_hrl_lmps.csv' in os.listdir(download_folder):
			#Move to desired folder
			time.sleep(.1) #Give file a bit of time to arrive
			shutil.move(download_folder + '/da_hrl_lmps.csv', destination_folder + '/da_hrl_lmps_'+date.strftime('%m_%d_%Y') + '.csv')
		else:
			time.sleep(1)

	if time.mktime(time.gmtime()) - start_time > 60:
		raise NotImplemented

if __name__ == '__main__':
	main(sys.argv)
