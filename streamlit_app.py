# Insert this directly into your navigation setup in streamlit_app.py:
tab0, tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🦅 Asymmetry Ledger",
    "🏢 Insiders", 
    "🏛️ Politics", 
    "🐋 Whales", 
    "🦅 MAGA Index", 
    "📋 Watchlist Manager"
])

# ==============================================================================
# TAB 0: PORTFOLIO REAL-TIME PERFORMANCE & CONVICTION ALLOCATION WEIGHTS
# ==============================================================================
with tab0:
    st.header("🦅 Asymmetry Portfolio Tracker")
    st.caption("Live asset exposure maps across corporate structures tracking raw cost cushions following May 2026 optimizations.")
    
    # Ingest the realigned positions ledger
    df_portfolio = data_store.get_live_portfolio_positions()
    
    # Calculate account summaries
    hsa_total = df_portfolio[df_portfolio["Account"] == "HSA"]["Total Value"].sum()
    blink_total = df_portfolio[df_portfolio["Account"] == "BrokerageLink"]["Total Value"].sum()
    blink_gain = df_portfolio[df_portfolio["Account"] == "BrokerageLink"]["Total Gain ($)"].sum()
    
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric(label="📊 BrokerageLink Balance", value=f"${blink_total:,.2f}", delta=f"+${blink_gain:,.2f} Account Gain")
    with col_b:
        st.metric(label="🏥 HSA Balance", value=f"${hsa_total:,.2f}", delta="Realigned (Tax-Sheltered)")
    with col_c:
        st.metric(label="📦 Combined Alpha Assets", value=f"${(blink_total + hsa_total):,.2f}")
        
    st.markdown("---")
    st.subheader("Active Position Tracking Weights")
    
    # Format structural outputs cleanly for UI rendering
    df_render = df_portfolio.copy()
    df_render["Shares"] = df_render["Shares"].map("{:,.3f}".format)
    df_render["Cost Basis"] = df_render["Cost Basis"].map("${:,.2f}".format)
    df_render["Current Price"] = df_render["Current Price"].map("${:,.2f}".format)
    df_render["Total Value"] = df_render["Total Value"].map("${:,.2f}".format)
    df_render["Total Gain ($)"] = df_render["Total Gain ($)"].map("${:,.2f}".format)
    df_render["Total Gain (%)"] = df_render["Total Gain (%)"].map("{:,.2f}%".format)
    
    # Drop intermediate processing calculation columns before showing user
    df_final_view = df_render.drop(columns=["Cost Basis Total"])
    st.dataframe(df_final_view, width="stretch")
