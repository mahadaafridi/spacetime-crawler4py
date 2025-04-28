import re
from urllib.parse import urlparse, urldefrag, urljoin
from bs4 import BeautifulSoup as Bs
from typing import List, Mapping
from collections import defaultdict
import string 

#set of all defragmented urls (for q1)
unique_pages = set()

# word count 
# made into list because lists are mutable
longest_word_count: List[int] = [0]
longest_word_count_url: List[str] = [""]

#all stopwords given to ignore
# can't use previous assignment tokenization because some of these stopwords use certain punctuation
stop_words = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", 
    "are", "aren't", "as", "at", "be", "because", "been", "before", "being", "below", 
    "between", "both", "but", "by", "can't", "cannot", "could", "couldn't", "did", 
    "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during", "each", "few", 
    "for", "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't", 
    "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself", 
    "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", 
    "into", "is", "isn't", "it", "it's", "its", "itself", "let's", "me", "more", "most", 
    "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", 
    "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", 
    "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such", 
    "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", 
    "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've", 
    "this", "those", "through", "to", "too", "under", "until", "up", "very", "was", 
    "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what", 
    "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's", 
    "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd", 
    "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves"
}

word_counter: Mapping[str, int] = defaultdict(int)

subdomain_counter: Mapping[str, int] = defaultdict(int)

def scraper(url, resp):
    links = extract_next_links(url, resp)
    
    # remove fragment and add to unique set
    defragmented_url, _ = urldefrag(resp.url)

    if defragmented_url not in unique_pages:
        unique_pages.add(defragmented_url)
        parsed = urlparse(defragmented_url)

        #make sure its in uci.edu domain
        if parsed.netloc.endswith(".uci.edu"):
            subdomain_counter[parsed.netloc] += 1
    
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

    # count words (for q2)
    text = soup.get_text(separator=" ")
    words = text.split()
    word_count = len(words)

    if word_count > longest_word_count[0]:
        longest_word_count[0] = word_count
        longest_word_count_url[0] = resp.url
    
    #increment the word counter for each word not in stopwords
    for word in words:
        #get rid of the punctioation like periods and commas
        normalized_word = word.lower().strip(string.punctuation)

        #make sure only words are added and not junk
        if normalized_word not in stop_words and word.isalpha():
            word_counter[normalized_word] += 1

        
    links = soup.find_all('a', href=True)

    for tag in links:
        href = tag['href']

        #join urls
        absolute_url = urljoin(resp.url, href)

        #take away fragment
        defragmented_url, _ = urldefrag(absolute_url)

        all_links.append(defragmented_url)

    return all_links

def is_valid(url) -> bool:
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

def write_report():
    top_50_words = sorted(word_counter.items(), key=lambda item: item[1], reverse=True)[:50]

    with open("report.txt", "w") as file:
        file.write(f"Unique pages: {len(unique_pages)}\n")
        file.write(f"Longest word count url: {longest_word_count_url[0]}\n")
        file.write(f"Longest word count: {longest_word_count[0]}\n")
        for word, count in top_50_words:
            file.write(f"{word}: {count}\n")       
        
        file.write(f"Total subdomains: {len(subdomain_counter)}\n")

        for key in sorted(subdomain_counter.keys()):
            file.write(f"{key}: {subdomain_counter[key]}\n")
            
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