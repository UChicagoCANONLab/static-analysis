# Web scraping tool for static analysis
# Zack Crenshaw
# Adapted from code by Jean Salac
# Modified by Marco Anaya to retrieve name of parent project when
# it was remixed by a Scratch Encore account

# COMMAND LINE: python3 webScrape.py (studio URL) (file path)

import sys
import requests
import scratchAPI as sa
import os
from bs4 import BeautifulSoup
import json


def scrapeStudio(studioURL, mod_dir):

    studioID = studioURL.strip('https://scratch.mit.edu/studios/')

    # Convert studio URL to the one necessary for scraping Scratch usernames and project IDs.
    # Pull projects until page number does not exist

    # Initialize studio URL and requests
    pageNum = 1
    studio_api_url = sa.studio_to_API(studioURL, pageNum)
    r = requests.get(studio_api_url, allow_redirects=True)

    # While the studio API URL exists, pull all the projects
    while (r.status_code == 200):
        studio_html = r.content
        studio_parser = BeautifulSoup(studio_html, "html.parser")

        for project in studio_parser.find_all('li'):
            # Find the span object with owner attribute
            span_string = str(project.find("span", "owner"))

            # Get project ID
            proj_id = project.get('data-id')

            # Pull scratch username
            scratch_username = span_string.split(">")[2]
            scratch_username = scratch_username[0:len(scratch_username) - 3]

            # if the user is an account used by Scratch Encore for data cleaning,
            # find parent account's username
            if "encoresa" in scratch_username.lower():
                # getting the parent project, where we remixed it from
                project_r = requests.get(sa.create_proj_info_URL(proj_id))
                project_json = json.loads(project_r.content)
                parent_id = str(project_json['remix']['parent'])
                # finding the name of the user
                parent_r = requests.get(sa.create_proj_info_URL(parent_id))
                parent_json = json.loads(parent_r.content)
                scratch_username = parent_json['author']['username']

            if scratch_username == "ScratchEncore": #ignore scratch encore projects
                continue

            # Read json file from URL. Convert Scratch URL to Scratch API URL, then read file.
            apiURL = sa.create_API_URL(proj_id)
            json_stream = requests.get(apiURL, allow_redirects=True)

            user_directory = mod_dir + "/json_files_by_studio/" + studioID + "/"
            json_filename = user_directory + scratch_username + ".json"
            try:
                os.makedirs(user_directory)
            except:
                pass
            with open(json_filename, 'wb') as j:
                j.write(json_stream.content)

        pageNum += 1
        studio_api_url = sa.studio_to_API(studioURL, pageNum)
        r = requests.get(studio_api_url, allow_redirects=True)


if __name__ == '__main__':
        scrapeStudio(sys.argv[1], sys.argv[2])
