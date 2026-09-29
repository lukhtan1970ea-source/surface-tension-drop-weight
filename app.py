import streamlit as st
import numpy as np
from helpers import LIQUIDS, get_physical_properties, generate_svg_animation

# Базовая настройка темы приложения
st.set_page_config(page_title="Stalagmometer Pro Sim", layout="wide")

# ==========================================
# 1. ИНИЦИАЛИЗАЦИЯ И СБРОС СОСТОЯНИЯ
# ==========================================
if "tare_weight" not in st.session_state:
    st.session_state.tare_weight = round(25.123 + np.random.uniform(-0.5, 0.5), 3)
if "experiment_triggered" not in st.session_state:
    st.session_state.experiment_triggered = False
if "last_liquid" not in st.session_state:
    st.session_state.last_liquid = ""
if "last_temp" not in st.session_state:
    st.session_state.last_temp = 20.0

# ==========================================
# 2. БОКОВАЯ ПАНЕЛЬ УПРАВЛЕНИЯ
# ==========================================
st.title("🔬 Лабораторная работа: Определение поверхностного натяжения методом взвешивания капель")
st.markdown("---")

st.sidebar.header("⚙️ Параметры эксперимента")
selected_liquid = st.sidebar.selectbox("Выберите исследуемую жидкость:", list(LIQUIDS.keys()))
temperature = st.sidebar.slider("Температура жидкости (°C)", 10.0, 80.0, 20.0, 0.5)
target_drops = st.sidebar.number_input("Сколько капель отсчитать в стакан?", min_value=5, max_value=50, value=10, step=5)

# Автоматический сброс весов при изменении настроек опыта
if selected_liquid != st.session_state.last_liquid or temperature != st.session_state.last_temp:
    st.session_state.last_liquid = selected_liquid
    st.session_state.last_temp = temperature
    st.session_state.experiment_triggered = False
    st.session_state.tare_weight = round(25.123 + np.random.uniform(-0.5, 0.5), 3)

# Расчет физических констант и массы для весов
sigma_true, rho_true = get_physical_properties(selected_liquid, temperature)
R_capillary = 0.0015  
g = 9.81
mass_one_drop_true = (2 * np.pi * R_capillary * sigma_true) / g

# Индивидуальный шум для весов (чтобы данные были реалистичными)
np.random.seed(int(temperature * 7))
actual_mass_one_drop = max(1e-6, mass_one_drop_true + np.random.normal(0, mass_one_drop_true * 0.005))

st.sidebar.header("🔍 Визир микроскопа")
mic_x = st.sidebar.slider("Смещение визира по X (мм)", -2.0, 2.0, 0.0, 0.05)
mic_y = st.sidebar.slider("Смещение визира по Y (мм)", -8.0, 2.0, 0.0, 0.1)

# ==========================================
# 3. ОСНОВНОЙ РАБОЧИЙ СТЕНД
# ==========================================
col1, col2 = st.columns([1.2, 1.0])

if st.sidebar.button("🚀 Запустить дозатор жидкости", use_container_width=True):
    st.session_state.experiment_triggered = True
    js_trigger = "true"
else:
    js_trigger = "false"

# Генерация HTML кода анимации из helpers.py
svg_html = generate_svg_animation(target_drops, sigma_true, mic_x, mic_y, js_trigger)

with col1:
    st.subheader("👁️ Поле зрения визира")
    st.components.v1.html(svg_html, height=540, scrolling=False)
    st.caption("Шкала микроскопа и движение капель теперь отрисовываются на стороне браузера и работают идеально плавно.")

with col2:
    st.subheader("📊 Измерительный модуль")
    
    # Расчет текущих показателей аналитических весов
    display_drops = target_drops if st.session_state.experiment_triggered else 0
    total_drops_mass_g = (display_drops * actual_mass_one_drop) * 1000 
    current_weight = st.session_state.tare_weight + total_drops_mass_g
    
    st.metric(label="Масса сухого стакана ($m_0$)", value=f"{st.session_state.tare_weight:.3f} г")
    st.metric(label="Итоговая масса стакана с жидкостью ($m_1$)", value=f"{current_weight:.3f} г")
    
    if st.session_state.experiment_triggered:
        st.success(f"✅ Успешно отсчитано капель: {display_drops} шт.")
    else:
        st.info("💡 Нажмите кнопку на боковой панели, чтобы начать прокапывание.")

# ==========================================
# 4. ТАБЛИЦА РЕЗУЛЬТАТОВ ДЛЯ ОТЧЕТА
# ==========================================
st.markdown("---")
st.subheader("📋 Данные текущего опыта")

results_data = {
    "Параметр измерения": [
        "Исследуемая рабочая жидкость",
        "Установленная температура опыта (T)",
        "Счётчик сброшенных капель (N)",
        "Масса пустого стакана (m₀)",
        "Масса стакана с каплями (m₁)",
        "Масса чистой фракции капель (Δm)"
    ],
    "Значение": [
        selected_liquid,
        f"{temperature} °C",
        f"{display_drops} шт.",
        f"{st.session_state.tare_weight:.3f} г",
        f"{current_weight:.3f} г",
        f"{(current_weight - st.session_state.tare_weight):.3f} г"
    ]
}
st.table(results_data)
