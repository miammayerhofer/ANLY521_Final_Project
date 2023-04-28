import logging
import os
import argparse
import time
import pandas as pd  
import numpy as np

from bs4 import BeautifulSoup   
from selenium import webdriver         
from selenium.webdriver.common.by import By    
from webdriver_manager.chrome import ChromeDriverManager

def setup_logger(log_file_name, log_dir_path):
    """ Function for logging this script """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    log_file_path = os.path.join(log_dir_path, log_file_name)
    file_handler = logging.FileHandler(log_file_path)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger

def scrape_table(url):
    """ Function to scrape the ACLU table of anti-LGBTQ+ bills """
    # Start a new Chrome web driver and got to input website
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get(url)
    # Locate table and get its HTML
    element = driver.find_element(By.XPATH, "/html/body/div/div[4]/div/section[1]/div/div/div[2]/div[4]/div")
    table_html = element.get_attribute("innerHTML")
    # Quit driver and return the HTML
    driver.quit()
    return table_html

def get_table_info(html):
    """ Function to extract the information from the ACLU table into a data frame """
    # Convert table to a soup object and store all the rows (tr tags) * remove the first one
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.find_all("tr")
    rows.pop(0)
    #row_soup = BeautifulSoup(str(rows), "html.parser")
    # Loop through the rows and get state, link, name, category, and status information
    states, links, names, categories, statuses = [], [], [], [], []
    cat_class_names = ["slt-pill slt-pill__school mr-xxs", "slt-pill slt-pill__speech mr-xxs", "slt-pill slt-pill__health mr-xxs",
        "slt-pill slt-pill__other mr-xxs", "slt-pill slt-pill__public mr-xxs", "slt-pill slt-pill__rights mr-xxs", "slt-pill slt-pill__ids mr-xxs"]
    for i in range(len(rows)):
        specific_bill_data = rows[i]
        states.append(specific_bill_data.find("div", class_ = "pl-none").text)
        url_tag = specific_bill_data.find("a", class_ = "is-block-mobile mb-sm-mobile")
        if url_tag == None: 
            links.append(np.NAN)
            finding_name = specific_bill_data.find("span", class_ = "is-block-mobile")
            names.append(finding_name.text.strip().replace(".", "").replace(" ", ""))
        else: 
            links.append(url_tag["href"])
            names.append(url_tag.text.strip())
        for c_name in cat_class_names:
            cat_element = specific_bill_data.find("div", class_ = c_name)
            if cat_element == None: continue
            else: 
                categories.append(cat_element.text.strip())
                break
        status_tag = specific_bill_data.find("div", class_ = "bill-status-description is-size-7")
        statuses.append(status_tag.text.strip())
    # Put lists into a dictionary form and convert to data frame
    data = {"state": states, "link": links, "bill_name": names, "category": categories, "status": statuses}
    return pd.DataFrame(data)



if __name__ == "__main__":

    startTime = time.time()
    timeTag = time.strftime('%Y%m%d_%H_%M_%S')

    # Read arguments
    parser = argparse.ArgumentParser(description = "Code to read in the bills from the ACLU")
    parser.add_argument("-o", "--outdir", required = True, help = "Path to logging")
    args = parser.parse_args()

    # Begin logger
    logger = setup_logger(f"log_{timeTag}.log", args.outdir)
    logger.info("Running ACLU table scraper script.")
    logger.info(f"Output directory: {args.outdir}")

    # Run web driver with this link
    aclu_url = "https://www.aclu.org/legislative-attacks-on-lgbtq-rights?impact=&state="
    logger.info("Converting the HTML of the ACLU table to a data frame.")
    aclu_table_html = scrape_table(aclu_url)
    # Make a data frame from the information
    df = get_table_info(aclu_table_html)
    logger.info(f"\n{df}")
    # Convert to csv file
    df.to_csv("../modified_data/aclu_table_data.csv", index = False)


