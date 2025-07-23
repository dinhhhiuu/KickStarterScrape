from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import json
import os

url = "https://www.kickstarter.com/projects/jellyphone/titan-2-the-latest-5g-qwerty-physical-keyboard-smartphone?ref=discovery_category_ending_soon&total_hits=55136&category_id=337"

# Set up Chrome options
options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...")

# Initialization Chrome driver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
driver.set_page_load_timeout(180)

# Open the web page
try:
    driver.get(url)
    time.sleep(5)
    html = driver.page_source
except Exception as e:
    print("Lỗi khi tải trang:", e)
    html = ""
finally:
    driver.quit()

if html:
    soup = BeautifulSoup(html, "html.parser")
    test = soup.find_all('span', class_='soft-black')
    test2 = soup.find_all('div', class_='block type-16 type-28-md bold dark-grey-500')
    test3 = soup.find_all('h1', class_='type-28 type-24-md soft-black mb1 project-name')
    test4 = soup.find_all('p', class_='f5')
    test5 = soup.find_all('span', class_='ml1')
    outer_div = soup.find("div", class_="rte__content ck ck-content")
    test6 = soup.find_all('p', class_='f5')
    test7 = soup.find_all('span', class_='money')
    comments = soup.find_all('span', class_='count')
    update = soup.find_all('span', class_='count')

    # Generate Dict object
    item = {"url": url}
    if test:
        item["value"] = test[0].get_text(strip=True)
    if test2:
        item["Banker"] = test2[0].get_text(strip=True)
    if test3:
        item["Name of project"] = test3[0].get_text(strip=True)
    if test4:
        item["Year"] = test4[0].get_text(strip=True)
    if test5:
        item["Country"] = test5[1].get_text(strip=True)
    if outer_div:
        p_tags = outer_div.find_all("p")
        item["Description"] = p_tags[0].get_text(strip=True)
    if test6:
        item["Duration"] = test6[0].get_text(strip=True)
    if test7:
        item["Price"] = test7[0].get_text(strip=True)
    if comments:
        cc = comments[1].find_all('data')
        if not cc:
            cc = comments[2].find_all('data')
        item["Comments"] = cc[0].get_text(strip=True)
    if update:
        item["Update"] = update[0].get_text(strip=True)

    # Open file JSON
    filename = "data.json"
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    data.append(item)

    # Save JSON
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print("Đã lưu vào file data.json!")
else:
    print("Không lấy được nội dung trang!")