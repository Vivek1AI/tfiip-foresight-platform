def calculate_cagr(start_volume, end_volume, years=10):
    """Calculates 10-Year Compound Annual Growth Rate."""
    if start_volume <= 0:
        return 0.0
    return ((end_volume / start_volume) ** (1 / years)) - 1.0

def calculate_momentum(annual_patent_counts):
    """Calculates 3-Year Momentum Velocity against baseline historical average."""
    if len(annual_patent_counts) < 10:
        return 0.0
    
    recent_3_years_sum = sum(annual_patent_counts[-3:])
    historical_baseline_avg = sum(annual_patent_counts[:-3]) / len(annual_patent_counts[:-3])
    
    if historical_baseline_avg == 0:
        return 0.0
        
    return recent_3_years_sum / (3 * historical_baseline_avg)

# --- Test Data: Carbon Capture Patent Filings Over 10 Years ---
patent_history = [12, 15, 18, 22, 30, 45, 60, 95, 140, 210]

cagr_result = calculate_cagr(patent_history[0], patent_history[-1])
momentum_result = calculate_momentum(patent_history)

print("--- TF-IIP Analytics Output ---")
print(f"10-Year CAGR: {cagr_result * 100:.2f}%")
print(f"3-Year Momentum Velocity: {momentum_result:.2f}x")