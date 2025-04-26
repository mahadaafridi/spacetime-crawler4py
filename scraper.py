import re
from urllib.parse import urlparse, urldefrag, urljoin
from bs4 import BeautifulSoup as Bs
from typing import List
import time

def scraper(url, resp):
    # Time delay is already built in 
    # time.sleep(.5)
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp) -> List[str]:
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content

    if resp.status != 200:
        print(f"error is {resp.error}")
        return []
    
    soup = Bs(resp.raw_response.content, 'html.parser')
    all_links = []

    links = soup.find_all('a', href=True)

    for tag in links:
        href = tag['href']

        #join urls
        absolute_url = urljoin(resp.url, href)

        #take away fragment
        defragmented_url, _ = urldefrag(absolute_url)

        all_links.append(defragmented_url)

    return all_links

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    valid_domains = {
        "ics.uci.edu",
        "cs.uci.edu",
        "informatics.uci.edu",
        "stat.uci.edu",
        #"today.uci.edu/department/information_computer_sciences/"
        #this is an odd case, make sure to implement correctly
        "today.uci.edu"
    }
    
    
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        
        #get domain
        domain = parsed.netloc.lower()

        #initialize to falase
        is_valid_domain = False
        for valid_domain in valid_domains:
            #if the domain is valid
            if domain.endswith(valid_domain):
                
                #special case where the domain and begining of path is diff
                if valid_domain == "today.uci.edu":
                    if not parsed.path.startswith("/department/information_computer_sciences/"):
                        return False
                is_valid_domain = True
                break
        
        if not is_valid_domain:
            return False
        
        #makes sure that it doesn't stay in calendar forever
        #unsure of how to determine if i should stay on a cal or not?
        if re.search(r'/day/\d{4}-\d{2}-\d{2}', parsed.path) or 'ical=' in parsed.query or 'outlook-ical=' in parsed.query:
            return False

        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

        return True
    except TypeError:
        print ("TypeError for ", parsed)
        raise

def test_is_valid():
    url1 = "https://ics.uci.edu/"
    url2 = 'https://ics.uci.edu/research-areas/'
    url3 = "https://today.uci.edu/department/information_computer_sciences/"
    url4  = "https://today.uci.edu/department/nah/fdsadfasfasd"
    
    assert(is_valid(url1) == True)
    assert(is_valid(url2) == True)
    assert(is_valid(url3) == True)
    assert(is_valid(url4) == False)
    
if __name__ == "__main__":
    test_is_valid()