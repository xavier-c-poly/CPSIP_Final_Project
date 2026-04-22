import streamlit as st # type: ignore
import pandas as pd
from tools import downloadPNG


def julias_function_placeholder(crop_name: str, current_season: str, date_num: int) -> dict:
    downloadPNG(crop_name)
    return {
        "harvests": 7,
        "price": 100,
        "average_batch": 1.5,
        "total_revenue": 300,
        "cost": 25,
        "grow_harvest": 10,
        "grow_mature": 3,
        "harvest_days": [15, 18, 21, 24, 27],
        "season": "SU",
        "total_cost": 100,
        "profit": 200,
        "photo": "image"
    }

def jordans_function_placeholder(crop_info: dict) -> str:
    return "This is a smart LLM response that tells you everything you need to know about the plant, including tips, tricks, and other stuff!"


def convert_season_to_readable(season_title: str) -> str:
    season_title = season_title.strip().lower()[:2]
    if season_title == "sp":
        return "Spring"
    elif season_title == "su":
        return "Summer"
    elif season_title == "fa":
        return "Fall"
    elif season_title == "wi":
        return "Winter"
    else:
        return "NAS (Not a season)"


# Main Info
st.title("Stardew Crop Analyzer")
st.divider()

crop_list: list = ["Blueberry", "Beet", "Pumpkin", "Melon"]

st.session_state["has_fetched_crop_list"] = False
#i_test_delete_when_you_know_it_doesnt_fetch_crop_list_every_millisecond: int = 0  # DEBUGGING
if not st.session_state["has_fetched_crop_list"]:
    data = pd.read_csv("stardew_data.csv")
    crop_list: list = data.crop_name.to_list()
    #i_test_delete_when_you_know_it_doesnt_fetch_crop_list_every_millisecond += 1  # DEBUGGING
    st.session_state["has_fetched_crop_list"] = True
    #st.write(f"it has read the csv: {i_test_delete_when_you_know_it_doesnt_fetch_crop_list_every_millisecond} times")  # DEBUGGING

# User input sidebar
crop: str = st.sidebar.selectbox("Add Plant:", crop_list)
season: str = st.sidebar.selectbox("Choose Season:", ["SP", "SU", "FA", "WI"])
date: int = st.sidebar.number_input("Choose Day:", 1, 28)

# Wait for user to press button
if st.sidebar.button("Analyze"):
    st.session_state["was_successful"] = False

    if date < 1 or date > 28:
        st.warning("Please enter a valid date.")
    else:
        with st.spinner("Calulating Crop Data..."):
            try:
                # Call julia's dictionary function and jordan's ai function
                julias_function_result: dict = julias_function_placeholder(crop, season, date)
                jordans_function_result: str = jordans_function_placeholder(julias_function_result)

                user_season: str = convert_season_to_readable(season)
                crop_growth_season: str = convert_season_to_readable(julias_function_result["season"])
                
                if user_season != crop_growth_season:
                    st.error(f"{crop} does not grow in the {user_season}, it only grows in {crop_growth_season}")
                else:
                    # Assign all fields that will be displayed from the stardew crop data to streamlit session states
                    st.session_state["cost"] = julias_function_result["cost"]
                    st.session_state["grow_harvest"] = julias_function_result["grow_harvest"]
                    st.session_state["grow_mature"] = julias_function_result["grow_mature"]
                    st.session_state["harvests"] = julias_function_result["harvests"]
                    st.session_state["total_cost"] = julias_function_result["total_cost"]
                    st.session_state["profit"] = julias_function_result["profit"]
                    st.session_state["harvest_days"] = julias_function_result["harvest_days"]
                    st.session_state["ai_result"] = jordans_function_result
                    st.session_state["was_successful"] = True
            except RuntimeError as e:
                st.error(f"API call failed: {e}")
    
    if st.session_state["was_successful"] == True:
        # Unpack streamlit session state variables to actual python variables
        price_per_seed: float = st.session_state["cost"]
        grow_time: int        = st.session_state["grow_harvest"]
        harvest_time: int     = st.session_state["grow_mature"]
        harvests: int         = st.session_state["harvests"]
        total_cost: float     = st.session_state["total_cost"]
        profit: float         = st.session_state["profit"]
        ai_result: str        = st.session_state["ai_result"]
        harvest_days: str     = st.session_state["harvest_days"]


        # Create a subheader
        st.subheader(crop)
        col1, col2 = st.columns([1, 1], border=True)

        # Create nested columns
        with col1:
            st.write("#### Grow Time info")
            col1_1, col1_2 = st.columns([5, 1])

            with col1_1:
                st.write("Harvests:")
                if harvest_time != 0:
                    st.write("Grow Time (from first planted):")
                    st.write("Harvest Time (after each harvest):")
                else:
                    st.write("Grow Time:")
            with col1_2:
                st.write(f"{harvests}")
                if harvest_time != 0:
                    st.write(f"{harvest_time}")
                    st.write(f"{grow_time}")
                else:
                    st.write(f"{grow_time}")
        
        with col2:
            st.write("#### Price stuff info")
            col2_1, col2_2 = st.columns([5, 1])

            with col2_1:
                st.write("Price Per Seed:")
                st.write("Total Cost (if you planted on all):")
                st.write("Profit:")
            with col2_2:
                st.write(f"{price_per_seed}")
                st.write(f"{total_cost}")
                st.write(f"{profit}")
        
        col3, col4 = st.columns([3, 2])
        with col3:
            st.write(f"#### Days To Harvest:", *harvest_days)
            st.write("#### AI Overview:")
            st.write(ai_result)
        with col4:    
            st.image("crop.png", caption=f"Fully Grown {crop}")
