import json
file_path = "files/tasks_data.json"
user_text_path = "files/user_text.txt"
def read_json():
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data
    except:
        data = {}
        return data

def read_user_text():
    try:
        with open(user_text_path, "r", encoding="utf-8") as r:
            return r.read()

    except FileNotFoundError:
        print(f"Помилка: файл '{user_text_path}' не знайдено.")
        return None