import sys
import os

sys.path.append(os.getcwd())

import streamlit as st
import pandas as pd
from logic.logic import updateCrop
from agent_helper.summarizer import load_model, query_model


def convert_season_to_readable(season_title: str) -> str:
    season_title = season_title.strip().lower()[:2]
    if season_title == "sp":
        return "Spring"
    elif season_title == "su" or season_title == "sm":
        return "Summer"
    elif season_title == "fa":
        return "Fall"
    elif season_title == "wi":
        return "Winter"
    else:
        return "NAS (Not a season)"


# Main Info
st.title("Stardew Valley Crop Analyzer")
st.divider()

crop_list: list = ["Blueberry", "Beet", "Pumpkin", "Melon"]

st.session_state["has_fetched_crop_list"] = False
st.session_state["has_loaded_ai_model"] = False

if not st.session_state["has_fetched_crop_list"]:
    data = pd.read_csv("stardew_data.csv")
    crop_list: list = data.crop_name.to_list()
    st.session_state["has_fetched_crop_list"] = True

# User input sidebar
st.sidebar.title("Crop Info")
crop: str = st.sidebar.selectbox("Add Plant:", crop_list)
season: str = st.sidebar.selectbox("Choose Season:", ["SP", "SM", "FA", "WI"])
date: int = st.sidebar.number_input("Choose Day:", 1, 28)

# Wait for user to press button
if st.sidebar.button("Analyze"):
    st.session_state["was_successful"] = False
    st.session_state["is_correct_season"] = False

    if date < 1 or date > 28:
        st.warning("Please enter a valid date.")
    else:
        with st.spinner("Calulating Crop Data..."):
            try:

                # Pull useful information about the crop and the AI Overview
                crop_info: dict = updateCrop(crop, season, date)

                user_season: str = convert_season_to_readable(season)
                crop_growth_season: str = convert_season_to_readable(crop_info["season"])
                
                if user_season != crop_growth_season:
                    st.error(f"{crop} does not grow in the {user_season}, it only grows in {crop_growth_season}")
                else:
                    st.session_state["is_correct_season"] = True
                
                    # Load the AI model if needed
                    if not st.session_state["has_loaded_ai_model"]:
                        load_model()
                        st.session_state["has_loaded_ai_model"] = True

                if st.session_state["is_correct_season"] == True:
                    # Query the AI model to obtain an AI overview on the crop
                    ai_overview: str = query_model(crop, convert_season_to_readable(season), date)

                    # Assign all fields that will be displayed from the stardew crop data to streamlit session states
                    st.session_state["cost"] = crop_info["cost"]
                    st.session_state["price"] = crop_info["price"]
                    st.session_state["grow_harvest"] = crop_info["grow_harvest"]
                    st.session_state["grow_mature"] = crop_info["grow_mature"]
                    st.session_state["harvests"] = crop_info["harvests"]
                    st.session_state["total_cost"] = crop_info["total_cost"]
                    st.session_state["profit"] = crop_info["profit"]
                    st.session_state["harvest_days"] = crop_info["harvest_days"]
                    st.session_state["ai_result"] = ai_overview                    
                    st.session_state["was_successful"] = True
            except RuntimeError as e:
                st.error(f"API call failed: {e}")
    
    if st.session_state["was_successful"] == True:
        # Unpack streamlit session state variables to actual python variables
        price_per_seed: float    = st.session_state["cost"]
        price_per_harvest: float = st.session_state["price"]
        grow_time: int           = st.session_state["grow_harvest"]
        harvest_time: int        = st.session_state["grow_mature"]
        harvests: int            = st.session_state["harvests"]
        total_cost: float        = st.session_state["total_cost"]
        profit: float            = st.session_state["profit"]
        ai_result: str           = st.session_state["ai_result"]
        harvest_days: str        = st.session_state["harvest_days"]


        # Create a subheader
        st.subheader(crop)
        col1, col2 = st.columns([1, 1], border=True)

        # Create nested columns
        with col1:
            st.write("#### Growth Time")
            col1_1, col1_2 = st.columns([5, 1])

            with col1_1:
                st.write("Harvests Left:")
                if harvest_time != 0:
                    st.write("Days to First Harvest:")
                    st.write("Days Between Harvests:")
                else:
                    st.write("Days to Harvest:")
                    st.write("Single Harvest")
            with col1_2:
                st.write(f"{harvests}")
                if harvest_time != 0:
                    st.write(f"{harvest_time}")
                    st.write(f"{grow_time}")
                else:
                    st.write(f"{grow_time}")
        
        with col2:
            st.write("#### Pricing")
            col2_1, col2_2 = st.columns([5, 1])

            with col2_1:
                st.write("Seed Cost:")
                st.write("Harvest Value:")
                st.write("Total Cost:")
                st.write("Total Profit:")
            with col2_2:
                st.write(f"{price_per_seed:<4} G")
                st.write(f"{price_per_harvest:<4} G")
                st.write(f"{total_cost:<4} G")
                st.write(f"{profit:<4} G")
        
        col3, col4 = st.columns([3, 2])
        with col3:
            st.write(f"#### Projected Harvest Dates:\n", *harvest_days)
            st.write("#### AI Overview:")
            st.write(ai_result)
        with col4:    
            st.image("crop.png", caption=f"Fully Grown {crop}")
