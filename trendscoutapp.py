import streamlit as st
from pytrends.request import TrendReq
import pandas as pd
import time
import random

# --- 1. Page Configuration ---
st.set_page_config(page_title="Pro Market Scout", page_icon="🚀", layout="wide")

# --- 2. Huge Database of Niches (Hidden Pool) ---
ALL_GROWTH_ITEMS = [
    # Tech & Gadgets
    "Portable Power Station", "Smart Ring", "Foldable Phone", "VR Headset", "Drone Fishing",
    "GaN Charger", "Mechanical Keyboard", "Smart Bird Feeder", "E-Ink Tablet", "3D Printer Filament",
    "Bone Conduction Headphones", "Smart Notebook", "Portable Monitor", "Cable Organizer",
    # Health & Wellness
    "Cold Plunge", "Red Light Therapy", "Mushroom Coffee", "Gua Sha", "Mouth Tape", 
    "Massage Gun", "Weighted Blanket", "Blue Light Glasses", "Air Purifier", "Water Flosser",
    "Ice Bath Tub", "Posture Corrector", "Neck Fan", "Sleep Mask", "Vitamin Shower Filter",
    # Home & Garden
    "Heat Pump", "Tiny House", "Vertical Farming", "Hydroponic Tower", "Robot Lawn Mower",
    "Epoxy Table", "Modular Sofa", "Air Fryer Liner", "Sunset Lamp", "Silk Pillowcase",
    "Bento Box", "Vegetable Chopper", "Motion Sensor Light", "Handheld Vacuum", "Carpet Cleaner",
    # Outdoor & Sports
    "Pickleball", "Paddle Board", "Roof Top Tent", "Trail Camera", "Disc Golf",
    "Electric Bike", "Golf Simulator", "Barefoot Shoes", "Ruck Plate", "Recovery Sandals",
    "Camping Stove", "Tactical Flashlight", "Waterproof Bag", "Hiking Poles", "Hammock Stand",
    # Kids & Pets
    "Montessori Toys", "Busy Board", "Slow Feeder Dog Bowl", "Dog DNA Test", "Baby Monitor",
    "Cat Water Fountain", "Dog Car Seat", "Reusable Water Balloon", "Balance Bike"
]

# --- 3. Session State (Memory) ---
if 'selected_trends' not in st.session_state:
    st.session_state.selected_trends = []

if 'current_menu_items' not in st.session_state:
    st.session_state.current_menu_items = random.sample(ALL_GROWTH_ITEMS, 10)

# --- 4. Massive Country Database (ISO-3166 Alpha-2) ---
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
    # (List shortened slightly for brevity, but covers top 95% of global GDP)
}

# --- 5. Sidebar Settings ---
st.sidebar.title("⚙️ Market Settings")
selected_country_label = st.sidebar.selectbox("Target Market", list(COUNTRY_MAP.keys()), index=0)
geo_code = COUNTRY_MAP[selected_country_label]

# Initialize Pytrends
try:
    pytrends = TrendReq(hl='en-US', tz=360, timeout=(10, 25))
except:
    st.sidebar.error("⚠️ VPN Error: Google connection failed.")

# --- 6. Helper Function: Fetch Data ---
@st.cache_data(ttl=24*60*60)
def fetch_trend_data(keywords, geo):
    combined_data = pd.DataFrame()
    for kw in keywords:
        if kw.strip():
            try:
                # If geo is empty (Global), we pass nothing or ''
                pytrends.build_payload([kw], cat=0, timeframe='today 5-y', geo=geo)
                df = pytrends.interest_over_time()
                if not df.empty:
                    df = df.drop(columns=['isPartial'], errors='ignore')
                    combined_data[kw] = df[kw]
                time.sleep(0.5) 
            except Exception as e:
                # Fail silently for individual keys to keep app running
                pass
    return combined_data

# --- 7. TOP SECTION: Discovery Menu ---
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
with st.spinner("Analyzing market trends..."):
    menu_data = fetch_trend_data(menu_items, geo_code)

# --- DISPLAY GRID (Fixed Height Boxes) ---
# We use st.columns and a fixed-height container
rows = [st.columns(5), st.columns(5)]
item_idx = 0

for row in rows:
    for col in row:
        if item_idx < len(menu_items):
            item_name = menu_items[item_idx]
            
            with col:
                # height=280 fixes the box size so they align perfectly
                with st.container(border=True, height=290):
                    st.write(f"**{item_name}**")
                    
                    # Sparkline
                    if item_name in menu_data.columns:
                        st.line_chart(menu_data[item_name], height=80, use_container_width=True)
                    else:
                        st.warning("No Data")
                        st.caption("Try 'Global' or broader market")
                    
                    # Layout for Buttons (Select | Check)
                    # We use columns inside the card to stack them or put them side-by-side
                    
                    # 1. Select Button
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
                    
                    # 2. Check on Google Button
                    search_url = f"https://www.google.com/search?q={item_name}"
                    st.link_button("🔎 Google Check", search_url, use_container_width=True)

            item_idx += 1

# --- 8. MIDDLE SECTION: Custom Inputs ---
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

# --- 9. BOTTOM SECTION: The Master Chart ---
st.divider()
st.subheader("📊 Trend Comparison Chart")

final_list = st.session_state.selected_trends + active_custom

if final_list:
    final_list = list(set(final_list))
    st.markdown(f"Comparing: **{', '.join(final_list)}**")
    
    with st.spinner("Generating comparison..."):
        chart_data = fetch_trend_data(final_list, geo_code)
    
    if not chart_data.empty:
        st.line_chart(chart_data, height=500)
    else:
        st.warning("No data available for these keywords in this region.")
else:
    st.info("👈 Select items or type product names to see the chart.")
