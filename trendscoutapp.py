import streamlit as st
from pytrends.request import TrendReq
import pandas as pd
import time
import random
import os

# --- 1. PROXY CONFIGURATION (THE FIX) ---
# ⚠️ REPLACE '10808' WITH YOUR ACTUAL VPN PORT IF DIFFERENT!
# Common ports: 10808 (Clash), 10809 (v2ray), 1080 (Shadowsocks)
VPN_PORT = '10808' 

# Force Python to use the VPN for all traffic
os.environ['http_proxy'] = f'http://127.0.0.1:{VPN_PORT}'
os.environ['https_proxy'] = f'http://127.0.0.1:{VPN_PORT}'

# --- 2. Page Configuration ---
st.set_page_config(page_title="Pro Market Scout", page_icon="🚀", layout="wide")

# --- 3. Robust Connection Setup ---
def get_pytrends_client():
    """
    Creates a client with built-in retry logic.
    """
    # We lowered the timeout slightly to fail faster if the proxy is wrong
    return TrendReq(hl='en-US', tz=360, timeout=(10, 25), retries=2, backoff_factor=1)

# --- 4. Stealth Data Fetching (Grouped) ---
def get_trend_data_grouped(keywords, geo):
    """
    Fetches keywords in groups of 5 to avoid blocking.
    """
    time.sleep(random.uniform(0.5, 1.5))
    
    # Connect (Proxies are now handled automatically by os.environ above)
    pytrends = get_pytrends_client()
    
    combined_data = pd.DataFrame()
    
    # Split keywords into chunks of 5
    batches = [keywords[i:i + 5] for i in range(0, len(keywords), 5)]
    
    for batch in batches:
        try:
            pytrends.build_payload(batch, cat=0, timeframe='today 5-y', geo=geo)
            data = pytrends.interest_over_time()
            
            if not data.empty:
                data = data.drop(columns=['isPartial'], errors='ignore')
                combined_data = pd.concat([combined_data, data], axis=1)
            
            # Wait between batches to be safe
            time.sleep(random.uniform(1.5, 3.0))
            
        except Exception as e:
            pass
            
    return combined_data

# --- 5. Database of Niches ---
ALL_GROWTH_ITEMS = [
    # Tech
    "Portable Power Station", "Smart Ring", "Foldable Phone", "VR Headset", "Drone Fishing",
    "GaN Charger", "Mechanical Keyboard", "Smart Bird Feeder", "E-Ink Tablet", "3D Printer Filament",
    # Health
    "Cold Plunge", "Red Light Therapy", "Mushroom Coffee", "Gua Sha", "Mouth Tape", 
    "Massage Gun", "Weighted Blanket", "Blue Light Glasses", "Air Purifier", "Water Flosser",
    # Home
    "Heat Pump", "Tiny House", "Vertical Farming", "Hydroponic Tower", "Robot Lawn Mower",
    "Epoxy Table", "Modular Sofa", "Air Fryer Liner", "Sunset Lamp", "Silk Pillowcase",
    # Outdoor
    "Pickleball", "Paddle Board", "Roof Top Tent", "Trail Camera", "Disc Golf",
    "Electric Bike", "Golf Simulator", "Barefoot Shoes", "Ruck Plate", "Recovery Sandals"
]

# --- 6. Session State ---
if 'selected_trends' not in st.session_state:
    st.session_state.selected_trends = []

# Start with just 5 items to test connection quickly
if 'current_menu_items' not in st.session_state:
    st.session_state.current_menu_items = random.sample(ALL_GROWTH_ITEMS, 5)

