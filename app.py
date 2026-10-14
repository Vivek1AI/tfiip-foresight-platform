# Mechanical Engineering Conversion Tool

def kw_to_hp(kilowatts):
    """Converts Kilowatts (kW) to Horsepower (hp)."""
    horsepower = kilowatts * 1.34102
    return horsepower

# Input power in kW
power_kw = 100
power_hp = kw_to_hp(power_kw)

print(f"{power_kw} kW is equal to {power_hp:.2f} HP")