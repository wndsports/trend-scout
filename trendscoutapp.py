import streamlit as st
from pytrends.request import TrendReq
import pandas as pd
import time
import random

# --- 1. Page Configuration ---
st.set_page_config(page_title="Pro Market Scout", page_icon="🚀", layout="wide")

# --- 2. Robust Connection Setup (FIXED) ---
def get_pytrends_client():
    """
    Creates a client with built-in retry logic.
    We removed the complex session code that was causing the crash.
    """
    # retries=3: Tries 3 times if Google fails
    # backoff_factor=1: Waits 1s, 2s, 4s between failures
    return TrendReq(hl='en-US', tz=360, timeout=(10, 25), retries=3, backoff_factor=1)

# --- 3. Helper Function: Robust Data Fetching ---
def fetch_trend_data_robust(keywords, geo):
    pytrends = get_pytrends_client()
    combined_data = pd.DataFrame()
    
    # Progress bar to show the user it's working
    progress_text = "Connecting to Google Trends..."
    my_bar = st.progress(0, text=progress_text)
    total = len(keywords)
    
    for i, kw in enumerate(keywords):
        if kw.strip():
            # Update progress
            percentage = int(((i + 1) / total) * 100)
            my_bar.progress(percentage, text=f"Analyzing: {kw}...")
            
            try:
                # Request data
                pytrends.build_payload([kw], cat=0, timeframe='today 5-y', geo=geo)
                df = pytrends.interest_over_time()
                
                if not df.empty:
                    df = df.drop(columns=['isPartial'], errors='ignore')
                    combined_data[kw] = df[kw]
                
                # Sleep is CRITICAL to avoid "429 Too Many Requests"
                # We wait 1-2 seconds between every single keyword
                time.sleep(random.uniform(1.0, 2.0))
                
            except Exception as e:
                # If it fails, we just skip this keyword and keep going
                # (The built-in retry has already tried 3 times by this point)
                pass
            
    my_bar.empty() # Remove progress bar when done
    return combined_data

# --- 4. Database of Niches ---
ALL_GROWTH_ITEMS = [
    # Tech
    "Portable Power Station", "Smart Ring", "Foldable Phone", "VR Headset", "Drone Fishing",
    "GaN Charger", "Mechanical Keyboard", "Smart Bird Feeder", "E-Ink Tablet", "3D Printer Filament",
    "Bone Conduction Headphones", "Smart Notebook", "Portable Monitor", "Cable Organizer",
    # Health
    "Cold Plunge", "Red Light Therapy", "Mushroom Coffee", "Gua Sha", "Mouth Tape", 
    "Massage Gun", "Weighted Blanket", "Blue Light Glasses", "Air Purifier", "Water Flosser",
    "Ice Bath Tub", "Posture Corrector", "Neck Fan", "Sleep Mask", "Vitamin Shower Filter",
    # Home
    "Heat Pump", "Tiny House", "Vertical Farming", "Hydroponic Tower", "Robot Lawn Mower",
    "Epoxy Table", "Modular Sofa", "Air Fryer Liner", "Sunset Lamp", "Silk Pillowcase",
    "Bento Box", "Vegetable Chopper", "Motion Sensor Light", "Handheld Vacuum", "Carpet Cleaner",
    # Outdoor
    "Pickleball", "Paddle Board", "Roof Top Tent", "Trail Camera", "Disc Golf",
    "Electric Bike", "Golf Simulator", "Barefoot Shoes", "Ruck Plate", "Recovery Sandals",
    "Camping Stove", "Tactical Flashlight", "Waterproof Bag", "Hiking Poles", "Hammock Stand",
    # Kids/Pets
    "Montessori Toys", "Busy Board", "Slow Feeder Dog Bowl", "Dog DNA Test", "Baby Monitor",
    "Cat Water Fountain", "Dog Car Seat", "Reusable Water Balloon", "Balance Bike"
]

# --- 5. Session State ---
if 'selected_trends' not in st.session_state:
    st.session_state.selected_trends = []

if 'current_menu_items' not in st.session_state:
    st.session_state.current_menu_items = random.sample(ALL_GROWTH_ITEMS, 10)

