import numpy as np
import plotly.graph_objects as go

# Справочные данные жидкостей при 20°C
LIQUIDS = {
    "Вода (H2O)": {"sigma_20": 72.75, "rho_20": 0.998, "temp_coeff": -0.165},
    "Этанол (C2H5OH)": {"sigma_20": 22.27, "rho_20": 0.789, "temp_coeff": -0.086},
    "Глицерин (C3H8O3)": {"sigma_20": 63.40, "rho_20": 1.261, "temp_coeff": -0.060},
    "Ацетон ((CH3)2CO)": {"sigma_20": 23.46, "rho_20": 0.791, "temp_coeff": -0.112}
}

def get_physical_properties(liquid_name, temp_c):
    """Возвращает sigma (Н/м) и rho (кг/м3) с учетом температуры"""
    data = LIQUIDS[liquid_name]
    dt = temp_c - 20.0
    sigma = (data["sigma_20"] + data["temp_coeff"] * dt) / 1000.0  # Н/м
    rho = (data["rho_20"] * (1 - 0.001 * dt)) * 1000.0            # кг/м3
    return max(0.005, sigma), max(500.0, rho)

def draw_scene(phase, growth_progress, drop_y_pos, sigma_true, drops_counted, mic_x, mic_y):
    """Отрисовка капли, микроскопа и стакана через Plotly"""
    fig = go.Figure()
    r_base = 1.0  
    y_cap = 0.0   
    
    # 1. Контур капилляра
    fig.add_trace(go.Scatter(x=[-1.5, -r_base, -r_base], y=[2.0, 2.0, y_cap], mode='lines', line=dict(color='gray', width=3), showlegend=False))
    fig.add_trace(go.Scatter(x=[1.5, r_base, r_base], y=[2.0, 2.0, y_cap], mode='lines', line=dict(color='gray', width=3), showlegend=False))
    
    critical_neck_r = max(0.2, (sigma_true * 1000) * 0.012)
    max_neck_r = r_base * 0.8
    
    # 2. Отрисовка капли в зависимости от фазы
    if phase == "growing":
        v = growth_progress
        current_neck_r = r_base - (r_base - critical_neck_r) * (v ** 2)
        drop_length = v * 4.5
        
        y_vals = np.linspace(y_cap, -drop_length, 100)
        x_vals = []
        for y in y_vals:
            ty = y / -drop_length if drop_length > 0 else 0
            if ty < 0.4:
                r = r_base - (r_base - current_neck_r) * np.sin(ty / 0.4 * np.pi / 2)
            else:
                factor = (ty - 0.4) / 0.6
                r = current_neck_r + (max_neck_r * 1.3 - current_neck_r) * np.sin(factor * np.pi)
                if factor > 0.8:
                    r *= (1.0 - (factor - 0.8) / 0.2)
            x_vals.append(max(0.01, r))
            
        x_plot = np.array(x_vals)
        fig.add_trace(go.Scatter(x=x_plot, y=y_vals, mode='lines', line=dict(color='lightblue', width=2), name='Капля'))
        fig.add_trace(go.Scatter(x=-x_plot, y=y_vals, mode='lines', line=dict(color='lightblue', width=2), fill='tonextx', fillcolor='rgba(173,216,230,0.4)', showlegend=False))

    elif phase == "falling":
        y_rest = np.linspace(y_cap, -0.5, 20)
        x_rest = r_base - (r_base - critical_neck_r) * (y_rest / -0.5)
        fig.add_trace(go.Scatter(x=x_rest, y=y_rest, mode='lines', line=dict(color='lightblue', width=2), showlegend=False))
        fig.add_trace(go.Scatter(x=-x_rest, y=y_rest, mode='lines', line=dict(color='lightblue', width=2), fill='tonextx', fillcolor='rgba(173,216,230,0.4)', showlegend=False))
        
        t = np.linspace(0, 2*np.pi, 50)
        x_fall = (critical_neck_r * 1.5) * np.cos(t)
        y_fall = drop_y_pos + (critical_neck_r * 1.8) * np.sin(t)
        fig.add_trace(go.Scatter(x=x_fall, y=y_fall, mode='lines', line=dict(color='lightblue', width=2), fill='toself', fillcolor='rgba(173,216,230,0.5)', showlegend=False))

    # 3. Стакан и уровень жидкости в нем
    fig.add_trace(go.Scatter(x=[-2.5, -2.5, 2.5, 2.5], y=[-8.0, -9.8, -9.8, -8.0], mode='lines', line=dict(color='white', width=4), showlegend=False))
    liquid_level = -9.8 + min(1.5, drops_counted * 0.05)
    fig.add_trace(go.Scatter(x=[-2.4, 2.4], y=[liquid_level, liquid_level], mode='lines', line=dict(color='rgba(173,216,230,0.6)', width=2), fill='tozeroy', fillcolor='rgba(173,216,230,0.2)', showlegend=False))

    # 4. Сетка микроскопа
    fig.add_shape(type="line", x0=-4, y0=mic_y, x1=4, y1=mic_y, line=dict(color="rgba(255,0,0,0.6)", width=1.5, dash="dash"))
    fig.add_shape(type="line", x0=mic_x, y0=2, x1=mic_x, y1=-10, line=dict(color="rgba(255,0,0,0.6)", width=1.5, dash="dash"))
    for tick in np.arange(-3.0, 3.1, 0.2):
        fig.add_shape(type="line", x0=mic_x + tick, y0=mic_y - 0.1, x1=mic_x + tick, y1=mic_y + 0.1, line=dict(color="red", width=1))

    fig.update_layout(
        xaxis=dict(range=[-4, 4], title="Шкала X (мм)", showgrid=False, zeroline=False),
        yaxis=dict(range=[-10, 2], title="Шкала Y (мм)", showgrid=False, zeroline=False),
        width=500, height=600, showlegend=False, template="plotly_dark", margin=dict(l=10, r=10, t=10, b=10)
    )
    return fig

