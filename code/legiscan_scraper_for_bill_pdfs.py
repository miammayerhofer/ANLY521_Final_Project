# =======================================
# Legiscan scraper attempt for bill pdfs 
# from the ACLU table
# File: legiscan_scraper_for_bill_pdfs.py
# Author(s): Mia Mayerhofer
# =======================================

# Import packages
from selenium import webdriver         
from selenium.webdriver.common.by import By   
from selenium.webdriver.support.ui import Select
import time                                   
from bs4 import BeautifulSoup                 
import pandas as pd                             
import re                                       
from webdriver_manager.chrome import ChromeDriverManager
import numpy as np
import requests
import io
import PyPDF2
from pikepdf import Pdf
from pathlib import Path
import pdfminer
import os
import pikepdf

# Read in the table scraped from the ACLU
aclu_bills = pd.read_csv("aclu_bill_data.csv")
aclu_bills.bill_name[23] = "HB 1098"


download_folder = os.path.join(os.getcwd(), "scraped_pdfs")
print(download_folder)
options = webdriver.ChromeOptions()
options.add_experimental_option("prefs", {
    "download.default_directory": download_folder,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
})

# Start a new Chrome web driver
driver = webdriver.Chrome(ChromeDriverManager().install(), options = options)

# Go to website
driver.get("https://legiscan.com/AL/legislation")

urls = []
texts = []

for i in range(1, len(aclu_bills)):
    state = aclu_bills.state[i]
    name = aclu_bills.bill_name[i]
    print("STATE:", state, "    NAME:", name)
    # Select state from dropdown
    dropdown = driver.find_element(By.ID, "edit-state-id")
    select = Select(dropdown)
    select.select_by_visible_text(state)
    # Enter bill number into input box
    driver.find_element(By.ID, "edit-bill-number").clear()
    input_box = driver.find_element(By.ID, "edit-bill-number")
    input_box.send_keys(name)
    # Click search
    driver.find_element(By.ID, "edit-submit").click()
    link = driver.find_element(By.PARTIAL_LINK_TEXT, "bill text")
    href = link.get_attribute('href')
    response = requests.get(href)
    with open(os.path.join(download_folder, os.path.basename(href)), 'wb') as f:
        f.write(response.content)

    """
    # Get the text of the bill
    try: 
        # Try to find the pdf
        driver.find_element(By.PARTIAL_LINK_TEXT, ".pdf")
    except: 
        # If no pdf is found, try to find the html
        print("No PDF found - trying to find HTML.")
        try: 
            driver.find_element(By.PARTIAL_LINK_TEXT, ".html")
        except: 
            print("No HTML found either.")
            texts.append("NOT ABLE TO GET TEXT")
        else:
            print("HTML found!")
            # Click on html
            html = driver.find_element(By.PARTIAL_LINK_TEXT, ".html")
            texts.append(html.text)
    else:
        print("PDF found!")
        # Click on pdf
        driver.find_element(By.PARTIAL_LINK_TEXT, ".pdf").click()
        pdf_content = requests.get(driver.current_url).content
        print(pdf_content)
    with pikepdf.open(io.BytesIO(pdf_content)) as pdf:
        text = ''
        for page in pdf.pages:
            text += page.extract_text()
        texts.append(text)
    
    response = requests.get(pdf_url)
    #with pdfplumber.open(io.BytesIO(response.content)) as pdf:
    #    text = ""
    #    for page in pdf.pages:
    #        text += page.extract_text()
    pdf_file_name = state + "_" + name.strip() + ".pdf"
    path1 = os.path.join(os.getcwd(), "scraped_pdfs")
    filepath = os.path.join(path1, pdf_file_name)
    with open(filepath, "wb") as pdf_object:
            pdf_object.write(response.content)
            print(f'{pdf_file_name} was successfully saved!')
    driver.find_element(By.PARTIAL_LINK_TEXT, ".pdf").click()
    # extract the bytes from the PDF content
    pdf_bytes = driver.execute_script("return document.getElementsByTagName('iframe')[0].contentWindow.document.body.innerHTML")
"""
    driver.back()
driver.quit()



