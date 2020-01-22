"""
Author: LiamOJ
Purpose: To read the robots.txt file of a website. It can also collect sitemap data from sitemap.xml or robots.txt. The reader requires a
requests object and not the content. 
"""

import urllib.robotparser
from urllib.parse import urlsplit, urlunsplit
import requests
import bs4
import datetime
import json
import sys
import os

def wget(url, user_agent):
    """Retrieve a webpage via its url, and return its contents
    Supply user_agent, default timeout is 10 seconds.
    Returns the response. 
    """
    headers = {'User-Agent': user_agent}
    response = requests.get(url, headers = headers, timeout = 10)

    # response.raise_for_status()
    
    # page_contents = response.content

    return response


def get_robots_txt(url):
    """Gets url of robot.txt file from any url
    Returns string
    """

    split_url = urlsplit(url)

    constructed_set = (split_url.scheme, split_url.netloc, "robots.txt", "", "") 

    new_url = urlunsplit(constructed_set)

    return new_url


def get_crawl_delay(robots_url, user_agent):
    """Gets crawl delay from robots.txt, requires correct URL
    and user agent
    Will return integer or None
    """
    
    robot = urllib.robotparser.RobotFileParser()
    robot.set_url(robots_url)
    robot.read()
    
    return robot.crawl_delay(user_agent)


def check_fetch(robots_url, user_agent, fetch_url):
    """Use to check if a specific robot is allowed to fetch an URL
    Will return bool
    """

    robot = urllib.robotparser.RobotFileParser()
    robot.set_url(robots_url)
    robot.read()

    return robot.can_fetch(user_agent, fetch_url)


def file_exists(file_name, folder_name):
    """Use to check if a filename exists already in the named
    sub-directory.
    This will cat on today's date
    Will return bool
    """
    save_directory = os.path.join(os.curdir, folder_name)
    
    file = file_name + " - " + str(datetime.date.today()) + ".json"

    full_path = os.path.join(save_directory, file)
    
    return os.path.isfile(os.path.join(os.curdir, full_path))


def url_name_builder(url, path):
    """Takes in URL and path to construct URL, normally used to
    transform any URL for a site into robots.txt or sitemap.xml
    Returns string. 
    """
    split_url = urlsplit(url)
    temp_tuple = (split_url[0], split_url[1], path, "", "")
    new_url = urlunsplit(temp_tuple)

    return new_url


def get_single_sitemap(orig_url, xml):
    """
    Returns dictionary of nested lists
    """
    
    dict_url = url_name_builder(orig_url, "")
        
    soup = bs4.BeautifulSoup(xml, features="html.parser")
    url_tags = soup.find_all("url")
    xml_list = []
    
    for index, url_tag in enumerate(url_tags):
        try:
            xml_list.append({element.name : element.text for element in url_tag})
        except AttributeError as err:
            temp_dict = {}
            for element in url_tag:
                try:
                    temp_dict[element.name] = element.text
                except Exception:
                    continue
            xml_list.append(temp_dict)

    return xml_list


def get_multi_sitemaps(orig_url, sitemap_tags, user_agent):

    dict_url = url_name_builder(orig_url, "")

    xml_list = []
    
    for sitemap in sitemap_tags:
        url = str(sitemap.findNext("loc").string)
        nested_sitemap = wget(url, user_agent)
        soup = bs4.BeautifulSoup(nested_sitemap.text, features = "html.parser")
        url_tags = soup.find_all("url")
        
        for url_tag in url_tags:
            try:
                xml_list.append({element.name : element.text for element in url_tag})
            except AttributeError as err:
                temp_dict = {}
                for element in url_tag:
                    try:
                        temp_dict[element.name] = element.text
                    except Exception:
                        continue
                        # Alternative at this point is to go through whatever nested tags are here. 
                xml_list.append(temp_dict)

    return xml_list


def robot_sitemap_parse(url):
    """Use this to pull sitemap URLs from robot.txt
    This will return a list
    """
    robot = urllib.robotparser.RobotFileParser()
    robot.set_url(url)
    robot.read()

    return robot.site_maps()


def master_get_sitemap(response, user_agent):
    """Use as a forking point to decide if a single sitemap has
    to be pulled or multiple. This will get the text of the response,
    make soup and generate list of sitemaps if applicable. 
    Will return large list of small lists. 
    """
    print(f"[*] Working on {response.url}")
    # Get sitemap data
    xml = response.text
    soup = bs4.BeautifulSoup(xml, features = "html.parser")
    sitemap_tags = soup.find_all("sitemap")
    
    # Does this if the /sitemap.xml contains more sitemaps
    if sitemap_tags:
        return get_multi_sitemaps(response.url, sitemap_tags, user_agent)
    else:
        return get_single_sitemap(response.url, xml)


def read_sitemap(url, user_agent):
    """Use to retrieve sitemap data from any URL.
    Pass in a URL to the target site and craweler user agent
    The return will be a dict
    Will raise exception if no sitemap is found.
    """

    # Get webpage content
    response = wget(url, user_agent)
    scheme_host_url = url_name_builder(url, "")

    # if /sitemap.xml doesn't exist, check with robotparser via robots.txt for sitemaps
    if response.status_code >= 400:
        robo_url = get_robots_txt(url)
        if robot_sitemap_parse(robo_url) is None: 
            raise FileNotFoundError(f"[!] No detectable site map for {url}")
        else:
            sitemap_dict = {}
            finished_list = []
            for index, site_map in enumerate(robot_sitemap_parse(robo_url)):
                response = wget(site_map, user_agent)
                finished_list.extend(master_get_sitemap(response, user_agent))
            return finished_list
    
    return master_get_sitemap(response, user_agent)
    

def main():
    pass
    

if __name__ == "__main__":
    main()
