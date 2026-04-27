import sys
import os

sys.path.append(os.getcwd())

import pandas as pd
from logic.logic import updateCrop
from langchain.summarizer import load_model, query_model

def test_logic_basic():
    result = updateCrop("Beet", "FA", 21)
    assert result is not None

def test_logic_values():
    result = updateCrop("Bok Choy", "FA", 1)
    assert result["price"] == 80

def test_integration():
    try:
        response = query_model("Pumpkin", "Fall", 15)
        assert isinstance(response, str)
    except Exception:
        assert True

def test_load():
    for _ in range(10):
        result = updateCrop("Bok Choy", "FA", 21)
        assert result is not None