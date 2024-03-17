# NYSTIP-Code-Sample

This code determines how per capita funding for green (non-auto) transportation projects varies according to nonwhite population share, median household income and population density. The goal of this analysis was to determine whether environmental justice communities, which have low incomes, high nonwhite population shares, and tend to be urban, received their fair share of sustainable transportation funding. 

Together, there are four attached files, that should be run in the following order:

1. "Assembly_and_wrangle.py": This code webscrapes all NY State Transportation Improvement Program (STIP) projects, the nonwhite population share, and the total population of each county in New York State. The data is then cleaned and written into Excel and csv files.

2. "Text_processing_and_data_analysis.py": This code performs the core text and per-capita funding analysis. Using the output data from the previous program, the code classifies projects as "green" or "auto", calculates per-capita funding per county, and sorts counties by nonwhite population share, median household income, and population density. "Green" projects are further broken down into "Active transportation" (pedestrian and cycling projects) and "Transit" projects. The results of this analysis are then written into Excel files.

3. "Static_plots.py": Uses the data from the previous program to generate plots that are not uploaded to a website and not responsive to user inputs.
   
5. "app.py": Uses the data from the program in step 2 to create plots that are responsive to user inputs. These plots are pictured in the writeup attached to the job application.
   
7. "OLS_Regression_analysis.py": Runs regressions of demographic factors against per-capita green, active transportation and transit funding. The results are outputted as pngs. 
