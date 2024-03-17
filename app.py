#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 19 13:28:20 2023

@author: rohanold
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


#Shiny code

income_info_1 = pd.read_excel("data/intermediate/med_household_income.xlsx")
nonwhite_stats_chart_data_final_1 = pd.read_excel("data/intermediate/nonwhite_info.xlsx")
density_grouped_1 = pd.read_excel("data/intermediate/density_info.xlsx")


from shiny import App, render, ui, reactive
#Use row
app_ui = ui.page_fluid(
    ui.row(
        ui.column(4,
            ui.output_image(id = "logo")
            ),
        ui.column(4,
            ui.h2("Homework 4-Shiny Dashboard", style = "color:blue")
            ),
        ui.column(4,
            ui.h5("Name: Rohan Kremer Guha"),
            ui.h5("Data and Programming in Python II"),
            ui.h5("Quarter: Autumn 2023")
            )
        
        ),
    ui.row(
        
        ui.column(2, 
            ui.card(
                #inspired by: https://rstudio.github.io/bslib/reference/card_body.html
                ui.card_header("Please choose parameters", color = "blue"),
                ui.input_select(id = "topic", 
                               label = "Choose a green project type",
                               choices = ["Transit", "Active Transportation"]),
                ui.input_select(id = "demo",
                                label = "Choose a demographic factor",
                                choices = ["Median Household Income", "Nonwhite Population Share", "Population Density"]),
                #inspired by chat gpt
                #Color from: https://htmlcolorcodes.com/
                style="background-color: #e7dbc8",
                )
                ),
        ui.column(10,
            ui.card(
                ui.output_plot("Eco_graph"),
                style = "background-color:#FCF6EF"
                )   
            )
            )
    
        
        )


def server(input, output, session):
    @reactive.Calc
    #Function below filters dataset from line 238 to create an dataset based
    #on inputed parameters
    def get_data():
        selected_demo = input.demo()
        data = []
        if selected_demo == "Median Household Income":
            data = income_info_1
        elif selected_demo == "Nonwhite Population Share":
            data = nonwhite_stats_chart_data_final_1
        elif selected_demo == "Population Density":
            data = density_grouped_1
        return data
    @output
    @render.plot
    def Eco_graph():
        output_data = get_data()
        fig, ax = plt.subplots()
        
        ax = sns.barplot(x = output_data["Chart labels"], y = output_data[f"Per Capita {input.topic()} Funding"], ax = ax, ci = None, palette="muted")
        
        ax.set_xlabel(f"{input.demo()} Quartiles")
        ax.set_ylabel("Per Capita Funding ($/person)")
        ax.set_title(f"{input.topic()} Per Capita Funding by {input.demo()}*")
        
        ax.grid(False)
        return ax
    @output
    @render.image
    def logo():
        ofile = "harris_logo.png"
        return {'src':ofile, 'contentType':'image/png'}

app = App(app_ui, server)