import time
import pprint
import os
import json
from flask import Flask, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# --- Flask App 初始化 ---
app = Flask(__name__)

# --- 爬虫核心逻辑 (封装成一个函数) ---
def scrape_xueqiu_posts():
    print("开始执行雪球爬虫任务...")
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('user-agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"')

    service = Service()
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_window_size(1920, 1080)
    URL = "https://xueqiu.com/u/8740756364"
    all_posts = []

    try:
        driver.get(URL)
        time.sleep(3)
        
        # ... (这里省略了滑块验证和滚动的代码，与您之前的版本完全相同) ...
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "timeline__item")))
        print("动态内容已加载...")
        
        for i in range(1): # 为加快API响应，这里只滚动1次，您可以根据需要调整
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            print(f"执行第 {i+1} 次向下滚动...")
            time.sleep(3)

        page_html = driver.page_source
        soup = BeautifulSoup(page_html, 'lxml')
        timeline_items = soup.find_all('article', class_='timeline__item')
        print(f"成功定位到 {len(timeline_items)} 条动态。")

        # ... (这里省略了循环解析每条动态的详细代码，与您之前的版本完全相同) ...
        # 为了演示，我们只提取最新的几条
        for item in timeline_items[:3]: # 只取最新的3条
            content_element = item.select_one('.timeline__item__content .content--description > div')
            content = content_element.get_text(strip=True, separator='\n') if content_element else "N/A"
            time_element = item.find('a', class_='date-and-source')
            timestamp = time_element.get_text(strip=True) if time_element else "N/A"
            link = "https://xueqiu.com" + time_element['href'] if time_element and time_element.has_attr('href') else "N/A"
            
            post_data = {
                'content': content,
                'timestamp': timestamp,
                'link': link,
            }
            all_posts.append(post_data)

    except Exception as e:
        print(f"爬取过程中发生错误: {e}")
        return {"error": str(e)} # 如果出错，返回错误信息
    finally:
        driver.quit()
        print("爬虫任务完成，浏览器已关闭。")
    
    return all_posts


# --- 创建 API Endpoint ---
@app.route('/latest-posts', methods=['GET'])
def get_latest_posts():
    # 每次请求都实时抓取数据
    # 注意：这可能会很慢，更好的做法是后台定时抓取存起来，API只负责读取
    data = scrape_xueqiu_posts()
    if "error" in data:
        return jsonify(data), 500
    return jsonify(data)

# --- 启动 Web 服务 ---
if __name__ == '__main__':
    # Zeabur 会通过 PORT 环境变量告诉我们应该监听哪个端口
    port = int(os.environ.get('PORT', 8080))
    # 监听 0.0.0.0 以允许外部访问
    app.run(host='0.0.0.0', port=port)