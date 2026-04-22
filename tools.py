import requests
import pandas as pd

def downloadPNG(crop : str):
    data = pd.read_csv("stardew_data.csv")
    crop_data = data[data["crop_name"] == crop]
    dict = crop_data.squeeze().to_dict()
    response = requests.get(dict["photo"])

    if response.status_code == 200:
        with open("crop.png", "wb") as file:
            file.write(response.content)


def pullCropData(crop : str):
    data = pd.read_csv("stardew_data.csv")
    crop_data = data[data["crop_name"] == crop]
    dict = crop_data.squeeze().to_dict()

    if crop_data.empty:
        raise ValueError
    else:
        return dict
