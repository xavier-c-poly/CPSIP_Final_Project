import requests
import pandas as pd


def downloadPNG(dictionary : dict, file_name : "str"):
    response = requests.get(dictionary["photo"])

    if response.status_code == 200:
        with open(file_name, "wb") as file:
            file.write(response.content)


def pullDataframeRow(name : str, dataframe):
    data_row = dataframe[dataframe["crop_name"] == name]

    if data_row.empty:
        raise ValueError
    else:
        dict = data_row.squeeze().to_dict()
        return dict