import streamlit as st # type: ignore
from tools import download_png


def julias_function_placeholder(crop_name: str, current_season: str, date_num: int) -> dict:
    #download_png(crop_name)
    return {
        "harvests": 7,
        "price": 100,
        "average_batch": 1.5,
        "total_revenue": 300,
        "cost": 25,
        "grow_harvest": 10,
        "grow_mature": 3,
        "harvest_days": [20, 25],
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


# When someone selects a new crop, clear ALL outputs!

# Main Info
st.title("Stardew Crop Analyzer")
st.divider()

# User input sidebar
crop: str = st.sidebar.selectbox("Add Plant:", ["Apple", "Banana", "Beets", "Blueberries"])
season: str = st.sidebar.selectbox("Choose Season:", ["SP", "SU", "FA", "WI"])
date: int = st.sidebar.number_input("Choose Day:", 1, 28)

if st.sidebar.button("Analyze"):
    st.session_state["was_successful"] = False

    if date < 1 or date > 28:
        st.warning("Please enter a valid date.")
    else:
        with st.spinner("Calulating Crop Data..."):
            try:
                julias_function_result: dict = julias_function_placeholder(crop, season, date)
                jordans_function_result: str = jordans_function_placeholder(julias_function_result)

                user_season: str = convert_season_to_readable(season)
                crop_growth_season: str = convert_season_to_readable(julias_function_result["season"])
                
                if user_season != crop_growth_season:
                    st.error(f"{crop} does not grow in the {user_season}, it only grows in {crop_growth_season}")
                else:
                    st.session_state["cost"] = julias_function_result["cost"]
                    st.session_state["grow_harvest"] = julias_function_result["grow_harvest"]
                    st.session_state["grow_mature"] = julias_function_result["grow_mature"]
                    st.session_state["harvests"] = julias_function_result["harvests"]
                    st.session_state["total_cost"] = julias_function_result["total_cost"]
                    st.session_state["profit"] = julias_function_result["profit"]
                    st.session_state["photo"] = julias_function_result["photo"]
                    st.session_state["harvest_days"] = julias_function_result["harvest_days"]
                    ## ANY OTHER FIELDS FROM JULIA'S FUNCTION WE NEED TO
                    ## DISPLAY DIRECTLY TO USER ON THE INTERFACE GOES HERE
                    ## Possible Seeds image instead of fully grown crops?
                    st.session_state["ai_result"] = jordans_function_result
                    st.session_state["was_successful"] = True
            except RuntimeError as e:
                st.error(f"API call failed: {e}")
    
    if st.session_state["was_successful"] == True:
        price_per_seed: float = st.session_state["cost"]
        grow_time: int        = st.session_state["grow_harvest"]
        harvest_time: int     = st.session_state["grow_mature"]
        harvests: int         = st.session_state["harvests"]
        total_cost: float     = st.session_state["total_cost"]
        profit: float         = st.session_state["profit"]
        sprite_image: str     = st.session_state["photo"]
        ai_result: str        = st.session_state["ai_result"]
        harvest_days: str     = st.session_state["harvest_days"]

        # All results from calculations and database searches we will display to user
        ## PLACEHOLDER STUFF
        #"""
        #st.subheader(crop)
        #st.text(f"Grow Time\t\t= {grow_time}")
        #st.text(f"Harvest Time\t= {harvest_time}")
        #if harvests < 1:
        #    st.text(f"Harvests\t\t= You cannot harvest {crop} in the {convert_season_to_readable(season)}.")
        #else:
        #    st.text(f"Harvests\t\t= {harvests}")
        #st.text(f"Price Per Seed\t= {price_per_seed}")
        #st.text(f"Total Cost\t\t= {total_cost}")
        #st.text(f"Profit\t\t\t= {profit}")
        #st.text(f"AI Result\t\t= {ai_result}")
        #st.text(f"Sprite Image: {sprite_image}")
        #st.image("../crop.png", caption=f"Image of fully grown {crop}")
        #"""
        ## PLACEHOLDER STUFF

        st.subheader(crop)
        col1, col2 = st.columns([1, 1], border=True)

        with col1:
            st.markdown("#### Grow Time info")
            col1_1, col1_2 = st.columns([5, 1])

            with col1_1:
                st.text("Harvests:")
                st.text("Days to plant:")
                if harvest_time != 0:
                    st.text("Grow Time (from first planted):")
                    st.text("Harvest Time (after each harvest):")
                else:
                    st.text("Grow Time:")
            with col1_2:
                st.markdown(f"{harvests}")
                st.markdown(*harvest_days)
                if harvest_time != 0:
                    st.markdown(f"{harvest_time}")
                    st.markdown(f"{grow_time}")
                else:
                    st.markdown(f"{grow_time}")
        
        with col2:
            st.markdown("#### Price stuff info")
            col2_1, col2_2 = st.columns([5, 1])

            with col2_1:
                st.text("Price Per Seed:")
                st.text("Total Cost (if you planted on all):")
                st.text("Profit:")
            with col2_2:
                st.markdown(f"{price_per_seed}")
                st.markdown(f"{total_cost}")
                st.markdown(f"{profit}")
        
        
        st.text("here is ai overview: \"ai ai ai ai yap yap yap yap\"")
        st.image("crop.png", caption=f"Image of fully grown {crop}")
