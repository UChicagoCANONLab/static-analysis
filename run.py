# Zack Crenshaw
# Code simplified by Marco Anaya, Summer 2019
# A combination of what was batch.py and run.py

# Structure of line of command file: (studio URL/ID),(grading script),(grade level), [--verbose]

import sys
import os
import csv
import click
from subprocess import call
from Naked.toolshed.shell import execute_js

from dataProcessing import aggregate
from plot import plot
from webScrape import scrapeStudio


@click.command()
@click.argument('project', nargs=1)
@click.argument('keyword', nargs=1, default='')
@click.option('--verbose', '-v', is_flag=True, help='Activates verbose mode.')
def main(project, keyword, verbose):
    """Program that analyzes a CANON PROJECT, specifically modules that match an optional KEYWORD
    (i.e. animation-L2, L2, animation). Without the optional argument, all modules in the project will be graded."""
    
    def vprint(s):
        if verbose:
            print(s)
    
    project_path = "./" + project
    file = project_path + "-metadata.csv"
    project_path += "/"
    grades = []

    vprint("Verbose grading active.")

    with open(file, 'r') as f:
        reader = csv.reader(f)
        csv_to_list = list(reader)
        modules = None
        rows_to_analyze = None
        try:
            modules = csv_to_list[0][2:]
        except:
            print("Error: metadata file improperly formatted.")
            return

        rows_to_analyze = {row: module for row, module in enumerate(modules) if keyword in module}
        print("Running analysis for " + ", ".join(rows_to_analyze.values()) + "...")
        
        if not rows_to_analyze:
            print("Error: keyword not found in any module in the metadata file.")
            return

        for module in rows_to_analyze.values():
            csv_path = project_path + module + "/csv/"
            os.makedirs(csv_path, exist_ok=True)
            if os.path.exists(csv_path + module + '-deep-dive.csv'):
                os.remove(csv_path + module + '-deep-dive.csv')

        grades = {module: [] for module in rows_to_analyze.values()}

        for tID, grade, *urls in csv_to_list[1:]:
            print('Grading teacher: ' + tID + ', grade: ' + grade + '.')
            for row, module in rows_to_analyze.items():
                # check if row is empty
                studioURL = urls[row]
                if studioURL.strip() == "":
                    continue
                studioID = studioURL.strip('htps:/cra.mieduo')  # Takes off "https://scratch.mit.edu/studios/"

                # create a folder for the grade if it has not been made yet
                if grade not in grades[module]:
                    grades[module].append(grade)
                    os.makedirs(project_path + module + "/csv/" + grade + "/", exist_ok=True)

                # Get folder for a module
                mod_dir = project_path + module

                studio_path = mod_dir + "/json_files_by_studio/" + studioID + "/"
                
                # Get data from web if not found locally
                if (os.path.isdir(studio_path) is True):
                    vprint("  Studio " + studioID + " found locally.") 
                else:
                    vprint("  Studio " + studioID + " not found locally, scraping data from web...")
                    scrapeStudio(studioURL, mod_dir)
                    vprint("  Scraped.\n")


                # Run grading script on studio
                args = [project, module, tID, grade, studioID, studio_path]
                if verbose:
                    args.append('verbose')
                execute_js('grade.js', " ".join(args))

        # aggregate data and make graphs for each module
        for module in rows_to_analyze.values():

            data = aggregate(project, module)
            os.makedirs(project_path + module + "/graphs/pngs/", exist_ok=True)
            if project == 'encore':
                data_names = ['class_distributions', 'class_performance_per_req']
                kwargs = {name: data[name] for name in data_names}

                plot(project, module, **kwargs)


if __name__ == '__main__':
    main()
