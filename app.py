import streamlit as st
import numpy as np
import time
from helpers import LIQUIDS, get_physical_properties, draw_scene

# Настройка страницы
st.set_page_config(page_title="Stalagmometer Pro Sim", layout="wide")

# ==========================================
# 1. ИНИЦИАЛИЗАЦИЯ СОСТОЯНИЯ (SESSION STATE)
# ==========================================
if "tare_weight" not in st.session_state:
    st.session_state.tare_weight = round(25.123 + np.random.uniform(-0.5, 0.5), 3)
if "drops_counted" not in st.session_state:
    st.session_state.drops_counted = 0
if "current_liquid" not in st.session_state:
    st.session_state.current_liquid = list(LIQUIDS.keys())[0]
if "current_temp" not in st.session_state:
    st.session_state.current_temp = 20.0

# ==========================================
# 2. ИНТЕРФЕЙС И УПРАВЛЕНИЕ
# ==========================================
st.title("🔬 Лабораторная работа: Определение поверхностного натяжения методом взвешивания капель")
st.markdown("---")

st.sidebar.header("⚙️ Параметры эксперимента")
selected_liquid = st.sidebar.selectbox("Выберите исследуемую жидкость:", list(LIQUIDS.keys()))
temperature = st.sidebar.slider("Температура жидкости (°C)", 10.0, 80.0, 20.0, 0.5)
target_drops = st.sidebar.number_input("Сколько капель отсчитать в стакан?", min_value=5, max_value=50, value=10, step=5)

# Сброс при смене параметров
if selected_liquid != st.session_state.current_liquid or temperature != st.session_state.current_temp:
    st.session_state.current_liquid = selected_liquid
    st.session_state.current_temp = temperature
    st.session_state.drops_counted = 0
    st.session_state.tare_weight = round(25.123 + np.random.uniform(-0.5, 0.5), 3)

sigma_true, rho_true = get_physical_properties(selected_liquid, temperature)

# Физические константы
R_capillary = 0.0015  
g = 9.81
mass_one_drop_true = (2 * np.pi * R_capillary * sigma_true) / g

np.random.seed(int(temperature * 7))
actual_mass_one_drop = max(1e-6, mass_one_drop_true + np.random.normal(0, mass_one_drop_true * 0.005))

# --- Управление микроскопом ---
st.sidebar.header("🔍 Визир микроскопа")
mic_x = st.sidebar.slider("Смещение визира по горизонтали (X)", -2.0, 2.0, 0.0, 0.05)
mic_y = st.sidebar.slider("Смещение визира по вертикали (Y)", -8.0, 2.0, 0.0, 0.1)

# ==========================================
# 3. СТЕНД ЭКСПЕРИМЕНТА
# ==========================================
col1, col2 = st.columns(2)

with col1:
    st.subheader("🔬 Поле зрения микроскопа")
    plot_placeholder = st.empty()
    # Первичный вывод сцены (фиксированная ширина, статический режим)
    fig_init = draw_scene("growing", 0.0, 0.0, sigma_true, st.session_state.drops_counted, mic_x, mic_y)
    plot_placeholder.plotly_chart(fig_init, use_container_width=False, config={'staticPlot': True})

with col2:
    st.subheader("📊 Управление и Весы")
    
    if st.button("🚀 Запустить дозатор жидкости", use_container_width=True):
        st.session_state.drops_counted = 0
        
        for d in range(target_drops):
            # 1. Фаза роста
            steps_growth = 15  # Немного уменьшим шаги для увеличения скорости и плавности
            for step in range(steps_growth):
                progress = step / float(steps_growth - 1)
                fig = draw_scene("growing", progress, 0.0, sigma_true, st.session_state.drops_counted, mic_x, mic_y)
                plot_placeholder.plotly_chart(fig, use_container_width=False, config={'staticPlot': True})
                time.sleep(0.03)
            
            # Пауза перед отрывом
            time.sleep(0.15)
            
            # 2. Фаза падения капли в стакан
            y_start = -4.5
            y_end = -9.5
            steps_fall = 5
            for step in range(steps_fall):
                pos_y = y_start + (y_end - y_start) * (step / float(steps_fall - 1))
                fig = draw_scene("falling", 1.0, pos_y, sigma_true, st.session_state.drops_counted, mic_x, mic_y)
                plot_placeholder.plotly_chart(fig, use_container_width=False, config={'staticPlot': True})
                time.sleep(0.015)
                
            st.session_state.drops_counted += 1
            
        # Финальное обновление весов и картинки
        fig_final = draw_scene("growing", 0.0, 0.0, sigma_true, st.session_state.drops_counted, mic_x, mic_y)
        plot_placeholder.plotly_chart(fig_final, use_container_width=False, config={'staticPlot': True})
        st.balloons()



    # Измерительный блок весов
    st.markdown("### ⚖️ Электронные аналитические весы")
    total_drops_mass_g = (st.session_state.drops_counted * actual_mass_one_drop) * 1000 
    current_weight = st.session_state.tare_weight + total_drops_mass_g
    
    st.metric(label="Масса сухого стакана ($m_0$)", value=f"{st.session_state.tare_weight:.3f} г")
    st.metric(label="Текущая масса стакана с жидкостью ($m_1$)", value=f"{current_weight:.3f} г")
    st.success(f"**Счётчик капель:** {st.session_state.drops_counted} / {target_drops} шт.")

# ==========================================
# 4. ЖУРНАЛ ДАННЫХ
# ==========================================
st.markdown("---")
st.subheader("📋 Данные текущего опыта")

results_data = {
    "Параметр измерения": [
        "Исследуемая рабочая жидкость",
        "Установленная температура опыта (T)",
        "Счётчик сброшенных капель (N)",
        "Масса пустого бюкса (m₀)",
        "Масса бюкса с каплями (m₁)",
        "Масса чистой фракции капель (Δm)"
    ],
    "Значение": [
        selected_liquid,
        f"{temperature} °C",
        f"{st.session_state.drops_counted} шт.",
        f"{st.session_state.tare_weight:.3f} г",
        f"{current_weight:.3f} г",
        f"{(current_weight - st.session_state.tare_weight):.3f} г"
    ]
}
st.table(results_data)

