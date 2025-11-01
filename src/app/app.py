import os
import requests
from typing import Optinal, Tuple, List, Dict
from dotenv import load_dotenv
import streamlit as st
from src.api.google_maps import search_nearby_cafes, load_config, geocode_place

load_dotenv()
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

# set streamlit config
st.set_page_config(page_title='☕️ Cafe Finder Bot', layout='centered')

