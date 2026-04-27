import pandas as pd
import logic.tools as tools
import streamlit as st


def updateCrop(crop : str, season : str, day : int):
    if "crop_dataframe" not in st.session_state:
        st.session_state.crop_dataframe = pd.read_csv("stardew_data.csv")

    crop_info = tools.pullDataframeRow(crop, st.session_state.crop_dataframe)

    tools.downloadPNG(crop_info, "crop.png")
    crop_info = additionalCropData(crop_info, season, day)

    return crop_info


def additionalCropData(crop_info : dict, season : str, day : int):
    if season != crop_info["season"]:
        crop_info["harvests"] = -1
        return crop_info
    
    if crop_info["grow_mature"] == 0:
        crop_info["harvests"] = (28 - day) // crop_info["grow_harvest"]
        crop_info["total_cost"] = crop_info["harvests"] * crop_info["cost"]
        crop_info["harvest_days"] = []
        for i in range(crop_info["harvests"]):
            crop_info["harvest_days"].append(day + (i + 1) * crop_info["grow_harvest"])
    elif crop_info["grow_mature"] > 0:
        if day + crop_info["grow_mature"] <= 28:
            crop_info["harvests"] = 1 + (28 - (day + crop_info["grow_mature"])) // crop_info["grow_harvest"]
        else:
            crop_info["harvests"] = 0
        crop_info["total_cost"] = 0 if crop_info["harvests"] == 0 else crop_info["cost"]
        crop_info["harvest_days"] = []
        for i in range(crop_info["harvests"]):
            crop_info["harvest_days"].append(day + crop_info["grow_mature"] + (i) * crop_info["grow_harvest"])
            
    crop_info["revenue"] = int(crop_info["harvests"] * crop_info["price"] * crop_info["average_batch"])
    crop_info["profit"] = crop_info["revenue"] - crop_info["total_cost"]

    return crop_info
    