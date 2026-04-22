import streamlit as st # type: ignore


def julias_function_placeholder(crop_name: str, current_season: str, date_num: int) -> dict:
    return {
        "Harvests": -1,
        "Crop Price": 100,
        "Average Batch": 1.5,
        "Total Revenue": 300,
        "Price Per Seed": 25,
        "Grow Time": 10,
        "Harvest Time": 3,
        "Harvest Days": [20, 25],
        "season": "SU",
        "Total Cost": 100,
        "Profit": 200,
        "Sprite Image": "image"
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
                    st.session_state["Price Per Seed"] = julias_function_result["Price Per Seed"]
                    st.session_state["Grow Time"] = julias_function_result["Grow Time"]
                    st.session_state["Harvest Time"] = julias_function_result["Harvest Time"]
                    st.session_state["Harvests"] = julias_function_result["Harvests"]
                    st.session_state["Total Cost"] = julias_function_result["Total Cost"]
                    st.session_state["Profit"] = julias_function_result["Profit"]
                    st.session_state["Sprite Image"] = julias_function_result["Sprite Image"]
                    ## ANY OTHER FIELDS FROM JULIA'S FUNCTION WE NEED TO
                    ## DISPLAY DIRECTLY TO USER ON THE INTERFACE GOES HERE
                    ## Possible Seeds image instead of fully grown crops?
                    st.session_state["AI Result"] = jordans_function_result
                    st.session_state["was_successful"] = True
            except RuntimeError as e:
                st.error(f"API call failed: {e}")
    
    if st.session_state["was_successful"] == True:
        price_per_seed: float = st.session_state["Price Per Seed"]
        grow_time: int        = st.session_state["Grow Time"]
        harvest_time: int     = st.session_state["Harvest Time"]
        harvests: int         = st.session_state["Harvests"]
        total_cost: float     = st.session_state["Total Cost"]
        profit: float         = st.session_state["Profit"]
        ai_result: str        = st.session_state["AI Result"]
        sprite_image: str     = st.session_state["Sprite Image"]

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
        col1, col2 = st.columns([2, 2], border=True)

        with col1:
            st.markdown("#### Grow Time info:")
            st.text("thingy1")
            st.text("thingy2")
            st.text("thingy3")
        with col2:
            st.markdown("#### Price stuff info:")
            st.text("thingy1")
            st.text("thingy2")
            st.text("thingy3")
        
        st.text("here is ai overview: \"ai ai ai ai yap yap yap yap\"")
        st.image("../crop.png", caption=f"Image of fully grown {crop}")
