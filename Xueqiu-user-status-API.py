import time
import os
import json
from flask import Flask, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException
from bs4 import BeautifulSoup

app = Flask(__name__)

def scrape_xueqiu_posts():
    print("--- Starting scrape_xueqiu_posts function ---")
    driver = None
    try:
        print("Initializing Chrome options...")
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('user-agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"')

        print("Initializing Chrome Service...")
        service = Service()
        
        print("Attempting to start webdriver.Chrome...")
        driver = webdriver.Chrome(service=service, options=options)
        print("--- Webdriver started successfully! ---")
        
        driver.set_window_size(1920, 1080)
        URL = "https://xueqiu.com/u/8740756364"
        all_posts = []

        print(f"Navigating to URL: {URL}")
        driver.get(URL)
        
        print("Waiting for timeline item to be present...")
        wait = WebDriverWait(driver, 20) # 增加等待时间
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "timeline__item")))
        print("Timeline item found. Waiting a bit more for dynamic content.")
        time.sleep(3) # 等待动态内容加载

        for i in range(1):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            print(f"Executing scroll down #{i+1}...")
            time.sleep(3)

        page_html = driver.page_source
        soup = BeautifulSoup(page_html, 'lxml')
        timeline_items = soup.find_all('article', class_='timeline__item')
        print(f"Successfully located {len(timeline_items)} posts.")

        for item in timeline_items[:3]:
            content_element = item.select_one('.timeline__item__content .content--description > div')
            content = content_element.get_text(strip=True, separator='\n') if content_element else "N/A"
            time_element = item.find('a', class_='date-and-source')
            timestamp = time_element.get_text(strip=True) if time_element else "N/A"
            link = "https://xueqiu.com" + time_element['href'] if time_element and time_element.has_attr('href') else "N/A"
            
            post_data = {'content': content, 'timestamp': timestamp, 'link': link}
            all_posts.append(post_data)

        return all_posts

    # --- 增强版错误捕捉 ---
    except TimeoutException as e:
        error_message = f"TimeoutException: The element was not found in time. Details: {e.msg}"
        print(error_message)
        return {"error": "A TimeoutException occurred", "details": e.msg}
    except WebDriverException as e:
        error_message = f"WebDriverException: An error occurred with the browser or driver. Details: {e.msg}"
        print(error_message)
        return {"error": "A WebDriverException occurred", "details": e.msg}
    except Exception as e:
        error_message = f"An unexpected error occurred: {type(e).__name__} - {str(e)}"
        print(error_message)
        return {"error": "An unexpected error occurred", "details": str(e)}
    # --- 结束 ---
    finally:
        if driver:
            print("Closing webdriver.")
            driver.quit()

@app.route('/latest-posts', methods=['GET'])
def get_latest_posts():
    data = scrape_xueqiu_posts()
    if "error" in data:
        return jsonify(data), 500
    return jsonify(data)

if __name__ == '__main__':
    print("--- Starting Flask Server ---")
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
