# Zack Crenshaw
# Code simplified by Marco Anaya, Summer 2019
# A combination of what was batch.py and run.py

# Structure of line of command file: (studio URL/ID),(grading script),(grade level), [--verbose]

import sys
import os
import csv
from subprocess import call
from Naked.toolshed.shell import execute_js


def main():

    arg = sys.argv[1] if len(sys.argv) > 1 else "*"
    verbose = sys.argv[2] if len(sys.argv) > 2 else ""

    if "verbose" in verbose:
        verbose = " --verbose"
        print("Verbose grading active.")

    file = "./metadata.csv"

    print("Start of grading: \n")
    grades = []

    # iterate through folder
    with open(file, 'r') as f:
        reader = csv.reader(f)
        csv_to_list = list(reader)
        modules = rows_to_analyze = None
        try:
            modules = csv_to_list[0][2:]
        except:
            print("Error: metadata.csv improperly formatted")
            return

        if arg == "*":
            rows_to_analyze = {row: module for row, module in enumerate(modules)}
            print("Running analysis for all modules...")
        elif arg in modules:
            rows_to_analyze = {modules.index(arg): arg}
            print("Running analysis for " + arg + "...")
        else:
            print("Error: module name not found in metadata.csv")
            return

        for module in rows_to_analyze.values():
            os.makedirs("./" + module + "/csv/", exist_ok=True)

        grades = {module: [] for module in rows_to_analyze.values()}
        for tID, grade, *urls in csv_to_list[1:]:

            for row, module in rows_to_analyze.items():
                # check if row is empty
                studioURL = urls[row]
                if studioURL.strip() == "":
                    continue
                # create a folder for the grade if it has not been made yet
                if grade not in grades[module]:
                    grades[module].append(grade)
                    os.makedirs("./" + module + "/csv/" + grade + "/", exist_ok=True)

                grade_and_save(studioURL, tID, module, grade, verbose)

        for module in rows_to_analyze.values():
            call(['python3', 'dataProcessing.py', module])
            os.makedirs("./" + module + "/graphs/pngs/", exist_ok=True)
            call(['python3', 'plot.py', module])


def grade_and_save(studioURL, teacherID, module, grade, verbose=""):

    studioID = studioURL.strip('htps:/cra.mieduo')  # Takes off "https://scratch.mit.edu/studios/"

    # Get folder for a module
    mod_dir = "./" + module

    project = mod_dir + "/json_files_by_studio/" + studioID+"/"
    print(project)

    # Get data from web if not found locally
    if (os.path.isdir(project) is True):
        print("Studio " + studioID + " found locally.")
    else:
        print("Studio " + studioID + " not found locally, scraping data from web...")
        call(["python3", "webScrape.py", studioURL, mod_dir])
        print("Scraped.\n")

    # looks for script in higher directory
    script = "../grading-scripts-s3/" + module + ".js"
    folder = mod_dir + "/csv/" + grade + '/'
    results = folder + teacherID + '-' + studioID + ".csv"

    # Run grading script on studio
    print("Running grading script...")
    execute_js('grade.js', script + " " + project + " " + results + verbose)
    print("Finished grading.\n")


if __name__ == '__main__':
    main()
