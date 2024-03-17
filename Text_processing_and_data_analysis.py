#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 19 13:28:20 2023

@author: rohanold
"""

import pandas as pd
import re
import copy


# TEXT PROCESSING AND DATA ANALYSIS FILE

demographics = pd.read_csv("demographics.csv")
income_and_unemployment = pd.read_csv("data/intermediate/med_household_income.csv")
nonwhite_stats = pd.read_csv("data/intermediate/nonwhite_share.csv")
combined_data = pd.read_excel("data/intermediate/Full STIP.xlsx")


def text_processing_designate_projects(comb_data):

    comb_data["Total Funding"] = comb_data["FA Cost"]+comb_data["NFA Rollup"]
    
    comb_data = comb_data.dropna(subset = ["Project Description"])
    
    # Regex is long due to numerous contingencies and edge cases
    bike_ped_search_pattern = r"BIKE|CYCLE|BICYCLE|CYCLING|BICYCLING|PEDESTRIAN|ADA|ACCESSIBILITY|ACCESSIBILE|SIDEWALKS?|COMPLETE STREETS|TRAIL|MULTI USE PATH|MULTI-USE PATH"
    
    # Transit pattern was long due to contingencies, and needed to be broken up    
    transit_pattern_Transit = r"\bTRANSIT\b(?!.*(?:\sWAY|\sROAD))"
    transit_pattern_Bus = r"\bBUS\b(?!Y|INESS)|TRAIN"
    transit_pattern_Railroad = r"\bRAILROAD\b(?!.*\b(CROSSINGS?)\b|\bOVERPASS\b)"
    transit_pattern_subway = r"SUBWAY"
    transit_pattern_ferry = r"\bFERRY\b(?! (STREETS?|ROAD|AVENUE|RD|AVE|\bST\b)\b)"
    
    transit_pattern = (
        transit_pattern_Transit + "|" 
        + transit_pattern_Bus + "|" 
        + transit_pattern_Railroad + "|" 
        + transit_pattern_subway + "|" 
        + transit_pattern_ferry
    )
    
    transit_results = [re.search(transit_pattern, index) for index in comb_data["Project Description"]]
    transit_list_of_res = [items.group() if items else "N/A" for items in transit_results]
    transit_output = [0 if items == "N/A" else 1 for items in transit_list_of_res]
    comb_data["Transit projects"] = transit_output
    
    # Transit agencies search pattern. Searches the "Responsible agency" column
    # rather than "project description" column as in the previous Regex's. 
    # Did this as some nuances not caught by transit_pattern
    
    transit_agency = r"TA\b|\bHART\b|LIRR|SUFFOLK CO. TRANSIT|Centro|CENTRO|TCAT"
    comb_data["Resp Agency"] = comb_data["Resp Agency"].astype(str)
    agency_results = [re.search(transit_agency, index) for index in comb_data["Resp Agency"]]
    agency_list_of_res = [items.group() if items else "N/A" for items in agency_results]
    agency_output = [0 if items == "N/A" else 1 for items in agency_list_of_res]
    comb_data["Transit Agency"] = agency_output
        
    ped_results = [re.search(bike_ped_search_pattern, items) for items in comb_data["Project Description"]]
    ped_results_list = [items.group() if items else None for items in ped_results]
    ped_output = [0 if items == None else 1 for items in ped_results_list]
    comb_data["Active Transportation"] = ped_output
    
    # Regex below for general green transportation projects.
    
    green_pattern = r"ELECTRIC VEHICLE CHARGERS|CARBON REDUCTION|NYC CLEAN TRUCKS"
    green_results = [re.search(green_pattern, index) for index in comb_data["Project Description"]]
    green_results_list = [items.group() if items else None for items in green_results]
    green_output = [0 if items == None else 1 for items in green_results_list]
    comb_data["General Green Project"] = green_output
    
    # Function below for whether projects are green or not.
    
    def green_status(row):
        active = row["Active Transportation"]
        transit_1 = row["Transit projects"]
        transit_2 = row["Transit Agency"]
        green_gen = row["General Green Project"]
    
        if active == 1 | transit_1 == 1 | transit_2 == 1| green_gen ==1:
            return 1
        else: 
            return 0
    
    comb_data["Green Status"] = comb_data.apply(green_status, axis = 1)
    
    # Function below is for project type classification
    # Uses multiple criteria due to a few conflicts.
    
    def project_type(row):
        active = row["Active Transportation"]
        transit_1 = row["Transit projects"]
        transit_2 = row["Transit Agency"]
        green_gen = row["General Green Project"]
        
        if transit_1 == 1 | transit_2 == 1:
            return "Transit"
        elif (transit_1 == 1 | transit_2 == 1) and active == 1:
            return "Transit"
        elif active == 1:
            return "Active Transportation"
        elif green_gen == 1:
            return "General Green Project"
        else: 
            return "Auto Project"
        
        # Did not include general green projects in the graphical analysis, and regressions
        # as there are very few of them (6 or so out of 8500 total). 
        # I included them as a category as I felt that there were certain projects, such as electric vehicle charging
        # and general "Carbon reduction" grants that should be categorized for the sake
        # of thoroughness. It would be a huge omission if these projects were not categorized
        # as green. 
    
    comb_data["Project Type"] = comb_data.apply(project_type, axis = 1)

    return comb_data
    

# Code below deals with multi county projects, which require a different scheme
# to allocate money towards counties.
# Limitation: Some MPOs spill into other counties. For example, one county in 
# saratoga, town of Moreau, is in AGFTC. MPOs not always coterminus with counties
# or even states. BMTS for example includes a county in Pennsylvania. 

# Function below is to group counties into MPOs, which are essential for 
# allocating funds from multi-county projects.

def multi_prep(demog):
    demog["County"] = demog["County"].str.strip().str.upper()
    
    def mpo_designation(row):
        county = row["County"]
        
        if county == "NEW YORK" or county == "KINGS" or county == "BRONX" or county == "QUEENS" or county == "RICHMOND":
            return "NYCTCC"
        elif county == "NASSAU" or county == "SUFFOLK":
            return "N/STCC"
        elif county == "WESTCHESTER" or county == "ROCKLAND" or county == "PUTNAM":
            return "MHSTCC"
        elif county == "DUTCHESS":
            return "PDCTC"
        elif county == "ORANGE":
            return "OCTC"
        elif county == "ULSTER":
            return "UCTC"
        elif county == "ALBANY" or county == "RENSSELAER" or county == "SARATOGA" or county == "SCHENECTADY":
            return "CDTC"
        elif county == "WARREN" or county == "WASHINGTON":
            return "AGFTC"
        elif county == "BROOME" or county == "TIOGA":
            return "BMTS"
        elif county == "CHEMUNG":
            return "ECTC"
        elif county == "TOMPKINS":
            return "ITCTC"
        elif county == "HERKIMER" or county == "ONEIDA":
            return "HOCTC"
        elif county == "ONONDAGA" or county == "MADISON" or county == "OSWEGO":
            return "SMTC"
        elif county == "JEFFERSON":
            return "WJCTC"
        elif county == "GENESEE" or county == "LIVINGSTON" or county == "MONROE" or county == "ONTARIO" or county == "ORLEANS" or county == "SENECA" or county == "WAYNE" or county == "WYOMING" or county == "YATES":
            return "GTC"
        elif county == "ERIE" or county == "NIAGARA":
            return "GBNRTC"
        else:
            return "RURAL"
    
    #Change name to MPO
    demog["MPO designation"] = demog.apply(mpo_designation, axis = 1)
    return demog

# Function below allocates funds to counties, using the MPO assignments from 
# the last one.

def county_funds_analysis(demog, comb_data):

    county_funds_df = copy.deepcopy(comb_data)
    #Code below is to correct spelling difference to ensure merge is successful.
    demog["County"][demog["County"]== "ST LAWRENCE"] = "ST. LAWRENCE"
    demog["County"][demog["County"]== "GENESEE"] = "GENESSEE"
    merged_county_funds = demog.merge(county_funds_df, on = "County", how = "left", indicator = True)

    merged_county_funds = merged_county_funds[merged_county_funds['County'] != 'MULTI']
    merged_county_funds = merged_county_funds[merged_county_funds['County'] != 'SYSTEM-WIDE']

    green_funds_all = copy.deepcopy(merged_county_funds)
    dropped_columns = ["Region","MPO designation", "MPO", "PIN", "Air Quality", "Resp Agency", "Project Description", "Short Description", "Phase Type", "FA Fund Type", "Phase Status", "_merge"]
    green_funds_all = green_funds_all.drop(columns = dropped_columns)
    #Groupby is to 
    green_funds_all = green_funds_all.groupby(["County", "Project Type"]).sum().reset_index()
    
    filter_conditions = (green_funds_all['Project Type'] == 'Transit') | (green_funds_all['Project Type'] == 'Active Transportation')

    green_funds_gen = green_funds_all[filter_conditions]
    green_funds_gen = green_funds_gen.drop(columns = "Project Type")
    green_funds_gen = green_funds_gen.groupby("County").sum().reset_index()
    transit_funds = green_funds_all[green_funds_all["Project Type"] == "Transit"]
    active_trans_funds = green_funds_all[green_funds_all["Project Type"] == "Active Transportation"]
    
    green_funds_gen_merge = pd.DataFrame(green_funds_gen[["County","Total Funding"]])
    demog = demog.merge(green_funds_gen_merge, how = "left", on = "County")
    demog = demog.rename(columns = {"Total Funding": "Green Funding"})
    transit_funds_merge = pd.DataFrame(transit_funds[["County","Total Funding"]])
    demog = demog.merge(transit_funds_merge, how = "left", on = "County")
    demog = demog.rename(columns = {"Total Funding": "Transit funding"})
    active_funds_merge = pd.DataFrame(active_trans_funds[["County","Total Funding"]])
    demog = demog.merge(active_funds_merge, how = "left", on = "County")
    demog = demog.rename(columns = {"Total Funding": "Active Transportation funding"})
    
    demog = demog.fillna(0)

    return demog, comb_data

#MULTI COUNTY ANALYSIS-FULL

def multi_county_analysis(demog, comb_data):
    
    multi_county_data = comb_data[comb_data["County"]== "MULTI"]
    multi_county_green_funds = multi_county_data[multi_county_data["Green Status"] == 1]
    dropped_columns = ["Region","County","PIN", "Air Quality", "Resp Agency", "Project Description", "Short Description", "Phase Type", "FA Fund Type", "Phase Status", "Project Type"]
    multi_county_green_funds = multi_county_green_funds.drop(columns = dropped_columns)
    # Groupby is used to determine total funding by MPO
    multi_county_green_funds = multi_county_green_funds.groupby("MPO").sum().reset_index()
    
    
    mpo_counts = copy.deepcopy(demog)
    mpo_counts = mpo_counts.drop(columns = "County")
    
    # Finding number of counties per MPO is essential to allocating funding to each county.
    mpo_counts = mpo_counts.groupby("MPO designation").count().reset_index()
    mpo_counts = mpo_counts.rename(columns = {"Transit funding": "Number of Counties"})
    mpo_counts_merge = pd.DataFrame(mpo_counts[["MPO designation", "Number of Counties"]])
    mpo_counts_merge = mpo_counts_merge.rename(columns = {"MPO designation":"MPO"})
    
    # List of counties per MPO merged into main dataframe to facilitate final 
    # final calculation.
    multi_county_green_merged = mpo_counts_merge.merge(multi_county_green_funds, how = "left", on = "MPO")
    multi_county_green_merged = multi_county_green_merged.dropna()
    
    #Code below is to calculate multi county funding by MPO. 
    multi_county_green_merged["Funding per county"] = multi_county_green_merged["Total Funding"]/multi_county_green_merged["Number of Counties"]   
    multi_county_green_merged_2 = copy.deepcopy(multi_county_green_merged)
    
    # Creates smaller dataframe to merge with main dataframe, which will be 
    # used to calculate total green funds by county.
    multi_county_green_merged_only_mpo_funds = pd.DataFrame(multi_county_green_merged_2[["MPO", "Funding per county"]])
    
    # Code below unifies name to facilitate merge of multi county funding with the
    # main dataframe
    demog = demog.rename(columns = {"MPO designation":"MPO"})
    
    demographics_with_green_multi_funds = demog.merge(multi_county_green_merged_only_mpo_funds, on = "MPO", how = "outer")
    demographics_with_green_multi_funds = demographics_with_green_multi_funds.fillna(0)
    demographics_with_green_multi_funds = demographics_with_green_multi_funds.rename(columns = {"Funding per county": "Multi County green funding per county"})
    
    demographics_with_green_multi_funds["Total Green Funding"] = demographics_with_green_multi_funds["Green Funding"]+demographics_with_green_multi_funds["Multi County green funding per county"]
    
    # Goal of code below is to do the same calculation for green projects in 
    # general to specific green projects. 
    def multi_mode(demog_green_multi, mult_data, mpo_merge, mode):
    
        multi_county_funds = mult_data[mult_data["Project Type"] == f"{mode}"]
        multi_county_funds_refined = pd.DataFrame(multi_county_funds[["MPO", "Total Funding"]])
        multi_county_funds_refined = multi_county_funds_refined.groupby("MPO").sum().reset_index()
        
        
        multi_county_funds_merged = mpo_merge.merge(multi_county_funds_refined, on = "MPO", how = "left")
        multi_county_funds_merged = multi_county_funds_merged.dropna()
        multi_county_funds_merged[f"Multi County {mode} Funding per County"] = multi_county_funds_merged["Total Funding"]/multi_county_funds_merged["Number of Counties"]
        multi_county_funds_final = pd.DataFrame(multi_county_funds_merged[["MPO", f"Multi County {mode} Funding per County"]])
        
        demographics_multi = demog_green_multi.merge(multi_county_funds_final, on = "MPO", how = "outer")
        demographics_multi = demographics_multi.fillna(0)
        demographics_multi[f"Total {mode} Funding"] = demographics_multi[f"Multi County {mode} Funding per County"]+demographics_multi[f"{mode} funding"]
    
        return demographics_multi
    
    demographics_with_transit_multi = multi_mode(demographics_with_green_multi_funds, multi_county_data, mpo_counts_merge, "Transit")
    demographics_with_active_multi = multi_mode(demographics_with_transit_multi, multi_county_data, mpo_counts_merge, "Active Transportation")
    
    # Goal of code below is to correct misspelling of county name.
    demographics_with_active_multi.loc[37, "County"] = "GENESEE"

    return demographics_with_active_multi

# Code below calculates per capita funding, which is essential to regression
# and graphical analysis.

def per_capita_analysis(demographics_active):
    def per_capita_funds(demog_active, mode):
    
        demog_active[f"Per Capita {mode} Funding"] = (demog_active[f"Total {mode} Funding"]*10**6)/demog_active[" 2020 Population Estimate"]
    
        return demog_active
    
    demographics_active = per_capita_funds(demographics_active, "Active Transportation")
    demographics_active = per_capita_funds(demographics_active, "Transit")
    demographics_active = per_capita_funds(demographics_active, "Green")

    return demographics_active



# Function below creates demographic quartiles for regression and graphical
# analysis. 
def prep_for_plots_reg(demographics_active, nw_stats, inc_unemp): 

    nonwhite_stats_grouped = nw_stats.groupby("CTYNAME").sum().reset_index()
    nonwhite_stats_grouped["Nonwhite Population Share"] = nonwhite_stats_grouped["Nonwhite Population"]/nonwhite_stats_grouped["TOT_POP"]
    nonwhite_stats_grouped["Quartiles"] = pd.qcut(nonwhite_stats_grouped["Nonwhite Population Share"], q = 4, labels = False)
    
    # Function to separate out NYC. NYC's nonwhite shares are much higher than
    # other counties, so they deserve their own category.
    
    def nyc_quart(row, county, quartile):
        nw_cty = row[f"{county}"]
        nw_quartiles = row[f"{quartile}"]
        
        if nw_cty in ["NEW YORK","KINGS" ,"QUEENS","BRONX","RICHMOND"]:
            return nw_quartiles+1
        else:
            return nw_quartiles
    
    nonwhite_stats_grouped["Quartiles with NYC"] = nonwhite_stats_grouped.apply(nyc_quart, axis = 1, args = ("CTYNAME", "Quartiles"))
    
    nonwhite_stats_final = pd.DataFrame(nonwhite_stats_grouped[["CTYNAME", "Quartiles with NYC"]])
    nonwhite_stats_final = nonwhite_stats_final.rename(columns = {"CTYNAME": "County"})
    
    nonwhite_stats_chart_data = demographics_active.merge(nonwhite_stats_final, on = "County", how = "left")
    nonwhite_stats_chart_data_final = pd.DataFrame(nonwhite_stats_chart_data[["Quartiles with NYC", "Per Capita Active Transportation Funding", "Per Capita Transit Funding", "Per Capita Green Funding"]])
    nonwhite_stats_chart_data_final = nonwhite_stats_chart_data_final.groupby("Quartiles with NYC").mean().reset_index()
    
    def labels(row):
        quartiles = row["Quartiles with NYC"]
        
        if quartiles == 0:
            return 1
        elif quartiles == 1:
            return 2
        elif quartiles == 2:
            return 3
        elif quartiles == 3:
            return 4
        else:
            return "NYC"
    
    nonwhite_stats_chart_data_final["Chart labels"] = nonwhite_stats_chart_data_final.apply(labels, axis = 1)
    
    nonwhite_stats_chart_data_final_1 = copy.deepcopy(nonwhite_stats_chart_data_final)
    
    # Code below is for density variable quartiles  
    demographics_with_active_multi["Density Quartiles"] = pd.qcut(demographics_with_active_multi[" 2020 Population Density"], q = 4, labels = False)
    
    demographics_with_active_multi["Quartiles with NYC"] = demographics_with_active_multi.apply(nyc_quart, axis = 1, args = ("County", "Density Quartiles"))
    density_grouped = pd.DataFrame(demographics_with_active_multi[["Quartiles with NYC", "Per Capita Active Transportation Funding", "Per Capita Transit Funding", "Per Capita Green Funding"]])
    density_grouped = density_grouped.groupby("Quartiles with NYC").mean().reset_index()
    
    density_grouped["Chart labels"] = density_grouped.apply(labels, axis = 1)

    density_grouped_1 = copy.deepcopy(density_grouped)
    
    # Code below is for Median household income quartiles
    
    income_chart = pd.DataFrame(income_and_unemployment[["County", "Median Household Income (2021)"]])
    demographics_active = demographics_active.merge(income_chart, on = "County", how = "outer")
    demographics_active["Income Quartiles"] = pd.qcut(demographics_active["Median Household Income (2021)"], q = 4, labels= False)
    income_info = pd.DataFrame(demographics_active[["Income Quartiles", "Per Capita Active Transportation Funding", "Per Capita Transit Funding", "Per Capita Green Funding"]])
    
    # Merging nonwhite_stats_grouped with demographics_with_active_multi to 
    # create larger dataframe for regressions 
    nonwhite_stats_grouped_merge = pd.DataFrame(nonwhite_stats_grouped[["CTYNAME", "Nonwhite Population Share"]])
    nonwhite_stats_grouped_merge = nonwhite_stats_grouped_merge.rename(columns = {"CTYNAME": "County"})
     
    demographics_active = demographics_active.merge(nonwhite_stats_grouped_merge, on = "County", how = "outer")
    
    #Creates dummy variable, which is needed for regressions. 
    def in_nyc(row):
        nw_cty = row["County"]
        
        if nw_cty in ["NEW YORK","KINGS" ,"QUEENS","BRONX","RICHMOND"]:
            return 1
        else:
            return 0
    
    demographics_active["In NYC"] = demographics_active.apply(in_nyc, axis = 1)
    
    def labels_2(row):
        quartiles = row["Income Quartiles"]
        
        return quartiles+1
        
    income_info["Chart labels"] = income_info.apply(labels_2, axis = 1)
    income_info = income_info.groupby("Chart labels").mean().reset_index()
    income_info_1 = copy.deepcopy(income_info)

    return demographics_active, income_info_1, density_grouped_1, nonwhite_stats_chart_data_final_1


# TEXT PROCESSING AND DATA ANALYSIS-FUNCTION CALLS

combined_data = text_processing_designate_projects(combined_data)
demographics = multi_prep(demographics)
demographics, combined_data = county_funds_analysis(demographics, combined_data)
demographics_with_active_multi = multi_county_analysis(demographics, combined_data)
demographics_with_active_multi = per_capita_analysis(demographics_with_active_multi)
demographics_with_active_multi, income_info_1, density_grouped_1, nonwhite_stats_chart_data_final_1 = prep_for_plots_reg(demographics_with_active_multi, nonwhite_stats, income_and_unemployment)


# OUTPUT FILES FOR PLOTTING 

income_info_1.to_excel("data/intermediate/med_household_income.xlsx", index = False)
density_grouped_1.to_excel("data/intermediate/density_info.xlsx", index = False)
nonwhite_stats_chart_data_final_1.to_excel("data/intermediate/nonwhite_info.xlsx", index = False)

#OUTPUT FILE FOR REGRESSION ANALYSIS
demographics_with_active_multi.to_excel("data/intermediate/Combined_demographics.xlsx")