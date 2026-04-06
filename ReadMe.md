# VIX Regime Analysis & Equity Market Behavior

This project analyzes how equity returns and volatility behave across different **VIX regimes**.

Using **SPY** and **VIX** data, the market is segmented into four volatility regimes *(low, normal, elevated, stress)*. The analysis evaluates **forward returns**, **risk-adjusted performance**, and **future realized volatility** across these regimes.

The goal is to understand whether volatility is just a **risk measure**, or a **driver of return opportunities**.

---

## Methodology

The project demonstrates a full **quantitative research workflow**:

- **regime classification** using VIX thresholds  
- **forward return analysis** *(1D, 5D, 20D horizons)*  
- **Sharpe ratio comparison** across regimes  
- **realized volatility forecasting**  
- **event vs regime-based signal comparison**  
- **statistical testing** *(t-tests)*  

---

## Example Outputs

Example outputs produced by the project include:

- **SPY vs VIX time series visualization**  
- **forward return comparison charts by regime**  
- **Sharpe ratio tables across volatility environments**  
- **realized volatility comparisons**  
- **VIX spike vs non-spike return analysis**  

---

## Key Findings

- High-volatility regimes generate **higher forward returns**  
- Stress regimes deliver **strongest risk-adjusted performance**  
- Volatility is **persistent** and predicts future realized volatility  
- Market stress creates **temporary dislocations and mean reversion opportunities**  
- **Regime-based signals** are more informative than single-day spikes  

---

## Assets Used

- **SPY** *(S&P 500 ETF)*  
- **VIX** *(CBOE Volatility Index)*  

---

## Repository Contents

- `vix_analysis.py` — main research and analysis script  
- `VIX_Regimes_Report.pdf` — full research report  
- `README.md` — project overview  

---

## Future Improvements

- Incorporate **transaction costs and position sizing**  
- Build a **regime-based trading strategy with backtesting**  
- Use **dynamic regime classification** *(clustering / HMM)*  
- Extend to **cross-asset signals** *(rates, credit, commodities)*  
- Deploy as an **interactive dashboard**  
