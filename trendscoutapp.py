import streamlit as st
from pytrends.request import TrendReq
import pandas as pd
import time

# --- 1. Page Configuration ---
st.set_page_config(page_title="Pro Market Scout", page_icon="🚀", layout="wide")

# --- 2. Session State (Memory) ---
# This remembers which buttons you clicked
if 'selected_trends' not in st.session_state:
    st.session_state.selected_trends = []

# --- 3. Country Database ---
# Mapping full names to Google Trends codes
COUNTRY_MAP = {
    "🌍 Global (All World)": "",
    "🇺🇸 United States": "US",
    "🇨🇳 China": "CN",
    "🇬🇧 United Kingdom": "GB",
    "🇩🇪 Germany": "DE",
    "🇯🇵 Japan": "JP",
    "🇫🇷 France": "FR",
    "🇨🇦 Canada": "CA",
    "🇦🇺 Australia": "AU",
    "🇮🇳 India": "IN",
    "🇧🇷 Brazil": "BR",
    "🇲🇽 Mexico": "MX",
    "🇰🇷 South Korea": "KR",
    "🇮🇹 Italy": "IT",
    "🇪🇸 Spain": "ES",
    "🇳🇱 Netherlands": "NL",
    "🇸🇦 Saudi Arabia": "SA",
    "🇹🇷 Turkey": "TR",
    "🇮🇩 Indonesia": "ID",
    "🇻🇳 Vietnam": "VN"
}

# --- 4. Sidebar Settings ---
st.sidebar.title("⚙️ Market Settings")
selected_country_label = st.sidebar.selectbox("Target Market", list(COUNTRY_MAP.keys()), index=0)
geo_code = COUNTRY_MAP[selected_country_label]

# Initialize Pytrends
try:
    # tz=360 is US CST time zone (standard for global trends)
    pytrends = TrendReq(hl='en-US', tz=360, timeout=(10, 25))
except:
    st.sidebar.error("⚠️ VPN Error: Google connection failed.")

# --- 5. Helper Function: Fetch Data (Cached) ---
@st.cache_data(ttl=24*60*60) # Save data for 24 hours so it's fast
def fetch_trend_data(keywords, geo):
    """Fetches 5-year data for a list of keywords individually to avoid grouping limits."""
    combined_data = pd.DataFrame()
    
    # We fetch one by one to avoid the "5 keyword limit" of Google Trends
    # and to ensure we get data even if one keyword fails.
    for kw in keywords:
        if kw.strip():
            try:
                pytrends.build_payload([kw], cat=0, timeframe='today 5-y', geo=geo)
                df = pytrends.interest_over_time()
                if not df.empty:
                    df = df.drop(columns=['isPartial'], errors='ignore')
                    # Rename the column to the keyword
                    combined_data[kw] = df[kw]
                time.sleep(0.5) # Slight pause to be polite to Google API
            except:
                pass
    return combined_data

# --- 6. TOP SECTION: Curated Growth Opportunities ---
st.title("🚀 Global Growth Opportunities")
st.markdown(f"**Market Analysis:** {selected_country_label}")

# A list of diverse, high-potential industries/products
# You can change these to whatever you want
CURATED_ITEMS = [
    "Portable Power Station", "Cold Plunge", "Pickleball", "Red Light Therapy", 
    "Smart Ring", "Heat Pump", "E-bike", "Matcha", 
    "Tiny House", "Air Purifier"
]

st.subheader("🔥 Top 10 Trending Sectors (Select to Analyze)")
st.caption("Click 'Select' to add these to the main comparison chart below.")

# Fetch data for these 10 items for the sparklines
curated_data = fetch_trend_data(CURATED_ITEMS, geo_code)

# Layout: 2 rows of 5 columns
rows = [st.columns(5), st.columns(5)]
item_idx = 0

for row in rows:
    for col in row:
        if item_idx < len(CURATED_ITEMS):
            item_name = CURATED_ITEMS[item_idx]
            
            with col:
                # Card-like container
                with st.container(border=True):
                    st.write(f"**{item_name}**")
                    
                    # Small Sparkline Chart
                    if item_name in curated_data.columns:
                        st.line_chart(curated_data[item_name], height=80, use_container_width=True)
                    else:
                        st.write("No Data")
                    
                    # Selection Button Logic
                    if item_name in st.session_state.selected_trends:
                        if st.button(f"✅ Selected", key=f"btn_{item_name}", type="primary"):
                            st.session_state.selected_trends.remove(item_name)
                            st.rerun()
                    else:
                        if st.button(f"Select", key=f"btn_{item_name}"):
                            # Limit to 6 selections from this list? (Optional, currently unlimited)
                            if len(st.session_state.selected_trends) < 6:
                                st.session_state.selected_trends.append(item_name)
                                st.rerun()
                            else:
                                st.toast("You can only select 6 items from this list at once!", icon="⚠️")
            item_idx += 1

# --- 7. MIDDLE SECTION: Custom Inputs ---
st.divider()
st.subheader("🔍 Add Your Own Products")
st.markdown("Enter up to 6 specific products to compare against the selected trends.")

col1, col2, col3, col4, col5, col6 = st.columns(6)
custom_inputs = []
with col1: custom_inputs.append(st.text_input("Product 1", ""))
with col2: custom_inputs.append(st.text_input("Product 2", ""))
with col3: custom_inputs.append(st.text_input("Product 3", ""))
with col4: custom_inputs.append(st.text_input("Product 4", ""))
with col5: custom_inputs.append(st.text_input("Product 5", ""))
with col6: custom_inputs.append(st.text_input("Product 6", ""))

# Filter out empty inputs
active_custom_inputs = [x for x in custom_inputs if x.strip() != ""]

# --- 8. BOTTOM SECTION: Main Comparison Chart ---
st.divider()
st.subheader("📊 Combined Trend Analysis")

# Combine Selected Items + Custom Inputs
all_comparison_items = st.session_state.selected_trends + active_custom_inputs

if all_comparison_items:
    st.write(f"Comparing: **{', '.join(all_comparison_items)}**")
    
    with st.spinner("Fetching data for all items..."):
        # We re-fetch specifically for this combined chart to ensure axes are aligned 
        # (Note: Google Trends allows max 5 for strict relative comparison, 
        # but here we overlay individual fetches to allow unlimited items)
        final_data = fetch_trend_data(all_comparison_items, geo_code)
    
    if not final_data.empty:
        st.line_chart(final_data, height=500)
        
        # Simple Data Table
        with st.expander("View Raw Data"):
            st.dataframe(final_data)
    else:
        st.warning("No data found for the selected items.")
else:
    st.info("👈 Select items from the top list or enter product names above to see the chart.")
