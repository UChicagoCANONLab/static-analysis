# Static Analysis 

Summer 2019 Update/Use (last updated on 7/24):

This repository must be placed within the "automated-assessments" repository so that the automated graders fetched for analyzing

Additionally, `python3`, `pip3`, and the supporting modules must be installed. The required modules can be found in `requirements.txt`. All modules in this file can be installed recursively by running `pip3 install -r requirements.txt`. 

If additional modules are required later on, it is recommended to set up a virtual environment, installing `virtualenv`, so that `requirements.txt` can be updated with only modules specific to this project.


run.py: `python3 run.py [optional module]`
* If no argument is given, runs analysis on all modules
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
_________________________________________________________________________________________
(Legacy)

Created by Zack Crenshaw, in part based on code from Max White and Jean Salac (as marked)

batch.py: python3 batch.py (text file with commands)
    Will run a batch of calls of 'run.py', given a text or CSV file of arguments
    Each line of text file:
    	StudioURL/Studio ID, module folder, grade level, verbose (optional) 

run.py: python3 run.py (studio URL) (module folder) (grade level) [--verbose]
    scrapes the data from the given studio, and grades the projects, organized by grade level. 
    
    Input a valid link to scrape from the web
    Input just the studio ID to only grade existing JSON files
    Optional verbose tag outputs the grades to the console.
    
    Uses webScrape.py to scrape web data
        Uses scratchAPI.py to get the JSON files
    Uses grade.js to grade the scripts
    	Any errors in grading a project will be printed to the console, regardless of the verbose tag.
    
mergeCSVs.py: python3 mergeCSV (folder containing CSVs) (output CSV file)
    Appends data from CSVs into new CSV
    
countCSV.py: python3 countCSV.py (input CSV) [output CSV]
    Counts each field of the input CSV, and saves the count to a single-line output CSV
    If no explicit output, will output to file with same name with "-counted" appended
    Currently designed to aggregate the first field into "grade level"
    Sets second field to the total count
    Subsequent fields are from the original CSV

addLetterHeading.py: python3 addLetterHeading.py (input file) (output file) (column to start lettering at)
	Creates version of a CSV with letters as the first line, starting where indicated
	This is designed to link informative CSVs with the letters on the graphs
	Output file: "self" for the same file, "copy" for a copy with addition to name
	Column is 1-indexed (starts at 1)

groupedBarGraph.py (module)
	Creates a grouped bar graph with the aggregated.csv in a given module

Metadata files in the module folders with data are designed to be run by batch.py
These files thus have the structure: studioURL,module,grade level

NOTE: See toolchain.txt for an example of how to use this toolchain. Below is a description of each step:

NOTE: Metadata and collected data is contained in the Dropbox folder. 

Data collection and processing procedure:

Data for each module is contained in the folder with that module's name.
Json files output by run.py will be organized by studio in "json_files_by_studio"
Text files containing the grades from these json files are in grades.txt, named for the studio ID
CSV files created by run.py will be named STUDIOID.csv (each studio has its own CSV), and placed in the folder with the grade indicated when run.py is called
The csv files in "aggregated" with grade levels (single digit numbers) are all the csv files for a given grade level appended to each other
Each of the CSVs in "counted" is this grade-wide data with some counting of the data, condensed to single line
aggregated.csv (and variants thereof) is all the counted csvs (or some subset) appended together. It is from this csv that the graphs (pdfs in the top level of a module) are based.



    

    



    
