import streamlit as st
import pandas as pd

def render_institution_tracker():
    st.header("Institutional & Hedge Fund Master Matrix")
    st.write("Cross-market analysis of asset management giants vs. tactical macro/quant platforms.")

    # 1. Build the dataset
    data = {
        "Rank": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "Entity / Fund": [
            "BlackRock", "Vanguard", "State Street", "Citadel LLC", 
            "Millennium Management", "Bridgewater Associates", 
            "Point72 Asset Management", "D. E. Shaw & Co.", 
            "Renaissance Technologies", "Situational Awareness LP"
        ],
        "Classification": [
            "Asset Manager", "Asset Manager", "Asset Manager", "Mega Hedge Fund", 
            "Mega Hedge Fund", "Institutional Fund", "Elite Hedge Fund", 
            "Pioneer Quant Fund", "Pure Quant Fund", "Macro Hedge Fund"
        ],
        "Core Strategy": [
            "Passive Index / Active", "Pure Passive Indexing", "Passive Indexing / Sector", 
            "Multi-Strategy Platform", "Multi-Manager (Pod Model)", "Systematic Global Macro", 
            "Fundamental Long/Short", "Quantitative / Systematic", "Mathematical Modeling", 
            "Deep Thesis Sovereign Macro"
        ],
        "Public 13F Footprint (U.S.)": [
            "~$3.5+ Trillion", "~$4.5+ Trillion", "~$1.1+ Trillion", "~$100B - $150B+", 
            "~$571 Billion", "~$97 Billion", "~$110B+", "~$60B - $80B", 
            "~$60B+", "~$13.68 Billion"
        ],
        "Total Global AUM": [
            "~$10.5+ Trillion", "~$9.2+ Trillion", "~$5.6+ Trillion", "~$69 Billion", 
            "~$89+ Billion", "~$78 Billion", "~$30+ Billion", "~$60+ Billion", 
            "~$45+ Billion", "~Under $5B"
        ],
        "Core AI & Tech Investment Style": [
            "Structural long exposure; automatically owns 7-10% of every mega-cap chip and infrastructure name.",
            "Identical to BlackRock—owns massive stakes in NVDA, MSFT, AAPL purely to match index weights.",
            "Captures highly targeted tech and sector flows via specialized industry baskets.",
            "Highly tactical. Uses massive options structures to hedge or bet on semi/big-tech volatility.",
            "Highly fragmented. Hundreds of independent 'pods' trade tech momentum, earnings, and arbitrage.",
            "Trades tech and semis purely as a macroeconomic proxy for liquidity, inflation, and growth cycles.",
            "Deep corporate research; aggressive, concentrated fundamental bets on semiconductor cycles and hardware.",
            "Blends math-driven predictive models with specialized fundamental energy and tech infrastructure teams.",
            "Completely systematic. Trades short-term mathematical anomalies in chip and hardware stock patterns.",
            "Hyper-concentrated on AI bottlenecks: nuclear/on-site power, physical hosting, and data storage."
        ],
        "Dominant Trading Vehicle": [
            "Market weight ETFs (iShares).", "Mutual Funds & Low-cost ETFs (VOO, VGT).", 
            "Sector SPDR ETFs (XLK, XLE).", "Heavy derivative options overlays over equity.", 
            "High-frequency, high-turnover long/short equity.", "Index tracking ETFs and liquid macro baskets.", 
            "Long/short individual tech equities via alternative data.", "Proprietary algorithmic execution & relative-value arb.", 
            "Pure non-fundamental quantitative algorithms.", "Barbell Strategy: Infrastructure longs vs. Semi index puts."
        ],
        "Leadership": [
            "Larry Fink", "Salim Ramji", "Yie-Hsin Hung", "Ken Griffin", 
            "Izzy Englander", "Bob Prince", "Steve Cohen", "Executive Committee", 
            "Peter Brown", "Leopold Aschenbrenner"
        ]
    }

    df = pd.DataFrame(data)

    # 2. Sidebar Filters for Interactivity
    st.sidebar.subheader("Matrix Filters")
    all_classes = ["All"] + list(df["Classification"].unique())
    selected_class = st.sidebar.selectbox("Filter by Classification", all_classes)

    search_query = st.sidebar.text_input("Search Fund or Leader", "")

    # 3. Apply Filters to Dataframe
    filtered_df = df.copy()
    if selected_class != "All":
        filtered_df = filtered_df[filtered_df["Classification"] == selected_class]
        
    if search_query:
        filtered_df = filtered_df[
            filtered_df["Entity / Fund"].str.contains(search_query, case=False) |
            filtered_df["Leadership"].str.contains(search_query, case=False)
        ]

    # 4. Render Layout
    st.dataframe(
        filtered_df, 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "Rank": st.column_config.NumberColumn("Rank", width="small"),
            "Entity / Fund": st.column_config.TextColumn("Fund / Firm", help="Official corporate or fund entity name"),
            "Public 13F Footprint (U.S.)": st.column_config.TextColumn("13F Value", help="Regulatory long equity/options footprint"),
            "Total Global AUM": st.column_config.TextColumn("Total AUM", help="Total global capital under management")
        }
    )

    # Context Highlight Block
    st.info(
        "**Note on Footprint vs. AUM:** Platform hedge funds (like Millennium) showcase a 13F footprint "
        "vastly larger than their physical AUM due to heavy regulatory options leverage. Conversely, passive giants "
        "like Vanguard reflect the broader global retail market flow."
    )

if __name__ == "__main__":
    # If running standalone for testing
    st.set_page_config(layout="wide")
    render_institution_tracker()
