def fetch_preshift_movers(tickers_list=None):
    """
    Scrapes live momentum gainers directly from public financial tracking lines.
    Uses structural HTML attribute targeting to maintain stability through UI updates.
    """
    try:
        # Step 1: Scan early pre-market tracking lines first
        url = "https://finance.yahoo.com/markets/stocks/pre-market-gainers/"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req).read()
        
        soup = BeautifulSoup(html, 'html.parser')
        rows = soup.find_all('tr')
        mode_label = "Pre-Market"
        
        # Verify if we captured valid financial data rows
        valid_rows = [r for r in rows if r.find('td', {'data-field': 'regularMarketPrice'})]
        
        # Step 2: Fallback to active regular session lines if pre-market is empty/closed
        if not valid_rows:
            url = "https://finance.yahoo.com/markets/stocks/gainers/"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            html = urllib.request.urlopen(req).read()
            soup = BeautifulSoup(html, 'html.parser')
            rows = soup.find_all('tr')
            valid_rows = [r for r in rows if r.find('td', {'data-field': 'regularMarketPrice'})]
            mode_label = "Intraday"
        
        movers = []
        for row in valid_rows:
            try:
                # Target structural data attributes instead of styling classes
                symbol_element = row.find('span', {'data-field': 'symbol'}) or row.find('span')
                symbol = symbol_element.text.strip() if symbol_element else None
                
                price_text = row.find('td', {'data-field': 'regularMarketPrice'}).text
                price = float(price_text.replace('$', '').replace(',', ''))
                
                gap_text = row.find('td', {'data-field': 'regularMarketChangePercent'}).text
                gap_pct = float(gap_text.replace('+', '').replace('%', '').replace(',', ''))
                
                volume_text = row.find('td', {'data-field': 'regularMarketVolume'}).text
                
                if 'M' in volume_text:
                    volume = int(float(volume_text.replace('M', '')) * 1_000_000)
                elif 'K' in volume_text:
                    volume = int(float(volume_text.replace('K', '')) * 1_000)
                else:
                    volume = int(volume_text.replace(',', ''))

                # Dynamic price ceiling filter based on session
                max_price = 5.00 if mode_label == "Pre-Market" else 10.00
                if 1.00 <= price <= max_price and gap_pct >= 2.0:
                    movers.append({
                        "Ticker": symbol,
                        "Price": f"${price:.2f}",
                        "Prev Close": f"${(price / (1 + (gap_pct/100))):.2f}",
                        "Gap/Change %": gap_pct,
                        "Volume Lines": volume,
                        "Session Source": mode_label
                    })
            except:
                continue 
                
        df = pd.DataFrame(movers)
        if not df.empty:
            return df.sort_values(by="Gap/Change %", ascending=False).reset_index(drop=True)
        return pd.DataFrame()
        
    except Exception as e:
        st.error(f"Public Data Stream Interrupted: {e}")
        return pd.DataFrame()
