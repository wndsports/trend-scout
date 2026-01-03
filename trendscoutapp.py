import streamlit as st
from pytrends.request import TrendReq
import pandas as pd
import wikipedia

# --- Page Config ---
st.set_page_config(page_title="B2B Product Scout", page_icon="🏭", layout="wide")

# --- Initialize Pytrends ---
# Warning: Requires VPN in China
try:
    pytrends = TrendReq(hl='en-US', tz=360, timeout=(10,25))
except:
    st.error("⚠️ Connection Error: Please ensure your VPN is Global Mode.")

# --- SIDEBAR: Quick Select ---
st.sidebar.title("🚀 Quick Niches")
niche = st.sidebar.radio("Select Industry:", ["Custom", "Outdoor Gear", "Industrial Machinery", "Sports Equipment"])

if niche == "Outdoor Gear":
    default_term = "Roof Top Tent"
elif niche == "Industrial Machinery":
    default_term = "Laser Cutting Machine"
elif niche == "Sports Equipment":
    default_term = "Pickleball Paddle"
else:
    default_term = ""

# --- MAIN PAGE ---
st.title("🏭 B2B Opportunity Scout")
st.markdown("Analyze global demand to find your next export opportunity.")

# 1. Search Field
col1, col2 = st.columns([3, 1])
with col1:
    product_kw = st.text_input("Enter Product Name (English):", value=default_term)
with col2:
    target_country = st.selectbox("Target Market", ["US", "GB", "DE", "AU", "CA"])

if product_kw:
    st.divider()
    
    # --- SECTION A: The 5-Year Trend ---
    st.subheader(f"1. Market Trend (5 Years) - {target_country}")
    
    try:
        pytrends.build_payload([product_kw], cat=0, timeframe='today 5-y', geo=target_country)
        data = pytrends.interest_over_time()
        
        if not data.empty:
            # Cleanup
            if 'isPartial' in data.columns: data = data.drop(columns=['isPartial'])
            
            # Draw Chart
            st.line_chart(data)
            
            # Metric: Growth Calculation
            start_vol = data[product_kw].iloc[:4].mean() # Avg of first month
            end_vol = data[product_kw].iloc[-4:].mean() # Avg of last month
            growth = ((end_vol - start_vol) / start_vol) * 100 if start_vol != 0 else 0
            
            st.metric(label="5-Year Growth Estimate", value=f"{growth:.1f}%")
        else:
            st.warning("Not enough data. Try a broader keyword (e.g. 'Tent' instead of 'Ultralight 2-person Tent')")

    except Exception as e:
        st.error(f"Google Trends Error: {e}")

    # --- SECTION B: Product Intro (Wikipedia) ---
    st.divider()
    st.subheader("2. What is this product?")
    try:
        summary = wikipedia.summary(product_kw, sentences=3)
        st.info(summary)
    except:
        st.write("No Wikipedia summary found. It might be a very niche or new product.")

    # --- SECTION C: B2B Commercial Intent ---
    st.divider()
    st.subheader("3. Commercial Intent (B2B)")
    st.markdown("Are people looking to *buy bulk* or just looking for info?")
    
    # We compare the generic term vs "wholesale/manufacturer" terms
    b2b_keywords = [product_kw, f"{product_kw} wholesale", f"{product_kw} manufacturer"]
    
    try:
        pytrends.build_payload(b2b_keywords, cat=0, timeframe='today 12-m', geo=target_country)
        b2b_data = pytrends.interest_over_time()
        
        if not b2b_data.empty:
            if 'isPartial' in b2b_data.columns: b2b_data = b2b_data.drop(columns=['isPartial'])
            st.line_chart(b2b_data)
            st.caption("Note: 'Wholesale' volume is usually much lower than the main keyword. If you see ANY movement in the colored lines, it's a good sign.")
    except:
        st.write("Could not fetch B2B comparison data.")

    # --- SECTION D: Action Links ---
    st.divider()
    st.subheader("4. Take Action")
    c1, c2, c3 = st.columns(3)
    
    # Link to find existing competitors
    search_url = f"https://www.google.com/search?q={product_kw}+brands"
    c1.link_button(f"🔍 See Competitors (Google)", search_url)
    
    # Link to find suppliers (to see if you can source it)
    alibaba_url = f"https://www.alibaba.com/trade/search?SearchText={product_kw}"
    c2.link_button(f"📦 Check Supply (Alibaba)", alibaba_url)
    
    # Link to check potential client keywords
    keyword_url = f"https://keywordseverywhere.com/"
    c3.link_button("🔑 Keyword Research Tool", keyword_url)
