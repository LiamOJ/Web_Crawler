# Class: Web crawler
# Desc: The class defining the web crawler

import bs4
import time
from urllib.parse import urlparse, urlsplit, urlunsplit, urljoin
import requests
import traceback
import time

import robo_reader
import utils

import sys
import os
import json
import re

class Spider:

    def __init__(self, user_agent, parser):
        """Creates a spider instance. Requires a user agent
        """
        self.user_agent = user_agent
        self.robot_data = {}
        self.error_log = open("error_log.txt", "a")
        self.parser = parser
        

    def site_list(self, list_of_urls):
        """Pass in a list of URLs to be searched
        """
        self.list_of_urls = list_of_urls
        

    def search_params(self, search_list):
        """Pass in a list of search terms to be looked for.
        This will later use Python's in-built 'in' paramater to do search.
        """
        self.search_params = {}
        
        for element in search_list:
            self.search_params[element] = []
            

    def __get_url(self, url):
        """Retrieve a webpage via its url, and return its contents"""
        self.url = url

        headers = {'User-Agent': self.user_agent}

        response = requests.get(url, headers = headers)
        page_contents = response.content
        
        return page_contents
    

    def __remove_dupes(self, list_with_dupes):
        """Use to remove exact duplicates from a list,
        this will return a list
        """

        return list(dict.fromkeys(list_with_dupes))
    

    def __get_keyword_links(self, article_links):
        """Extract links matching search terms
        Looks in link path for keyword
        Provides full link by making sure scheme is not empty
        """

        # Sort links in list by subject, assign to dict 
        for link in article_links:
            split_link = urlsplit(link)
            for key in self.search_params.keys():
                if key in split_link.path and split_link.scheme != "":
                    temp_tuple = (split_link.scheme, split_link.netloc, split_link.path, '', '') # potentially a bad idea, not accurate
                    url_to_be_added = urlunsplit(temp_tuple) 
                    if not url_to_be_added in self.search_params[key] and self.__validate_url(url_to_be_added): # check
                        self.search_params[key].append(url_to_be_added) 

        return self.search_params #probably doesn't need to be returned


    def __scoop_the_urls(self, url, soup):
        """Pass in a single URL, from which all full URLs will be returned in a list.
        If an incomplete URL (absent scheme and netloc) the passed in URLs values will
        substituted in and added to list. 
        All other URL-like values are stored in discarded_urls
        """

        list_of_urls = []
        self.discarded_urls = []

        for extract in soup.find_all('a', href = True):
            extracted_url = urlsplit(extract['href'])
            if len(extracted_url.path) > 1 and len(extracted_url.netloc) == 0: # assumed incomplete links are native to the page
                temp_tuple = (url.scheme, url.netloc, extracted_url.path, extracted_url[3], extracted_url.query) # not sure this is a good idea yet? Check if valid?
                #list_of_urls.append(urljoin(url, extract['href']))
                list_of_urls.append(urlunsplit(temp_tuple))
            elif len(extracted_url.path) >  1:
                list_of_urls.append(extract['href'])
            else:
                self.discarded_urls.append(extract) # this doesn't go anywhere?

        return list_of_urls

        

    def __make_soup(self, url):
        """Put 'html.parser'"""
        self.url = url

        # get page contents
        page_contents = self.__get_url(url)

        # make soup
        soup = bs4.BeautifulSoup(page_contents, self.parser)

        return soup
    

    def list_build_sitemap(self, sub_directory):
        """This will build a sitemap if one is available.
        It will save this in JSON format in the indicated folder.
        Provide relative or abs path. 
        The JSON will be a dictionary of a list containing dictionaries.
        """
       
        for url in self.list_of_urls:
            try:
                print(f"[*] {url}")

                # Check if file already exists, if so do not proceed
                if robo_reader.file_exists(urlsplit(url).netloc, sub_directory):
                    continue

                # Initial pass - check for /sitemap.xml 
                sitemap_url = robo_reader.url_name_builder(url, "sitemap.xml")

                # Run main sitemap retrieval function
                sitemap_dict = robo_reader.read_sitemap(sitemap_url, self.user_agent)
                
                # if sitemap dict is not empty, save using URL hostname into sitemap folder
                if sitemap_dict:
                    utils.json_save(urlsplit(url).netloc, sitemap_dict, sub_directory)
                else:
                    print("[ERROR] Sitemap empty - please investigate") 
            except Exception as err:
                print(f"[!] Exception({err.__class__.__name__}) at {url}")
                # print(f"[!] Error on line {sys.exc_info()[-1].tb_lineno}")
                # rejected_urls.append(url)
                continue
            

    def local_search(self, folder_location, search_list, exclusion_list=None):
        """Use to search locally held sitemaps (or any txt document) for lines
        containing the specified string. The in-built 'in' feature is used as
        default. This will look in the specified directory for the local data.
        The return is a dictionary.
        """
        result = utils.local_search(folder_location, search_list, exclusion_list)

        return result

    def local_search_regex(self, folder_location, search_list):
        pass
    

    def do_list_search(self):
        self.subject_sorted_dict = {}
        
        for url in self.list_of_urls:

            print(f"[*] Checking URL: {url}")

            try:
                # Split up url for later use
                split_url = urlsplit(url)

                # Make soup
                soup = self.__make_soup(url)

                # Pick URLs from soup and remove duplicates
                unfiltered_url_list = self.__scoop_the_urls(split_url, soup)
                unfiltered_url_list_no_dupes = self.__remove_dupes(unfiltered_url_list)

                # Populate dict
                self.subject_sorted_dict = self.__get_keyword_links(unfiltered_url_list_no_dupes)

            # Broad exception done as this is a long process, error captured in log for analysis
            except Exception as err:
                print(f"Exception({err.__class__.__name__}) : {err}")
                self.error_log.write(f"Exception({err.__class__.__name__}) : {err}\n")
                self.error_log.write(f"Details: \nURL: {url} \n")
                self.error_log.write(traceback.format_exc())
                continue

        return self.subject_sorted_dict

    def __robot_data(self, url):
        """Builds data structure of robot.txt data for each URL
        """

        robo_url = robo_reader.get_robots_txt(url)
        
        if not robo_url in self.robot_data.keys():
            crawl_delay = robo_reader.get_crawl_delay(robo_url, self.user_agent)

            self.robot_data[robo_url] = crawl_delay


    def __validate_url(self, url):

        self.__robot_data(url) # adds crawl delay to dict

        robots_url = robo_reader.get_robots_txt(url)
        
        if self.robot_data[robots_url] is not None:
            print(f"[DELAY]{url}: {self.robot_data[robots_url]}")
            time.sleep(self.robot_data[robots_url])
            
        # Checks if we're allowed to go there, and then if there is an error
        return robo_reader.check_fetch(robots_url, self.user_agent, url) and requests.get(url).status_code < 400 

