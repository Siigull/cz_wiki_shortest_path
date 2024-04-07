from bs4 import BeautifulSoup
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

from collections import deque

######## variable init #########
start = "/wiki/Fakulta_informa%C4%8Dn%C3%ADch_technologi%C3%AD_Vysok%C3%A9ho_u%C4%8Den%C3%AD_technick%C3%A9ho_v_Brn%C4%9B"
end = "/wiki/Klinefelter%C5%AFv_syndrom"
map = {}
map[start] = []
q = deque()
vis = set()
################################

def parse_html(link):
    page = requests.get("https://cs.wikipedia.org/" + link)
    data = page.text
    soup = BeautifulSoup(data)

    return soup

def is_article(link):
    if link.startswith("/wiki/Speci") or \
       link.startswith("/wiki/Wikipedie") or \
       link.startswith("/wiki/N%C3%A1pov%C4%9Bda") or \
       link.startswith("/wiki/Hlavn%C3%AD_strana") or \
       link.startswith("/wiki/Soubor") or \
       link.startswith("/wiki/Kategorie"):
        return False
    else:
        return True

######## one depth search from end ########
# have to use selenium because the returned html from links from on wikipedia doesnt work
# even on selenium I had to use view-source:[link] 
referencing_end = set()
end_metadata = {}
vis_end = set()

options = webdriver.ChromeOptions()
options.add_argument("--headless")
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

def get_backwards_reference(search_link):
    driver.get("view-source:https://cs.wikipedia.org/wiki/Speci%C3%A1ln%C3%AD:Co_odkazuje_na?target=" + search_link[6:] + "&limit=5000#bodyContent")

    for link in driver.find_elements(By.TAG_NAME, "a"):
        cur_link = link.get_attribute('href')

        if cur_link != None:
            cur_link = cur_link[24:] ## remove https://cs.wikipedia.org shown because of view-source

            if cur_link.startswith("/wiki/"):
                if cur_link not in vis_end:
                    if is_article(cur_link):
                        vis_end.add(cur_link)

                        referencing_end.add(cur_link)

                        end_metadata[cur_link] = search_link

get_backwards_reference(end)

prev_set = referencing_end.copy()
if len(referencing_end) < 50:
    for i in prev_set:
        get_backwards_reference(i)

driver.quit()

def print_end_reference(link):
    print_arr = []
    print_arr.append(link)

    while end_metadata[link] != end:
        print_arr.append(end_metadata[link])
        link = end_metadata[link]
    
    print(end)
    for i in reversed(print_arr):
        print(i)
#############################################


def get_links(start_link):
    print("currently parsing:" + start_link)

    soup = parse_html(start_link)

    for link in soup.find_all('a'):
        cur_link = link.get('href')

        if cur_link != None:
            if cur_link.startswith("/wiki/"):
                if cur_link not in vis:
                    if is_article(cur_link):
                        vis.add(cur_link)
                        q.append(cur_link)

                        map[start_link].append(cur_link)

                        map[cur_link] = []
                        map[cur_link].append("head" + start_link)

                        if cur_link in referencing_end:
                            print_end_reference(cur_link)

                            return "found"
    return ""


######## start of main ########
cur_link = ""

q.append(start)
vis.add(start)

while True:
    cur_link = q.popleft()

    if cur_link in referencing_end:
        print_end_reference(cur_link)
        cur_link = ""

        break

    if get_links(cur_link) == "found":
        break

if cur_link != "":
    while True:
        print(cur_link)
        
        if(cur_link == start):
            break

        for link in map[cur_link]:
            if link.startswith("head"):
                cur_link = link[4:]