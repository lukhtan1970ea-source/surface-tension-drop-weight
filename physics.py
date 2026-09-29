# Довідкові дані рідин при 20°C
LIQUIDS = {
    "Вода (H2O)": {"sigma_20": 72.75, "rho_20": 0.998, "temp_coeff": -0.165},
    "Етанол (C2H5OH)": {"sigma_20": 22.27, "rho_20": 0.789, "temp_coeff": -0.086},
    "Гліцерин (C3H8O3)": {"sigma_20": 63.40, "rho_20": 1.261, "temp_coeff": -0.060},
    "Ацетон ((CH3)2CO)": {"sigma_20": 23.46, "rho_20": 0.791, "temp_coeff": -0.112}
}

def get_physical_properties(liquid_name, temp_c):
    """Обчислює поверхневий натяг та щільність залежно від температури"""
    data = LIQUIDS[liquid_name]
    dt = temp_c - 20.0
    sigma = (data["sigma_20"] + data["temp_coeff"] * dt) / 1000.0  # Н/м
    rho = (data["rho_20"] * (1 - 0.001 * dt)) * 1000.0            # кг/м3
    return max(0.005, sigma), max(500.0, rho)
