import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urlparse
from config import TEXT_FILE_PATH

def extract_text_in_order(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        for element in soup(["script", "style", "nav", "footer", "header", "aside", "time", "figure", "img"]):
            element.decompose()
        all_content = []
        for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p']):
            text = element.get_text().strip()
            if text and len(text) > 15 and not any(word in text.lower() for word in ['share', 'follow', 'photo', 'video', 'поділитися', 'спільнувач']):
                all_content.append(text)
        return all_content
    except requests.RequestException as e:
        print(f"Помилка: {e}")
        return None

def save_to_file(content, url, folder_path):
    try:
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.replace('www.', '').replace('.', '_')
        path = parsed_url.path.strip('/').replace('/', '_') or 'page'
        if len(path) > 30:
            path = path[:30]
        filename = f"{domain}_{path}.txt"
        file_path = os.path.join(folder_path, filename)
        counter = 1
        original_path = file_path

        while os.path.exists(file_path):
            name, ext = os.path.splitext(original_path)
            file_path = f"{name}_{counter}{ext}"
            counter += 1
        with open(file_path, 'w', encoding='utf-8') as f:
            for text in content:
                f.write(text + "\n")
        print(f"✅ Збережено: {file_path}")
        return file_path
    except Exception as e:
        print(f"❌ Помилка при збереженні: {e}")
        return None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(BASE_DIR))
TEXT_DIR = os.path.join(PROJECT_ROOT, TEXT_FILE_PATH)



