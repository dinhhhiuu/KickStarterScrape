from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import os
import re

from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# Set up driver
# def get_driver():
#     options = Options()
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_argument("--headless=new")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")
#     options.add_argument("user-agent=Mozilla/5.0")
#     service = Service(ChromeDriverManager().install())
#     return webdriver.Chrome(service=service, options=options)
def get_driver():
    options = Options()
    options.binary_location = os.getenv("CHROME_BINARY", "/usr/bin/chromium")  # ← phải khớp với Dockerfile
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0")
    
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

# Scrape Kickstarter
def scrape_kickstarter(url):
    # Handle URL
    url2 = url.split("?")[0] + "/creator"
    html, html2 = "", ""

    # Get Info
    driver1 = get_driver()
    driver2 = get_driver()
    try:
        driver1.get(url)
        time.sleep(5)
        html = driver1.page_source
    finally:
        driver1.quit()
    
    try:
        driver2.get(url2)
        time.sleep(5)
        html2 = driver2.page_source
    finally:
        driver2.quit()
    
    if not html or not html2:
        return None
    
    # Parse
    soup = BeautifulSoup(html, "html.parser")
    soup2 = BeautifulSoup(html2, "html.parser")

    # Get Data first page
    name_project = soup.find_all('span', class_='relative')
    year = soup.find_all('p', class_='f5')
    backers_count = soup.find_all('div', class_='mb0')
    country = soup.find_all('a', class_='grey-dark mr3 nowrap type-12')
    description = soup.find_all('span', class_='content edit-profile-blurb js-edit-profile-blurb')
    goal = soup.find_all('div', class_='type-12 medium navy-500')
    pledged = soup.find_all('h3', class_='mb0')
    comments = soup.find_all('a', class_='tabbed-nav__link project-nav__link--comments js-load-project-content js-analytics-section js-load-project-comments type-14 mx3')
    updates = soup.find_all('a', class_='tabbed-nav__link project-nav__link--updates js-load-project-content js-analytics-section js-load-project-updates type-14 mx3')
    videos = soup.find_all('iframe')
    staff_pick = soup.find_all('a', class_='grey-dark mr3 nowrap type-12 flex items-center')

    # Get Data second page
    create_num = soup2.find_all('span', class_='kds-type kds-type-heading-lg')
    back_num = soup2.find_all('span', class_='kds-type kds-type-heading-sm')
    single_person_creator = soup2.find_all('div', 'text-preline do-not-visually-track kds-type kds-type-body-md')

    # Generate Dict object
    item = {}
    if name_project:
        name_project_main = name_project[0].find_all("a", class_='hero__link')
        item["Name of project"] = name_project_main[0].get_text(strip=True) if name_project_main else "N/A"

    if year:
        year_main = year[0].find_all('time', class_='js-adjust-time')
        item["Year"] = year_main[0].get_text(strip=True) if year_main else "N/A"

    if backers_count:
        backers_count_main = backers_count[0].find_all('h3', class_='mb0')
        item["Backers Count"] = backers_count_main[0].get_text(strip=True) if backers_count_main else "N/A"

    item["Category"] = "None"

    if country:
        country_main = country[0]
        country_main_text = [t for t in country_main.contents if isinstance(t, str)]
        clean_country_main_text = ''.join(country_main_text).strip()
        item["Country"] = clean_country_main_text if clean_country_main_text else "N/A"

    if single_person_creator:
        item["single-person creator"] = single_person_creator[0].get_text(strip=True)

    if create_num:
        create_num_text = create_num[0].get_text(strip=True)
        item["Create Num"] = create_num_text.split(" ")[0]

    if back_num:
        back_num_text = back_num[0].get_text(strip=True)
        item["Back Num"] = back_num_text.split(" ")[0]

    if create_num and back_num:
        create_num_text = create_num[0].get_text(strip=True)
        back_num_text = back_num[0].get_text(strip=True)
        create_num_text_split = create_num_text.split(" ")[0]
        back_num_text_split = back_num_text.split(" ")[0]
        item["Projects Created / Funded"] = int(create_num_text_split) + int(back_num_text_split)
    
    item["Gender"] = "None"

    if description:
        description_text = description[0].get_text(strip=True)
        depth_description = description_text.count(" ") + 1
        item["Depth of Project Description (WordsText)"] = str(depth_description) if description else "0"

    if year:
        duration = year[0]
        duration_text = [t for t in duration.contents if isinstance(t, str)]
        clean_duration_text = ''.join(duration_text).strip()
        duration_number = clean_duration_text.split("(")[1].strip(") ").split(" ")[0]
        item["Duration (Days)"] = duration_number if duration_number else "N/A"
        
    if goal:
        goal_main = goal[0].find_all('span', class_='money')
        item["Goal"] = goal_main[0].get_text(strip=True) if goal_main else "N/A" 

    if pledged:
        pledged_main = pledged[0].find_all('span', class_='money')
        item["Pledged"] = pledged_main[0].get_text(strip=True) if pledged_main else "N/A"
    
    if staff_pick:
        staff_pick_main = staff_pick[0]
        staff_pick_main_text = [t for t in staff_pick_main.contents if isinstance(t, str)]
        clean_staff_pick_main_text = ''.join(staff_pick_main_text).strip()
        if str(clean_staff_pick_main_text) == "Project We Love":
            item["Staff Pick"] = "1"
        else:
            item["Staff Pick"] = "0"

    if goal and pledged:
        goal_main = goal[0].find_all('span', class_='money')
        pledged_main = pledged[0].find_all('span', class_='money')
        if goal_main and pledged_main:
            goal_text = goal_main[0].get_text(strip=True)
            pledged_text = pledged_main[0].get_text(strip=True)

            goal_amount = int(''.join(re.findall(r'\d+', goal_text)))
            pledged_amount = int(''.join(re.findall(r'\d+', pledged_text)))

            item["State"] = 1 if pledged_amount > goal_amount else 0
    if videos:
        amount_videos = len(videos)
        item["Videos"] = str(amount_videos) if amount_videos > 0 else "0"

    if comments:
        comments_main = comments[0].find_all('span', class_='count')
        comments_main_2 = comments_main[0].find_all('data')
        item["Comments"] = comments_main_2[0].get_text(strip=True) if comments_main_2 else "N/A"

    if updates:
        updates_main = updates[0].find_all('span', class_='count')
        item["Updates"] = updates_main[0].get_text(strip=True) if updates_main else "N/A" 
    
    item["Rewards"] = "None"
    item["LINK"] = url

    # Save to MongoDB
    mongo_uri = os.getenv("MONGO_URI")
    client = MongoClient(mongo_uri)
    db = client["kickstarter"]
    collection = db["projects"]
    collection.insert_one(item)
    print("✅ Đã lưu vào MongoDB")