# --- 7. Country Database ---
COUNTRY_MAP = {
    "🌍 Global (All World)": "",
    "🇺🇸 United States": "US", "🇬🇧 United Kingdom": "GB", "🇨🇦 Canada": "CA", 
    "🇦🇺 Australia": "AU", "🇩🇪 Germany": "DE", "🇫🇷 France": "FR", 
    "🇨🇳 China": "CN", "🇯🇵 Japan": "JP", "🇮🇳 India": "IN", "🇧🇷 Brazil": "BR",
    "🇲🇽 Mexico": "MX", "🇰🇷 South Korea": "KR", "🇮🇹 Italy": "IT", "🇪🇸 Spain": "ES",
    "🇳🇱 Netherlands": "NL", "🇹🇷 Turkey": "TR", "🇸🇦 Saudi Arabia": "SA",
    "🇮🇩 Indonesia": "ID", "🇻🇳 Vietnam": "VN"
}

# --- 8. Sidebar ---
st.sidebar.title("⚙️ Market Settings")
selected_country_label = st.sidebar.selectbox("Target Market", list(COUNTRY_MAP.keys()), index=0)
geo_code = COUNTRY_MAP[selected_country_label]

# --- 9. TOP SECTION: Discovery ---
col_title, col_btn = st.columns([6, 1])
with col_title:
    st.title("🚀 Growth Opportunities")
    st.caption(f"Market Analysis: **{selected_country_label}**")
with col_btn:
    st.write("") 
    st.write("") 
    if st.button("🔄 Refresh", type="primary"):
        st.session_state.current_menu_items = random.sample(ALL_GROWTH_ITEMS, 5)

menu_items = st.session_state.current_menu_items

# --- FETCH DATA ---
# This is where the error happened before. Now it uses the VPN.
with st.spinner(f"Connecting to Google via Proxy Port {VPN_PORT}..."):
    menu_data = get_trend_data_grouped(menu_items, geo_code)

# --- DISPLAY GRID ---
cols = st.columns(5)
item_idx = 0

for col in cols:
    if item_idx < len(menu_items):
        item_name = menu_items[item_idx]
        
        with col:
            with st.container(border=True, height=300):
                st.write(f"**{item_name}**")
                
                if item_name in menu_data.columns:
                    st.line_chart(menu_data[item_name], height=80, use_container_width=True)
                else:
                    st.warning("No Data")
                    st.caption("Try 'Global'")
                
                # Buttons
                is_selected = item_name in st.session_state.selected_trends
                if is_selected:
                    if st.button(f"✅ Active", key=f"btn_{item_name}", use_container_width=True):
                        st.session_state.selected_trends.remove(item_name)
                        st.rerun()
                else:
                    if st.button(f"Select", key=f"btn_{item_name}", use_container_width=True):
                        if len(st.session_state.selected_trends) < 6:
                            st.session_state.selected_trends.append(item_name)
                            st.rerun()
                        else:
                            st.toast("Max 6 items!", icon="⚠️")
                
                search_url = f"https://www.google.com/search?q={item_name}"
                st.link_button("🔎 Check Google", search_url, use_container_width=True)

        item_idx += 1

# --- 10. MIDDLE SECTION: Custom Inputs ---
st.divider()
st.subheader("🔍 Add Custom Products")
col1, col2, col3, col4, col5 = st.columns(5)
custom_inputs = []
with col1: custom_inputs.append(st.text_input("Product 1", ""))
with col2: custom_inputs.append(st.text_input("Product 2", ""))
with col3: custom_inputs.append(st.text_input("Product 3", ""))
with col4: custom_inputs.append(st.text_input("Product 4", ""))
with col5: custom_inputs.append(st.text_input("Product 5", ""))

active_custom = [x for x in custom_inputs if x.strip() != ""]

# --- 11. BOTTOM SECTION: Master Chart ---
st.divider()
st.subheader("📊 Comparison")

final_list = st.session_state.selected_trends + active_custom

if final_list:
    final_list = list(set(final_list))
    st.markdown(f"Comparing: **{', '.join(final_list)}**")
    
    with st.spinner("Fetching comparison data..."):
        chart_data = get_trend_data_grouped(final_list, geo_code)
    
    if not chart_data.empty:
        st.line_chart(chart_data, height=500)
    else:
        st.error(f"Connection Failed. Please check if Port {VPN_PORT} is correct in your VPN settings.")
else:
    st.info("Select items to compare.")
