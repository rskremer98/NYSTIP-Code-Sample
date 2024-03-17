#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 19 13:28:20 2023

@author: rohanold
"""

import pandas as pd
import os
import requests
from bs4 import BeautifulSoup
import csv


csv.register_dialect('semicolon-delimited', delimiter=';')

os.chdir("/Users/rohankremerguha_1/Documents/GitHub/final-project-rskg")

def prep_downloaded_files():
    # Code below prepares median household income file for text processing
    income_and_unemployment = pd.read_excel("data/UnemploymentReport.xlsx", skiprows = 2)
    income_and_unemployment = income_and_unemployment.iloc[:-2]
    income_and_unemployment = income_and_unemployment.dropna(axis = 1)
    income_and_unemployment = income_and_unemployment.rename(columns = {"Name":"County"})
    income_and_unemployment["County"] = income_and_unemployment["County"].str.replace(" County, NY", "")
    income_and_unemployment["County"] = income_and_unemployment["County"].str.upper()
    income_and_unemployment = income_and_unemployment.iloc[1:]
    
    # Code below prepares nonwhite population file preparation for text processing
    nonwhite_stats = pd.read_csv("data/cc-est2022-alldata-36.csv")
    nonwhite_stats["White Population"] = (nonwhite_stats["WA_MALE"]+nonwhite_stats["WA_FEMALE"])-(nonwhite_stats["HWAC_MALE"]+nonwhite_stats["HWAC_FEMALE"])
    nonwhite_stats["Nonwhite Population"] = nonwhite_stats["TOT_POP"]-nonwhite_stats["White Population"]
    nonwhite_stats["Nonwhite Population Share"] = nonwhite_stats["Nonwhite Population"]/nonwhite_stats["TOT_POP"]
    nonwhite_stats["CTYNAME"] = nonwhite_stats["CTYNAME"].str.upper()
    nonwhite_stats["CTYNAME"] = nonwhite_stats["CTYNAME"].str.replace(" COUNTY", "")
    nonwhite_stats = nonwhite_stats.drop(columns = {"STNAME"})

    return income_and_unemployment, nonwhite_stats



# Scrapes data files files from STIP website
# If Full_STIP, the final file, already exists, web scraping will not occur. 
# This is to make the code more efficient.

def stip_assembly():
    STIP_data_numbers = list(range(1,12))
    
    if os.path.exists("Full STIP.xlsx") != True:
        for i in range(0,len(STIP_data_numbers)):
            url = f"https://www.dot.ny.gov/programs/stip/files/R{STIP_data_numbers[i]}.xls"
            STIP_file = requests.get(url)
            STIP_data = STIP_file.content
            with open(f"/Users/rohankremerguha_1/Documents/GitHub/final-project-rskg/r{STIP_data_numbers[i]}.xls", "wb") as output:
                output.write(STIP_data)
    else:
        print("Full STIP found. Web scraping toggled off.")
    
    # System wide project scraping, which is a component of the STIP data file.
    if os.path.exists("SW.xls") != True:
        url = "https://www.dot.ny.gov/programs/stip/files/SW.xls"
        SW_file = requests.get(url)
        SW_data = SW_file.content
        with open("/Users/rohankremerguha_1/Documents/GitHub/final-project-rskg/SW.xls", "wb") as output:
            output.write(SW_data)
    else:
        print("sw.xls found. Web scraping toggled off.")
    
    # Code below is for appending files scraped earlier to make full file for analysis.
    full_stip = []
    
    for i in range(0,len(STIP_data_numbers)):
        data_file = pd.read_excel(f"r{STIP_data_numbers[i]}.xls", sheet_name = 2)
        full_stip.append(data_file)
    
    sw = pd.read_excel("SW.xls", 2)
    full_stip.append(sw)
    
    return pd.concat(full_stip, ignore_index = True)
    


# Code below is for web scraping population density information, which is needed
# for analysis.

def demographics_scrape():
    if os.path.exists("demographics.csv") != True:
        url2 = "https://www.health.ny.gov/statistics/vital_statistics/2020/table02.htm"
        path = "/Users/rohankremerguha_1/Documents/GitHub/final-project-rskg/demographics.csv"
        
        response = requests.get(url2)
        soup = BeautifulSoup(response.text, "lxml")
        
        "New York " in soup.text
        
        table = soup.find("tbody")
        table.find_all("tr")
        
        
        unparsed_rows = []
        for row in table.find_all("tr"):
            row_tags = row.find_all("td")
            unparsed_rows.append([val.text for val in row_tags])
        
        unparsed_rows = (unparsed_rows[2:])
        
        del unparsed_rows[1]
        del unparsed_rows[7]
        
        # Inspired by chatgpt with search query "how to put together scraped data into
        # table Python". 
        
        unparsed_rows = [[item.replace(",", "") for item in row] if isinstance(row, list) else row for row in unparsed_rows]
        
        parsed_rows = [",".join(row) for row in unparsed_rows]
        
        header = "County, 2020 Population Estimate, 2010 Population Estimate, 2020 Land Area Square Miles, 2020 Population Density" 
        
        parsed_rows.insert(0,header)
        
        df = '\n'.join(parsed_rows)
        
        with open(path, "w") as dem:
            dem.write(df)
    
    else:
        print("Demographics.csv exists. Web scraping toggled off.")


income_and_unemployment, nonwhite_stats = prep_downloaded_files()
combined_data = stip_assembly()
demographics_scrape()

# Creates output files, which are needed for text processing and data analysis.
income_and_unemployment.to_csv("data/intermediate/med_household_income.csv", index = False)
nonwhite_stats.to_csv("data/intermediate/nonwhite_share.csv", index = False)
combined_data.to_excel("data/intermediate/Full STIP.xlsx", index = False)