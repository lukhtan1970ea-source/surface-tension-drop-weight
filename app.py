import streamlit as st
import numpy as np
from helpers import LIQUIDS, get_physical_properties, generate_microscope_svg, generate_stand_svg

# Базове налаштування сторінки
st.set_page_config(page_title="Stalagmometer Pro Sim", layout="wide")

# ==========================================
# 1. ІНІЦІАЛІЗАЦІЯ ТА СКИДАННЯ СТАНУ
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
# 2. БОКОВА ПАНЕЛЬ КЕРУВАННЯ
# ==========================================
st.title("🔬 Лабораторна робота: Визначення коефіцієнта поверхневого натягу методом зважування крапель")
st.markdown("---")

st.sidebar.header("⚙️ Параметри експерименту")
selected_liquid = st.sidebar.selectbox("Оберіть досліджувану рідину:", list(LIQUIDS.keys()))
temperature = st.sidebar.slider("Температура рідини (°C)", 10.0, 80.0, 20.0, 0.5)
target_drops = st.sidebar.number_input("Скільки крапель відрахувати у склянку?", min_value=5, max_value=50, value=20, step=5)

# Автоматичне скидання ваг при зміні параметрів досліду
if selected_liquid != st.session_state.last_liquid or temperature != st.session_state.last_temp:
    st.session_state.last_liquid = selected_liquid
    st.session_state.last_temp = temperature
    st.session_state.experiment_triggered = False
    st.session_state.tare_weight = round(25.123 + np.random.uniform(-0.5, 0.5), 3)

# Розрахунок фізичних констант
sigma_true, rho_true = get_physical_properties(selected_liquid, temperature)
R_capillary = 0.0015  
g = 9.81
mass_one_drop_true = (2 * np.pi * R_capillary * sigma_true) / g

# Додавання живого шуму для ваг
np.random.seed(int(temperature * 7))
actual_mass_one_drop = max(1e-6, mass_one_drop_true + np.random.normal(0, mass_one_drop_true * 0.005))

# ==========================================
# 3. ВЛАСНЕ СТЕНД (ВКЛАДКИ)
# ==========================================
tab1, tab2 = st.tabs(["🔍 Окуляр мікроскопа (Вимірювання шийки)", "⚖️ Лабораторний стенд (Зважування крапель)"])

with tab1:
    st.subheader("👀 Вигляд через перевернуту оптику мікроскопа")
    st.markdown("_Примітка: Об'єктив мікроскопа повністю перевертає зображення. Капіляр знаходиться знизу, а крапля росте і відривається вгору._")
    
    col_mic_left, col_mic_right = st.columns([1.2, 1.0])
    
    with col_mic_right:
        st.markdown("### 🎛️ Налаштування візира мікроскопа")
        mic_x = st.slider("Зсув шкали по горизонталі X (мм)", -2.0, 2.0, 0.0, 0.05)
        mic_y = st.slider("Зсув шкали по вертикалі Y (мм)", -4.0, 4.0, 0.0, 0.05)
        st.info("💡 Наводьте перехрестя візира на краї шийки краплі безпосередньо в момент її найбільшого розтягування перед відривом.")
        
    with col_mic_left:
        # Генерація перевернутого SVG з helpers.py
        mic_svg = generate_microscope_svg(sigma_true, mic_x, mic_y)
        st.components.v1.html(mic_svg, height=440, scrolling=False)

with tab2:
    st.subheader("💧 Прокапування рідини та аналітичні ваги")
    
    col_st_left, col_st_right = st.columns([1.0, 1.2])
    
    with col_st_right:
        st.markdown("### ⚖️ Показання електронних ваг")
        
        if st.button("🚀 Запустити дозатор рідини", use_container_width=True):
            st.session_state.experiment_triggered = True
            js_trigger = "true"
        else:
            js_trigger = "false"
            
        display_drops = target_drops if st.session_state.experiment_triggered else 0
        total_drops_mass_g = (display_drops * actual_mass_one_drop) * 1000 
        current_weight = st.session_state.tare_weight + total_drops_mass_g
        
        st.metric(label="Маса сухої склянки ($m_0$)", value=f"{st.session_state.tare_weight:.3f} г")
        st.metric(label="Поточна маса склянки з рідиною ($m_1$)", value=f"{current_weight:.3f} г")
        
        if st.session_state.experiment_triggered:
            st.success(f"✅ Успішно відраховано крапель: {display_drops} шт.")
        else:
            st.info("Натисніть кнопку вище, щоб розпочати процес генерації та підрахунку крапель.")
            
    with col_st_left:
        # Генерація нормального (не перевернутого) стенду
        stand_svg = generate_stand_svg(target_drops, sigma_true, js_trigger)
        st.components.v1.html(stand_svg, height=500, scrolling=False)

# ==========================================
# 4. ЖУРНАЛ ДАНИХ (СПІЛЬНИЙ ДЛЯ ОБОХ ВКЛАДОК)
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
        f"{display_drops} шт.",
        f"{st.session_state.tare_weight:.3f} г",
        f"{current_weight:.3f} г",
        f"{(current_weight - st.session_state.tare_weight):.3f} г"
    ]
}
st.table(results_data)
