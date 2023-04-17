# ==========================================
# This file scrapes the table of anti-LGBTQ+ 
# legislation from the ACLU website to get 
# the information for each bill.
# ==========================================

from selenium import webdriver         
from selenium.webdriver.common.by import By    
import time                                   
from bs4 import BeautifulSoup                 
import pandas as pd                             
import re                                       
from webdriver_manager.chrome import ChromeDriverManager
import numpy as np


def scrape_table(url):
    """ Function to scrape the ACLU table of anti-LGBTQ+ bills """
    # Start a new Chrome web driver
    driver = webdriver.Chrome(ChromeDriverManager().install())
    # Go to website
    driver.get(url)
    # Locate table 
    element = driver.find_element(By.XPATH, "/html/body/div/div[4]/div/section[1]/div/div/div[2]/div[4]/div")
    # Get HTML of just the table
    table_html = element.get_attribute("innerHTML")
    # Quit driver
    driver.quit()
    # Return the html of the table
    return table_html

def get_table_info(html):
    """ Function to extract the information from the ACLU table into a data frame """
    # Convert table to a soup object
    soup = BeautifulSoup(html, "html.parser")
    # Store all the rows (tr tags)
    rows = soup.find_all("tr")
    # Remove the first one (header)
    rows.pop(0)
    # Make a soup object for the rows
    row_soup = BeautifulSoup(str(rows), "html.parser")
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
    # Put lists into a dictionary form, convert to data frame, and save to csv file
    data = {"state": states, "link": links, "bill_name": names, "category": categories, "status": statuses}
    # Return the data as a pandas data frame
    return pd.DataFrame(data)



if __name__ == "__main__":
    aclu_url = "https://www.aclu.org/legislative-attacks-on-lgbtq-rights?impact=&state="
    # Run web driver
    aclu_table_html = scrape_table(aclu_url)
    # Make a data frame from the information
    df = get_table_info(aclu_table_html)
    # Convert to csv file
    df.to_csv("../modified_data/aclu_table_data.csv", index = False)


