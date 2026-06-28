import streamlit as st

# --- 1. INITIALIZATION & CLOUD/URL SYNC ---
query_params = st.query_params

# Using 'global_watchlist' to perfectly match your other tabs and fix the AttributeError
if "global_watchlist" not in st.session_state:
    if "symbols" in query_params:
        # Pull from cloud URL parameter if it exists
        st.session_state.global_watchlist = [s.strip().upper() for s in query_params["symbols"].split(",") if s.strip()]
    else:
        # Default Whale Anchors & Bottlenecks
        st.session_state.global_watchlist = ["SMH", "SOXX", "WOLF", "LITE", "FORM", "SKYT"]


def update_cloud_storage():
    """Syncs the current global_watchlist back to the browser URL."""
    if st.session_state.global_watchlist:
        st.query_params["symbols"] = ",".join(st.session_state.global_watchlist)
    else:
        if "symbols" in st.query_params:
            del st.query_params["symbols"]


# --- 2. INTERFACE ENGINE ---
st.markdown("## 🦅 Rebel Terminal Watchlist Manager")
st.caption("Synchronized to Streamlit Cloud URL State")

# Form to safely add new tickers
with st.form(key="add_ticker_form", clear_on_submit=True):
    new_ticker = st.text_input("Enter Ticker Symbol (e.g., MU, NVDA, POWL):").strip().upper()
    submit_button = st.form_submit_button(label="⚡ Add to Watchlist")
    
    if submit_button and new_ticker:
        if new_ticker not in st.session_state.global_watchlist:
            st.session_state.global_watchlist.append(new_ticker)
            update_cloud_storage()
            st.toast(f"Added {new_ticker} to cloud matrix!", icon="✅")
            st.rerun()
        else:
            st.toast(f"{new_ticker} is already active.", icon="ℹ️")

# Render active matrix with trim buttons
if st.session_state.global_watchlist:
    st.write("### Current Active Matrix")
    for ticker in st.session_state.global_watchlist:
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"**` {ticker} `** — Tracking Institutional Order Blocks")
        with col2:
            if st.button(f"🪓 Trim", key=f"del_{ticker}"):
                st.session_state.global_watchlist.remove(ticker)
                update_cloud_storage()
                st.rerun()
else:
    st.info("Watchlist is currently empty. Add tickers above to activate the radar.")
