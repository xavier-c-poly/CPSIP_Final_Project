import sys
import os

sys.path.append(os.getcwd())

from langchain.tools import tool
from logic.logic import updateCrop

@tool("CropAnalyzer",
    description="Use this to analyze crops. Input format: crop (str), season (str), day (int). (e.g. 'Beet FA 21', SP=Spring, SM or SU =Summer, FA=Fall, WI=Winter)")
def crop_analyzer(crop: str, season: str, day: int):
    return updateCrop(crop, season, day)