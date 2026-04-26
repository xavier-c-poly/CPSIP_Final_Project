import pandas as pd

BASE_TEXT = \
"""Crops can only grow in their respective season and will wilt upon being in another.
All seasons are exactly 28 days long.
Currency is measured in G. G is not short for anything and should be written simply as G.
G is an exclusively integer based currency and should never have a decimal
The following are common crops able to be purchased by the user.

"""

CROP_TEXT = \
"""{0} grows from its seeds in {1} days in {2} and {3}. {0} seeds cost {4} G and sells for on average {5} G.
"""

SINGLE_HARVEST_TEXT = "can only be harvested once"
MULTIPLE_HARVEST_TEXT = "can be harvested every {} days"

decompress_date = {"SP": "Spring", "SM": "Summer", "FA": "Fall", "WI": "Winter"}

def generate_stardew_crop_descriptions():
    with open("stardew_crop_descriptions.txt", "w") as file:
        file.write(BASE_TEXT)

        crop_data = pd.read_csv("stardew_data.csv")

        crops = []
        for (crop_name, _description, grow_mature, grow_harvest, _multiple_harvests,
            season, price, cost, average_batch, _photo) in crop_data.itertuples(index=False):
            crops.append((crop_name, grow_mature if grow_mature > 0 else grow_harvest,
                decompress_date[season], grow_harvest if grow_mature > 0 else 0,
                cost, price * average_batch))

        for crop_name, grow_time, season, regrow_rate, seed_price, avg_sell_price in crops:
            file.write(CROP_TEXT.format(crop_name, grow_time, season,
                SINGLE_HARVEST_TEXT if regrow_rate <= 0 else MULTIPLE_HARVEST_TEXT.format(regrow_rate),
                seed_price, avg_sell_price))

if __name__ == "__main__":
    generate_stardew_crop_descriptions()