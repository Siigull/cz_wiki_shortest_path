from bs4 import BeautifulSoup
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

from collections import deque

start = "/wiki/Fakulta_informa%C4%8Dn%C3%ADch_technologi%C3%AD_Vysok%C3%A9ho_u%C4%8Den%C3%AD_technick%C3%A9ho_v_Brn%C4%9B"
end = "/wiki/Klinefelter%C5%AFv_syndrom"
map = {}
map[start] = []
q = deque()
vis = set()

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

        if cur_link == None:
            break

        if cur_link in vis_end:
            continue

        vis_end.add(cur_link)

        cur_link = cur_link[24:]
        if cur_link.startswith("/wiki/Speci") or \
        cur_link.startswith("/wiki/Wikipedie") or \
        cur_link.startswith("/wiki/N%C3%A1pov%C4%9Bda") or \
        cur_link.startswith("/wiki/Hlavn%C3%AD_strana") or \
        cur_link.startswith("/wiki/Soubor") or \
        cur_link.startswith("/wiki/Kategorie"):
            continue

        if cur_link.startswith("/wiki/"):
            referencing_end.add(cur_link)

            end_metadata[cur_link] = search_link

get_backwards_reference(end)

prev_set = referencing_end.copy()
if len(referencing_end) < 50:
    for i in prev_set:
        get_backwards_reference(i)

driver.quit()
#############################################

def get_links(start_link):
    print("currently parsing:" + start_link)

    page = requests.get("https://cs.wikipedia.org/" + start_link)
    data = page.text
    soup = BeautifulSoup(data)

    for link in soup.find_all('a'):
        cur_link = link.get('href')

        if cur_link == None:
            break

        if cur_link.startswith("/wiki/"):
            if cur_link in vis:
                continue

            if cur_link.startswith("/wiki/Speci") or \
                cur_link.startswith("/wiki/Wikipedie") or \
                cur_link.startswith("/wiki/N%C3%A1pov%C4%9Bda") or \
                cur_link.startswith("/wiki/Hlavn%C3%AD_strana") or \
                cur_link.startswith("/wiki/Soubor") or \
                cur_link.startswith("/wiki/Kategorie"):
                    continue
            
            vis.add(cur_link)
            q.append(cur_link)

            map[start_link].append(cur_link)

            map[cur_link] = []
            map[cur_link].append("head" + start_link)
            if cur_link in referencing_end:
                print_arr = []
                print_arr.append(cur_link)
                print(end)
                while end_metadata[cur_link] != end:
                    print_arr.append(end_metadata[cur_link])
                    cur_link = end_metadata[cur_link]
                
                for i in reversed(print_arr):
                    print(i)

                return "found"
        
    return ""

######## start of main ########

q.append(start)

cur_link = ""

while True:
    cur_link = q.popleft()

    if get_links(cur_link) == "found":
        break

while True:
    print(cur_link)
    
    if(cur_link == start):
        break

    for link in map[cur_link]:
        if link.startswith("head"):
            cur_link = link[4:]