# --- 6. Country Database ---
COUNTRY_MAP = {
    "🌍 Global (All World)": "",
    "🇺🇸 United States": "US", "🇬🇧 United Kingdom": "GB", "🇨🇦 Canada": "CA", 
    "🇦🇺 Australia": "AU", "🇩🇪 Germany": "DE", "🇫🇷 France": "FR", 
    "🇨🇳 China": "CN", "🇯🇵 Japan": "JP", "🇮🇳 India": "IN", "🇧🇷 Brazil": "BR",
    "🇲🇽 Mexico": "MX", "🇰🇷 South Korea": "KR", "🇮🇹 Italy": "IT", "🇪🇸 Spain": "ES",
    "🇳🇱 Netherlands": "NL", "🇹🇷 Turkey": "TR", "🇸🇦 Saudi Arabia": "SA",
    "🇮🇩 Indonesia": "ID", "🇻🇳 Vietnam": "VN", "🇷🇺 Russia": "RU", "🇿🇦 South Africa": "ZA",
    "🇦🇪 United Arab Emirates": "AE", "🇦🇷 Argentina": "AR", "🇦🇹 Austria": "AT", 
    "🇧🇪 Belgium": "BE", "🇧🇬 Bulgaria": "BG", "🇧🇭 Bahrain": "BH", "🇧🇩 Bangladesh": "BD",
    "🇨🇭 Switzerland": "CH", "🇨🇱 Chile": "CL", "🇨🇴 Colombia": "CO", "🇨🇿 Czechia": "CZ",
    "🇩🇰 Denmark": "DK", "🇪🇬 Egypt": "EG", "🇫🇮 Finland": "FI", "🇬🇷 Greece": "GR",
    "🇭🇰 Hong Kong": "HK", "🇭🇺 Hungary": "HU", "🇮🇪 Ireland": "IE", "🇮🇱 Israel": "IL",
    "🇰🇼 Kuwait": "KW", "🇲🇾 Malaysia": "MY", "🇳🇬 Nigeria": "NG", "🇳🇴 Norway": "NO",
    "🇳🇿 New Zealand": "NZ", "🇵🇭 Philippines": "PH", "🇵🇰 Pakistan": "PK", "🇵🇱 Poland": "PL",
    "🇵🇹 Portugal": "PT", "🇶🇦 Qatar": "QA", "🇷🇴 Romania": "RO", "🇸🇪 Sweden": "SE",
    "🇸🇬 Singapore": "SG", "🇹🇭 Thailand": "TH", "🇹🇼 Taiwan": "TW", "🇺🇦 Ukraine": "UA"
}

# --- 7. Sidebar Settings ---
st.sidebar.title("⚙️ Market Settings")
selected_country_label = st.sidebar.selectbox("Target Market", list(COUNTRY_MAP.keys()), index=0)
geo_code = COUNTRY_MAP[selected_country_label]

# --- 8. TOP SECTION: Discovery Menu ---
col_title, col_btn = st.columns([6, 1])
with col_title:
    st.title("🚀 Growth Opportunities")
    st.caption(f"Market Analysis: **{selected_country_label}**")
with col_btn:
    st.write("") 
    st.write("") 
    if st.button("🔄 Refresh", type="primary"):
        st.session_state.current_menu_items = random.sample(ALL_GROWTH_ITEMS, 10)

# Fetch data for menu
menu_items = st.session_state.current_menu_items
# Note: This might take 10-15 seconds now because of the pauses
menu_data = fetch_trend_data_robust(menu_items, geo_code)

# --- DISPLAY GRID ---
rows = [st.columns(5), st.columns(5)]
item_idx = 0

for row in rows:
    for col in row:
        if item_idx < len(menu_items):
            item_name = menu_items[item_idx]
            
            with col:
                # Fixed height box
                with st.container(border=True, height=290):
                    st.write(f"**{item_name}**")
                    
                    if item_name in menu_data.columns:
                        st.line_chart(menu_data[item_name], height=80, use_container_width=True)
                    else:
                        st.warning("No Data")
                        st.caption("Try 'Global' or broader market")
                    
                    # Buttons
                    is_selected = item_name in st.session_state.selected_trends
                    if is_selected:
                        if st.button(f"✅ Active", key=f"btn_{item_name}_{item_idx}", use_container_width=True):
                            st.session_state.selected_trends.remove(item_name)
                            st.rerun()
                    else:
                        if st.button(f"Select", key=f"btn_{item_name}_{item_idx}", use_container_width=True):
                            if len(st.session_state.selected_trends) < 6:
                                st.session_state.selected_trends.append(item_name)
                                st.rerun()
                            else:
                                st.toast("Max 6 items allowed!", icon="⚠️")
                    
                    search_url = f"https://www.google.com/search?q={item_name}"
                    st.link_button("🔎 Google Check", search_url, use_container_width=True)

            item_idx += 1

# --- 9. MIDDLE SECTION: Custom Inputs ---
st.divider()
st.subheader("🔍 Add Custom Products")

col1, col2, col3, col4, col5, col6 = st.columns(6)
custom_inputs = []
with col1: custom_inputs.append(st.text_input("Product 1", ""))
with col2: custom_inputs.append(st.text_input("Product 2", ""))
with col3: custom_inputs.append(st.text_input("Product 3", ""))
with col4: custom_inputs.append(st.text_input("Product 4", ""))
with col5: custom_inputs.append(st.text_input("Product 5", ""))
with col6: custom_inputs.append(st.text_input("Product 6", ""))

active_custom = [x for x in custom_inputs if x.strip() != ""]

# --- 10. BOTTOM SECTION: The Master Chart ---
st.divider()
st.subheader("📊 Trend Comparison Chart")

final_list = st.session_state.selected_trends + active_custom

if final_list:
    final_list = list(set(final_list))
    st.markdown(f"Comparing: **{', '.join(final_list)}**")
    
    with st.spinner("Generating comparison chart (this might take a few seconds)..."):
        chart_data = fetch_trend_data_robust(final_list, geo_code)
    
    if not chart_data.empty:
        st.line_chart(chart_data, height=500)
    else:
        st.warning("No data available. Google might be limiting requests temporarily.")
else:
    st.info("👈 Select items or type product names to see the chart.")
