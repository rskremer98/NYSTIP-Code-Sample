#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 19 13:28:20 2023

@author: rohanold
"""
# Code inspired by Chatgpt. Used the query "How to run regressions in Python
# with output"

import pandas as pd
import statsmodels.api as sm

#Changing column names to create more concise output file names later
demographics_with_active_multi = pd.read_excel("data/intermediate/Combined_demographics.xlsx")
demographics_with_active_multi = demographics_with_active_multi.rename(columns = {" 2020 Population Density": "pop_density"})
demographics_with_active_multi = demographics_with_active_multi.rename(columns = {"Median Household Income (2021)": "med_household_income"})
demographics_with_active_multi = demographics_with_active_multi.rename(columns = {"Nonwhite Population Share": "nonwhite"})
demographics_with_active_multi = demographics_with_active_multi.rename(columns = {"Per Capita Active Transportation Funding": "active"})
demographics_with_active_multi = demographics_with_active_multi.rename(columns = {"Per Capita Transit Funding": "transit"})
demographics_with_active_multi = demographics_with_active_multi.rename(columns = {"Per Capita Green Funding": "green"})

def single_var_reg_dummy(mode,char,dummy, source_data):
    x = source_data[[char, dummy]]
    x = sm.add_constant(x)
    y = source_data[mode]
    model = sm.OLS(y,x).fit()
    
    summary_file = model.summary().as_text()
    
    file_path = f"data/regressions/{char}_{mode}.txt"
    
    with open(file_path, "w") as file:
        file.write(summary_file)
    
    return file_path

def double_var_reg_dummy(mode, char_1, char_2, dummy, source_data):
    x = source_data[[char_1, char_2, dummy]]
    x = sm.add_constant(x)
    y = source_data[mode]
    model = sm.OLS(y,x).fit()    
    summary_file = model.summary().as_text()
    
    file_path = f"data/regressions/{char_1}_{char_2}_{mode}.txt"
    
    with open(file_path, "w") as file:
        file.write(summary_file)
    
    return file_path

def triple_var_reg_dummy(mode,char_1, char_2, char_3, dummy,source_data):
    x = source_data[[char_1, char_2, char_3, dummy]]
    x = sm.add_constant(x)
    y = source_data[mode]
    model = sm.OLS(y,x).fit()
    summary_file = model.summary().as_text()
    
    file_path = f"data/regressions/{char_1}_{char_2}_{char_3}_{mode}.txt"
    
    with open(file_path, "w") as file:
        file.write(summary_file)
    
    return file_path

# Single variable regressions

def single_var_regs_run(mode, source_data):

    single_var_reg_dummy(mode, "pop_density", "In NYC", source_data)
    single_var_reg_dummy(mode, "nonwhite", "In NYC", source_data)
    single_var_reg_dummy(mode, "med_household_income", "In NYC", source_data)
    
single_var_regs_run("active", demographics_with_active_multi)
single_var_regs_run("transit", demographics_with_active_multi)
single_var_regs_run("green", demographics_with_active_multi)

# Double variable regressions

def double_var_regs_run(mode, char, source_data):
    
    double_var_reg_dummy(mode, "pop_density", char, "In NYC", source_data)

double_var_regs_run("active", "med_household_income", demographics_with_active_multi)
double_var_regs_run("active", "nonwhite", demographics_with_active_multi)
double_var_regs_run("transit", "med_household_income", demographics_with_active_multi)
double_var_regs_run("transit", "nonwhite", demographics_with_active_multi)
double_var_regs_run("green", "med_household_income", demographics_with_active_multi)
double_var_regs_run("green", "nonwhite", demographics_with_active_multi)

# Triple variable regression-only runs once

def triple_var_regs_run(mode, source_data):
    triple_var_reg_dummy(mode, "pop_density", "med_household_income", "nonwhite", "In NYC", source_data)

triple_var_regs_run("active", demographics_with_active_multi)
triple_var_regs_run("transit", demographics_with_active_multi)
triple_var_regs_run("green", demographics_with_active_multi)
