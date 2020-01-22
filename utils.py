"""
Author: LiamOJ
Purpose: To provide utilities for the web crawler. 
"""
import os
import json
from urllib.parse import urlsplit
import datetime

def json_save(file_name, subject_dict, folder_name=None):
    """Saves a dict to json file in specified sub-directory
    Will cat on today's date to filename
    Null return.
    """
    save_directory = os.path.join(os.curdir, folder_name)
    
    file = file_name + " - " + str(datetime.date.today()) + ".json"

    full_path = os.path.join(save_directory, file)
    
    with open(full_path, "w") as json_file:
        json.dump(subject_dict, json_file, indent = 4)


def print_dict_of_lists(subject_sorted_dict):
    """Use to print a dict of lists to stdout
    """
    for subject in subject_sorted_dict:
        print(f"{subject}")
        for item in subject_sorted_dict[subject]:
            print(f"{item}")

def print_dict(dictionary, seperator):
    for key in dictionary.keys():
        print(f"{key} {seperator} {dictionary[key]}")


def remove_dupes(list_with_dupes):
    """Use to remove exact duplicates from a list,
    this will return a list
    """

    return list(dict.fromkeys(list_with_dupes))
            

def wget(url, user_agent):
    """Retrieve a webpage via its url, and return its contents
    Supply user_agent, default timeout is 10 seconds.
    Returns the .content of response. 
    """
    headers = {'User-Agent': user_agent}
    response = requests.get(url, headers = headers, timeout = 10)

    # response.raise_for_status()
    
    # page_contents = response.content

    return response

def p_type(what_is):
    print(type(what_is))
    

def local_search(folder_location, search_list, exclusion_list=None):
    """Use to search locally held sitemaps (or any txt document) for lines
    containing the specified string. The in-built 'in' feature is used as
    default. This will look in the specified directory for the local data.
    The return is a dictionary.
    """
    search_result_dict = {}

    # Converts a search list to dictionary
    if type(search_list) is list:
        search_params = {}
        for element in search_list:
            search_params[element] = []
        

    # Iterates through dir, loads json files into structure and iterares over elements
    # which are currently dicts of lists. It first looks for positive matches, then
    # there are exlusionary terms it will exclude them from return
    if os.path.exists(folder_location):
        for dirpath, dirname, filenames in os.walk(folder_location):
            for filename in filenames: 
                with open(os.path.join(os.curdir, dirpath, filename)) as file:
                    data = file.read()
                    sitemap_list = json.loads(data)
                    for url_dict in sitemap_list:
                        path = urlsplit(url_dict["loc"]).path
                        for string in search_list:
                            if string in path:
                                if exclusion_list:
                                    if not any(exclusion in path for exclusion in exclusion_list):
                                        search_params[string].append(url_dict["loc"])
                                else:
                                    search_params[string].append(url_dict["loc"])

    else:
        raise Exception("There is no valid file path to search.")

    # Put excluded terms in dict
    # Could implement counters to see how much is being excluded, would need to move this
    if exclusion_list:
        search_params['Exclusions'] = exclusion_list
    
    return search_params

def main():
    pass

if __name__ == '__main__':
    main()
"""
                        for string in search_list:
                            if string in urlsplit(url_dict["loc"]).path:
                                if exclusion_list:
                                    exclude = False
                                    for exclusion in exclusion_list:
                                        if exclusion in urlsplit(url_dict["loc"]).path:
                                            exclude = True
                                    if exclude == False:
                                        search_params[string].append(url_dict["loc"])
                                else:
                                    search_params[string].append(url_dict["loc"])

                         for string in search_list:
                            if string in urlsplit(url_dict["loc"]).path:
                                if exclusion_list:
                                    if not any(exclusion in urlsplit(url_dict["loc"]).path for exclusion in exclusion_list):
                                        search_params[string].append(url_dict["loc"])
                                else:
                                    search_params[string].append(url_dict["loc"])

                            result = map(lambda x: x in urlsplit(url_dict["loc"]).path, search_list)
                            
                        if any(string in urlsplit(url_dict["loc"]).path for string in search_list):
                            if exclusion_list:
                                if any(exclusion in urlsplit(url_dict["loc"]).path for exclusion in exclusion_list):
                                    continue
                                else:
                                    search_params[string].append(url_dict["loc"])
                            else:
                                search_params[string].append(url_dict["loc"])
                        else:
                            continue
"""   
