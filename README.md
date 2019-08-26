# Static Analysis 

Last Updated (8/26)

This repository must be placed within the "automated-assessments" repository so that the automated graders fetched for analyzing.

Additionally, `python3`, `pip3`, and the supporting modules must be installed. The required modules can be found in `requirements.txt`. All modules in this file can be installed recursively by running `pip3 install -r requirements.txt`. 

If additional modules are required later on, it is recommended to set up a virtual environment, installing `virtualenv`, so that `requirements.txt` can be updated with only modules specific to this project.


run.py: `python3 run.py project-name [optional keyword] [--verbose/-v]`
* Requires a project name, i.e. encore, act-one
* Second optional argument to narrow down to specific modules within a project, i.e. animation-L1. If no argument is given, run.py will run on all modules in a project
* For each row (classroom) in the CSV metadata file, reads the Scratch studio URL for each module which the analysis is being conducted on
* Uses webScrape.py to scrape the studio jsons if they are not already present locally
* Grades each project using grade.js
* Runs dataProcessing.py and plot.py to output csvs and graphs
* Creates any directories required but a file called "metadata.csv" should be made before running


dataProcessing.py (ran by run.py): `python3 dataProcessing.py (module)`
* Manipulates the data outputted by grade.js and outputs aggregated graphs


plot.py (ran by run.py): `python3 plot.py (module)`
* Given the CSVs from dataProcessing.py, creates the following graphs:
  * Per grade:
    * Distribution, classroom completion per requirement, and classroom completion totals
  * Overall:
    * Classroom completion by grade and teacher/classroom
* Graphs are grouped as PDFs in the graphs folder and saved individually as PNGs within graphs/pngs


webScrape.py (helper for run.py):
* Scrapes the web for a scratch project, adding it to the folder json_files_by_studio and within the folder of its corresponding Studio
* Files are named by the Scratch username of the user. If they the project has been remixed by a Scratch Encore account, it uses the username of the project that it was remixed from

grade.js (helper for run.py):
* Grades each json in a Studio directory (within json_files_by_studio)
* Adds results from each project as rows of a CSV
* CSVs, for each classroom (Studio), are placed in folders by their corresponding grade



Only the files mentioned above have been used for static analysis for Scratch Encore during Summer 2019



    

    



    
