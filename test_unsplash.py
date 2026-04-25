import streamlit as st
from utils.api_handlers import _build_search_variations, get_unsplash_image
import config

print("Variations for Dubai:", _build_search_variations("Dubai"))
try:
    imgs = get_unsplash_image("Dubai", count=3)
    print("Images:")
    for img in imgs:
        print(img["url"])
except Exception as e:
    print("Error:", e)
