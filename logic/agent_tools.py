import sys
import os

sys.path.append(os.getcwd())

from langchain.tools import Tool
from logic.logic import updateCrop

def crop_tool_func(crop: str, season: str, day: int):
    return updateCrop(crop, season, day)

crop_tool = Tool(
    name="CropAnalyzer",
    func=crop_tool_func,
    description="Use this to analyze crops. Input format: crop (str), season (str), day (int). (e.g. 'Beet FA 21', SP=Spring, SM or SU =Summer, FA=Fall, WI=Winter)"
)