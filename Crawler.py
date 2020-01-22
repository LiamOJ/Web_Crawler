import spinner
import utils

import os
import json
import datetime


def main():

    
    # Setting some variables
    user_agent = "Student Research Assistant (SRA 1.0)" 
    path = os.path.join(os.curdir, "sitemaps")
    parser = 'html.parser'

    list_of_urls = [
        #'https://forums.darklordpotter.net/',
        'https://www.theguardian.com/uk/technology',
        'https://thehackernews.com/',
        'https://www.schneier.com/',
        'https://krebsonsecurity.com/',
        'https://www.theregister.co.uk/',
        'https://www.welivesecurity.com',
        #'https://nakedsecurity.sophos.com', # Too large
        'https://threatpost.com/',
        #'https://www.cyberark.com/blog/', # Robotparser not picking up sitemaps from robots.txt
        'https://www.eff.org/deeplinks',
        'https://www.darkreading.com/Default.asp',
        'http://www.informationweek.com/',
        'http://www.homelandsecuritynewswire.com/topics/cybersecurity',
        'http://www.informationsecuritybuzz.com/', # Times out every time, accessible via browser
        'https://www.linkedin.com/groups/Information-Security-Buzz-5031905?trk=',
        'https://www.infosecurity-magazine.com/',
        'https://insidecybersecurity.com/',
        'http://www.bssi2.com/blog/',
        'https://twitter.com/thehackersnews',
        'http://www.securitycurrent.com/en/news/ac_news',
        #'http://www.securitycurrent.com/en/podcasts/podcasts_index',
        #'https://www.cnet.com/topics/security/', # Too large
        'http://www.veracode.com/blog',
        'http://bhconsulting.ie/securitywatch/',
        'http://www.securityweek.com/',
        'https://staysafeonline.org/',
        'http://www.cerias.purdue.edu/site/blog/',
        'http://www.technewsworld.com/perl/section/cyber-security/',
        'https://threatpost.com/',
        'https://forensicnews.net/',
        ]
        
    search_params = [
        'Excellimore',
        ]

    list_of_urls = [
        'https://www.edinburghnews.scotsman.com',
        ]

    exclusion_list = [
        #enter exclusions here
        ]

    spider_boi = spinner.Spider(user_agent, parser)

    spider_boi.site_list(list_of_urls)

    #spider_boi.list_build_sitemap("sitemaps")

    result = spider_boi.local_search("sitemaps", search_params)

    utils.json_save("_".join(search_params), result, "Results")


if __name__ == "__main__":
    main()

