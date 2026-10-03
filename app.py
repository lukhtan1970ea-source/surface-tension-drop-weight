import streamlit as st
import numpy as np
from physics import LIQUIDS, get_physical_properties
from microscope_engine import generate_microscope_svg
from helpers import generate_stand_svg

# Базове налаштування сторінки
st.set_page_config(page_title="Stalagmometer Pro Sim", layout="wide")

# ==========================================
# 1. ІНІЦІАЛІЗАЦІЯ ТА СКИДАННЯ СТАНУ
# ==========================================
# Жорстко фіксуємо масу склянки один раз при старті сесії! Вона БІЛЬШЕ НЕ ЗМІНЮЄТЬСЯ від температури
if "tare_weight" not in st.session_state:
    st.session_state.tare_weight = round(25.123 + np.random.uniform(-0.5, 0.5), 3)
if "experiment_triggered" not in st.session_state:
    st.session_state.experiment_triggered = False
if "last_liquid" not in st.session_state:
    st.session_state.last_liquid = ""
if "last_temp" not in st.session_state:
    st.session_state.last_temp = 20.0

# ==========================================
# 2. БОКОВА ПАНЕЛЬ КЕРУВАННЯ
# ==========================================
st.title("🔬 Лабораторна робота: Визначення коефіцієнта поверхневого натягу методом зважування крапель")
st.markdown("---")

st.sidebar.header("⚙️ Параметри експерименту")
selected_liquid = st.sidebar.selectbox("Оберіть досліджувану рідину:", list(LIQUIDS.keys()))
temperature = st.sidebar.slider("Температура рідини (°C)", 10.0, 80.0, 20.0, 0.5)
target_drops = st.sidebar.number_input("Скільки крапель відрахувати у склянку?", min_value=5, max_value=50, value=20, step=5)

def reset_stand_state():
    st.session_state.experiment_triggered = False
    # Перегенерація тари відбувається ТІЛЬКИ при повному ручному скиданні стенду кнопкою
    st.session_state.tare_weight = round(25.123 + np.random.uniform(-0.5, 0.5), 3)

# Автоматичний скид дозатора при зміні параметрів, але БЕЗ зміни сухої ваги стакана!
if selected_liquid != st.session_state.last_liquid or temperature != st.session_state.last_temp:
    st.session_state.last_liquid = selected_liquid
    st.session_state.last_temp = temperature
    st.session_state.experiment_triggered = False

# Розрахунок чесної фізики речовини
sigma_true, rho_true = get_physical_properties(selected_liquid, temperature)
R_capillary = 0.0015  
g = 9.81
mass_one_drop_true = (2 * np.pi * R_capillary * sigma_true) / g

# Легкий лабораторний шум додається ТІЛЬКИ до ваги самої рідини
np.random.seed(int(temperature * 10))
actual_mass_one_drop = max(1e-6, mass_one_drop_true + np.random.normal(0, mass_one_drop_true * 0.003))

# ==========================================
# 3. ВЕРХНЯ ПАНЕЛЬ УПРАВЛІННЯ
# ==========================================
ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([1.5, 1.5, 1.0])

with ctrl_col1:
    if st.button("💧 Відкрити затвор дозатора рідини", use_container_width=True):
        st.session_state.experiment_triggered = True

with ctrl_col2:
    if st.button("🔄 Перезавантажити стенд", use_container_width=True):
        reset_stand_state()
        st.rerun()

display_drops = target_drops if st.session_state.experiment_triggered else 0
total_drops_mass_g = (display_drops * actual_mass_one_drop) * 1000 
current_weight = st.session_state.tare_weight + total_drops_mass_g

with ctrl_col3:
    if st.session_state.experiment_triggered:
        st.success(f"Ціль досліду: {target_drops} шт.")
    else:
        st.warning("Дозатор перекрито")

st.markdown(" ")

# ==========================================
# 4. ГОЛОВНІ ВКЛАДКИ
# ==========================================
tab1, tab2 = st.tabs(["🔍 Окуляр мікроскопа (Вимірювання шийки)", "⚖️ Лабораторний стенд (Зважування крапель)"])

with tab1:
    col_mic_left, col_mic_right = st.columns([1.2, 1.0])
    
    with col_mic_right:
        st.markdown("### 🎛️ Налаштування візира мікроскопа")
        mic_x = st.slider("Зсув шкали по горизонталі X (мм)", -2.0, 2.0, 0.0, 0.01)
        mic_y = st.slider("Зсув шкали по вертикалі Y (мм)", -4.0, 4.0, 0.0, 0.01)
        st.info("🔬 **Порада для студентів:** Сумістіть вертикальну лінію червоної шкали з бічною межею шийки краплі перед самим її відривом за допомогою гвинтів тонкої наводки.")
        
    with col_mic_left:
        if st.session_state.experiment_triggered:
            mic_svg = generate_microscope_svg(sigma_true, rho_true, mic_x, mic_y)
            st.components.v1.html(mic_svg, height=440, scrolling=False)
        else:
            st.info("💡 Відкрийте затвор дозатора рідини вище, щоб спостерігати капілярну грушу в окулярі мікроскопа.")

with tab2:
    col_st_left, col_st_right = st.columns([1.0, 1.2])
    
    with col_st_right:
        st.markdown("### ⚖️ Показання електронних ваг")
        w_col1, w_col2 = st.columns(2)
        w_col1.metric(label="Маса сухої склянки ($m_0$)", value=f"{st.session_state.tare_weight:.3f} г")
        
        if st.session_state.experiment_triggered:
            w_col2.metric(label="Маса склянки з рідиною ($m_1$)", value=f"{current_weight:.3f} г")
            st.info(f"**Mass фракції крапель (Δm):** {current_weight - st.session_state.tare_weight:.3f} г")
        else:
            w_col2.metric(label="Маса склянки з рідиною ($m_1$)", value="--- г")
            st.info("**Маса чистої фракції крапель (Δm):** Очікування запуску...")
            
    with col_st_left:
        # Передаємо точну масу фракції прямо з розрахунку для залізобетонного збігу табло
        stand_svg = generate_stand_svg(target_drops, sigma_true, st.session_state.experiment_triggered, st.session_state.tare_weight, total_drops_mass_g)
        st.components.v1.html(stand_svg, height=480, scrolling=False)

# ==========================================
# 5. СУКУПНИЙ ЖУРНАЛ ВИМІРЮВАНЬ
# ==========================================
st.markdown("---")
st.subheader("📋 Журнал вимірювань (Вихідні дані для звіту)")

results_data = {
    "Параметр вимірювання": [
        "Досліджувана робоча рідина",
        "Встановлена температура досліду (T)",
        "Лічильник скинутих крапель (N)",
        "Маса порожньої склянки (m₀)",
        "Маса склянки з краплями (m₁)",
        "Маса чистої фракції крапель (Δm)"
    ],
    "Значення": [
        selected_liquid,
        f"{temperature} °C",
        f"{target_drops} шт." if st.session_state.experiment_triggered else "0 шт.",
        f"{st.session_state.tare_weight:.3f} г",
        f"{current_weight:.3f} г" if st.session_state.experiment_triggered else "--- г",
        f"{(current_weight - st.session_state.tare_weight):.3f} г" if st.session_state.experiment_triggered else "--- г"
    ]
}
st.table(results_data)
