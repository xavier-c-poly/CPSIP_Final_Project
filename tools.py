import requests

def download_png(url : str):
    response = requests.get(url)

    if response.status_code == 200:
        with open("crop.png", "wb") as file:
            file.write(response.content)