#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 19 13:28:20 2023

@author: rohanold
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

income_info = pd.read_excel("data/intermediate/med_household_income.xlsx")
density_grouped = pd.read_excel("data/intermediate/density_info.xlsx")
nonwhite_stats_chart_data_final = pd.read_excel("data/intermediate/nonwhite_info.xlsx")

def green_plots(category, projects, topic):
    fig, ax = plt.subplots()
    
    ax = sns.barplot(x = category["Chart labels"], y = category[f"Per Capita {projects} Funding"], ax = ax, ci = None, palette="muted")
    
    ax.set_xlabel(f"{topic} Quartiles")
    ax.set_ylabel("Per capita funding ($/person)")
    ax.set_title(f"{projects} Funding by {topic}*")
    
    ax.grid(False)
    
    plt.savefig(f"data/green_{topic}.png")
    plt.show()

# "Green" chosen for static plots as it encompasses both types of Green funding 
# (transit and active transportation)
green_plots(income_info, "Green", "Median Household Income")
green_plots(nonwhite_stats_chart_data_final,"Green", "Nonwhite Population Share")
green_plots(density_grouped, "Green", "Population Density")