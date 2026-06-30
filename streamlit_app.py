import streamlit as st
import pandas as pd

def render_rebel_terminal_master():
    st.title("Rebel Terminal")
    st.subheader("Watchlist, Technicals, and Institutional Hedge Fund Footprints")

    # Master Watchlist Dataset mapping custom layout to all major groups discussed
    watchlist_data = {
        "Ticker": ["NVDA", "POWL", "FIX", "SMCI", "VRT"],
        "Company Name": [
            "NVIDIA Corporation", 
            "Powell Industries", 
            "Comfort Systems USA", 
            "Super Micro Computer", 
            "Vertiv Holdings Co."
        ],
        "Technical Indicator Check": [
            "Watch RSI for overbought territory; tracking volume spikes.",
            "Monitor volume trend relative to its 30-day average.",
            "Look for consolidation patterns near key moving averages.",
            "High volatility name; strictly monitor RSI cooling off.",
            "Track support levels on volume expansions."
        ],
        "Hedgefunds": [
            "Active multi-strats (Citadel) run heavy options volume while index giants (Vanguard/BlackRock) maintain structural long weight. Notably targeted by Macro funds (Aschenbrenner's Situational Awareness LP) with a massive $1.57B put option hedge line.",
            "Low concentration among the ultra-large multi-manager platforms. Primarily accumulated by mid-cap institutional growth desks and long-only sector asset managers.",
            "Steady, systematic accumulation by large long-only institutional books and industrial asset managers. Very little high-frequency pod trading or speculative options activity from the mega platforms.",
            "High-turnover favorite for multi-strategy quantitative desks (Millennium, Citadel). Heavily traded by automated systematic pods for high-frequency volatility capture rather than broad long-term macro holding.",
            "High-conviction focal point across liquid AI infrastructure themes. Clustered heavily by fundamental long/short hedge funds (Point72) and macro growth books capitalizing on data center physical buildouts."
        ]
    }

    df = pd.DataFrame(watchlist_data)

    # Render clean table matching your terminal layout
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Ticker": st.column_config.TextColumn("Ticker", width="small"),
            "Company Name": st.column_config.TextColumn("Company"),
            "Technical Indicator Check": st.column_config.TextColumn("Technical Profile"),
            "Hedgefunds": st.column_config.TextColumn("Hedge Fund Flows & Positioning")
        }
    )

if __name__ == "__main__":
    st.set_page_config(layout="wide")
    render_rebel_terminal_master()
