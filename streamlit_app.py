# ==============================================================================
# 5. WATCHLIST MANAGER & TECHNICAL FOCUS LAYOUT
# ==============================================================================
with tab5:
    st.subheader("📋 Dynamic Signal Focus Console")
    st.caption("Isolate core bottleneck nodes, policy trends, and lithium/copper infrastructure positions")

    # 1. Initialize persistent session selections for specialized tickers
    if "tracked_watchlist" not in st.session_state:
        st.session_state.tracked_watchlist = ["NVDA", "LITE", "MRVL", "AXTI", "COHR", "FIX", "ALB"]

    # 2. Interactive management input panel
    updated_watchlist = st.multiselect(
        "Define Active Asymmetry Focus Matrix:",
        options=["NVDA", "LITE", "MRVL", "AXTI", "COHR", "FIX", "ALB", "AMD", "INTC", "POWL", "WOLF", "CIEN", "SNDK", "STX"],
        default=st.session_state.tracked_watchlist
    )
    
    # Sync selections back to local state engine
    st.session_state.tracked_watchlist = updated_watchlist

    st.markdown("---")
    
    # 3. Stream filtered high-signal technical analysis matrix
    if st.session_state.tracked_watchlist:
        st.markdown(f"##### 🎯 Entry Windows & Support Anchors ({len(st.session_state.tracked_watchlist)} Assets Selected)")
        try:
            # Query backend data core with thread-isolated parameters
            df_filtered_tech = data_store.get_live_technicals(st.session_state.tracked_watchlist)
            
            if not df_filtered_tech.empty:
                st.dataframe(df_filtered_tech, width="stretch", hide_index=True)
            else:
                st.info("Calculating technical momentum spreads... Verify asset matrix input flags.")
        except Exception as e:
            st.error(f"Technical trend filtering collision: {e}")
    else:
        st.warning("Focus matrix completely empty. Select target assets above to engage tracking telemetry.")
