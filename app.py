import streamlit as st
import numpy as np
from physics import LIQUIDS, get_physical_properties
from microscope_engine import generate_microscope_svg
from helpers import generate_stand_svg

# Базове налаштування сторінки
st.set_page_config(page_title="Stalagmometer Pro Sim", layout="wide")

# ==========================================
# 1. ІНІЦІАЛІЗАЦІЯ СТАНУ СЕСІЇ
# ==========================================
if "tare_weight" not in st.session_state:
    st.session_state.tare_weight = round(25.123 + np.random.uniform(-0.5, 0.5), 3)
if "experiment_triggered" not in st.session_state:
    st.session_state.experiment_triggered = False
if "experiment_finished" not in st.session_state:
    st.session_state.experiment_finished = False
if "microscope_triggered" not in st.session_state:
    st.session_state.microscope_triggered = False
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
    st.session_state.experiment_finished = False
    st.session_state.microscope_triggered = False
    st.session_state.tare_weight = round(25.123 + np.random.uniform(-0.5, 0.5), 3)

# Автоматичний скид при зміні рідини або температури
if selected_liquid != st.session_state.last_liquid or temperature != st.session_state.last_temp:
    st.session_state.last_liquid = selected_liquid
    st.session_state.last_temp = temperature
    reset_stand_state()

# Розрахунок чесної фізики речовини
sigma_true, rho_true = get_physical_properties(selected_liquid, temperature)
R_capillary = 0.0015  
g = 9.81
mass_one_drop_true = (2 * np.pi * R_capillary * sigma_true) / g

# Легкий лабораторний шум додається ТІЛЬКИ до ваги самої рідини
np.random.seed(int(temperature * 10))
actual_mass_one_drop = max(1e-6, mass_one_drop_true + np.random.normal(0, mass_one_drop_true * 0.003))

# Повна чесна маса рідини
total_drops_mass_g = (target_drops * actual_mass_one_drop) * 1000 
current_weight = st.session_state.tare_weight + total_drops_mass_g

# ==========================================
# 3. ГОЛОВНІ ВКЛАДКИ ЛАБОРАТОРІЇ
# ==========================================
tab1, tab2 = st.tabs(["🔍 Окуляр мікроскопа (Вимірювання шийки)", "⚖️ Лабораторний стенд (Зважування крапель)"])

# ----------------------------------------------------
# ВКЛАДКА 1: ОКУЛЯР МІКРОСКОПА
# ----------------------------------------------------
with tab1:
    col_mic_left, col_mic_right = st.columns([1.2, 1.0])
    
    with col_mic_right:
        st.markdown("### 🎛️ Візуальне вимірювання талії краплі")
        
        # Локальна кнопка керування оптикою мікроскопа
        if not st.session_state.microscope_triggered:
            if st.button("💧 Подати рідину в капіляр мікроскопа", use_container_width=True):
                st.session_state.microscope_triggered = True
                st.rerun()
        else:
            if st.button("🛑 Зупинити подачу в мікроскопі", use_container_width=True):
                st.session_state.microscope_triggered = False
                st.rerun()
                
        st.info("🔬 **Порада для студентів:** Обертайте червоні гвинти тонкої наводки безпосередньо під вікном окуляра мікроскопа, щоб плавно сумістити вертикальну сітку з бічною межею шийки краплі перед її відривом.")
        st.info("Ціна кожної маленької поділки окулярного мікрометра становить строго **0.1 мм**.")
        
    with col_mic_left:
        if st.session_state.microscope_triggered:
            mic_svg = generate_microscope_svg(sigma_true, rho_true)
            st.components.v1.html(mic_svg, height=570, scrolling=False)
        else:
            st.info("💡 Натисніть кнопку «Подати рідину в капіляр», щоб спостерігати та вимірювати діаметр шийки краплі в момент відриву.")

# ----------------------------------------------------
# ВКЛАДКА 2: ЛАБОРАТОРНИЙ СТЕНД З ВАГАМИ
# ----------------------------------------------------
with tab2:
    # ІСПРАВЛЕНО: Керування дозатором перенесене прямо всередину цієї вкладки!
    st.markdown("### 🎛️ Панель керування ваговою установкою")
    col_btn1, col_btn2, col_btn3 = st.columns([1.5, 1.5, 1.0])
    
    with col_btn1:
        if st.button("💧 Відкрити затвор дозатора (Старт відліку)", use_container_width=True):
            st.session_state.experiment_triggered = True
            st.session_state.experiment_finished = False
            st.rerun()
            
    with col_btn2:
        if st.button("🔄 Перезавантажити стенд та ваги (Скид)", use_container_width=True):
            reset_stand_state()
            st.rerun()
            
    with col_btn3:
        if st.session_state.experiment_triggered:
            st.info("🔄 Йде відлік крапель...")
        elif st.session_state.experiment_finished:
            st.success("✅ Завершено!")
        else:
            st.warning("Кран перекрито")
            
    st.markdown("---")
    
    col_st_left, col_st_right = st.columns([1.0, 1.2])
    
    with col_st_right:
        st.markdown("### ⚖️ Показання електронних ваг стенду")
        w_col1, w_col2 = st.columns(2)
        w_col1.metric(label="Маса сухої склянки ($m_0$)", value=f"{st.session_state.tare_weight:.3f} г")
        
        # Кнопка фіксації результату, що з'являється тільки під час капання
        if st.session_state.experiment_triggered:
            if st.button("⚖️ Зняти показання з ваг (Зафіксувати $m_1$)", use_container_width=True):
                st.session_state.experiment_finished = True
                st.session_state.experiment_triggered = False
                st.rerun()

        if st.session_state.experiment_finished:
            w_col2.metric(label="Маса склянки з рідиною ($m_1$)", value=f"{current_weight:.3f} г")
        elif st.session_state.experiment_triggered:
            w_col2.metric(label="Маса склянки з рідиною ($m_1$)", value="Вимірювання... г")
        else:
            w_col2.metric(label="Маса склянки з рідиною ($m_1$)", value="--- г")
            
    with col_st_left:
        stand_svg = generate_stand_svg(
            target_drops, 
            sigma_true, 
            st.session_state.experiment_triggered, 
            st.session_state.experiment_finished,
            st.session_state.tare_weight, 
            total_drops_mass_g
        )
        st.components.v1.html(stand_svg, height=480, scrolling=False)

# ==========================================
# 5. СУКУПНИЙ ЖУРНАЛ ВИМІРЮВАНЬ (ДЛЯ ЗВІТУ)
# ==========================================
st.markdown("---")
st.subheader("📋 Журнал вимірювань (Вихідні дані для звіту)")

# ІСПРАВЛЕНО: Повністю прибрали m0 та m1, тепер студенти знімають масу очима з табло ваг!
results_data = {
    "Параметр вимірювання": [
        "Досліджувана робоча рідина",
        "Встановлена температура досліду (T)",
        "Лічильник скинутих крапель (N)"
    ],
    "Значення": [
        selected_liquid,
        f"{temperature} °C",
        f"{target_drops} шт." if st.session_state.experiment_finished else "0 шт."
    ]
}
st.table(results_data)

