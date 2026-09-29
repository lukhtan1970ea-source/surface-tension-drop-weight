import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

# Настройка страницы
st.set_page_config(page_title="Виртуальная Лабораторная Работа", layout="wide")

# ==========================================
# 1. СПРАВОЧНЫЕ ДАННЫЕ И ФИЗИЧЕСКАЯ МОДЕЛЬ
# ==========================================
# Свойства жидкостей при 20°C (sigma в мН/м, плотность в г/см3, dsigma/dT в мН/(м*К))
LIQUIDS = {
    "Вода (H2O)": {"sigma_20": 72.75, "rho_20": 0.998, "temp_coeff": -0.165, "molar_mass": 18.02},
    "Этанол (C2H5OH)": {"sigma_20": 22.27, "rho_20": 0.789, "temp_coeff": -0.086, "molar_mass": 46.07},
    "Глицерин (C3H8O3)": {"sigma_20": 63.40, "rho_20": 1.261, "temp_coeff": -0.060, "molar_mass": 92.09},
    "Ацетон ((CH3)2CO)": {"sigma_20": 23.46, "rho_20": 0.791, "temp_coeff": -0.112, "molar_mass": 58.08}
}

def get_physical_properties(liquid_name, temp_c):
    """Возвращает sigma (Н/м) и rho (кг/м3) с учетом температуры"""
    data = LIQUIDS[liquid_name]
    dt = temp_c - 20.0
    
    # Расчет поверхностного натяжения (переводим из мН/м в Н/м)
    sigma = (data["sigma_20"] + data["temp_coeff"] * dt) / 1000.0
    
    # Расчет плотности (приблизительное тепловое расширение для симуляции)
    rho = (data["rho_20"] * (1 - 0.001 * dt)) * 1000.0
    
    return max(0.005, sigma), max(500.0, rho)

# ==========================================
# 2. ИНИЦИАЛИЗАЦИЯ СОСТОЯНИЯ (SESSION STATE)
# ==========================================
if "tare_weight" not in st.session_state:
    # Случайный вес пустого стакана в граммах (около 25г) с точностью до мг
    st.session_state.tare_weight = round(25.123 + np.random.uniform(-0.5, 0.5), 3)
if "drops_counted" not in st.session_state:
    st.session_state.drops_counted = 0
if "experiment_running" not in st.session_state:
    st.session_state.experiment_running = False

# ==========================================
# 3. ИНТЕРФЕЙС И УПРАВЛЕНИЕ
# ==========================================
st.title("🔬 Лабораторная работа: Определение поверхностного натяжения методом взвешивания капель")
st.markdown("---")

# Боковая панель управления
st.sidebar.header("⚙️ Параметры эксперимента")
selected_liquid = st.sidebar.selectbox("Выберите исследуемую жидкость:", list(LIQUIDS.keys()))
temperature = st.sidebar.slider("Температура жидкости (°C)", 10.0, 80.0, 20.0, 0.5)
target_drops = st.sidebar.number_input("Сколько капель отсчитать в стакан?", min_value=10, max_value=100, value=50, step=5)

# Расчет истинных физических параметров стенда
sigma_true, rho_true = get_physical_properties(selected_liquid, temperature)

# Базовый радиус капилляра (справочный, пусть будет 1.2 мм)
R_capillary = 0.0012 
# Масса одной капли по закону Тейте (с поправкой)
g = 9.81
mass_one_drop_true = (2 * np.pi * R_capillary * sigma_true) / g

# Добавляем небольшой шум к массе капель для реалистичности
np.random.seed(int(temperature * 10)) 
mass_noise = np.random.normal(0, mass_one_drop_true * 0.01)
actual_mass_one_drop = max(1e-6, mass_one_drop_true + mass_noise)

# --- Управление микроскопом ---
st.sidebar.header("🔍 Настройка микроскопа")
mic_y = st.sidebar.slider("Смещение шкалы по вертикали (Y)", -2.0, 2.0, 0.0, 0.1)
mic_x = st.sidebar.slider("Смещение шкалы по горизонтали (X)", -2.0, 2.0, 0.0, 0.1)
scale_division = 0.05 # Цена деления шкалы в мм

# ==========================================
# 4. ЦЕНТРАЛЬНАЯЗОНА: АНИМАЦИЯ И СТЕНД
# ==========================================
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("👁️ Вид в окуляр микроскопа (Шейка капли)")
    
    # Эмпирический радиус шейки в момент отрыва зависит от поверхностного натяжения
    # Чем меньше натяжение, тем тоньше шейка перед разрывом
    neck_radius_mm = (sigma_true * 1000) * 0.04 
    
    # Отрисовка капли и шкалы через Plotly
    fig_mic = go.Figure()
    
    # 1. Рисуем контур шейки капли (параболическое сужение)
    y_drop = np.linspace(0, 4, 100)
    # Форма капли: сужение в районе y=2 (шейка)
    x_drop_right = neck_radius_mm + 0.2 * (y_drop - 2)**2
    x_drop_left = -x_drop_right
    
    fig_mic.add_trace(go.Scatter(x=x_drop_right, y=y_drop, mode='lines', line=dict(color='lightblue', width=3), name='Капля'))
    fig_mic.add_trace(go.Scatter(x=x_drop_left, y=y_drop, mode='lines', line=dict(color='lightblue', width=3), fill='tonextx', fillcolor='rgba(173,216,230,0.3)', showlegend=False))
    
    # 2. Рисуем шкалу микроскопа (сетка рисок) с учетом смещения студента (mic_x, mic_y)
    scale_y = 2.0 + mic_y
    for tick in np.arange(-3.0, 3.1, scale_division * 4): # Шаг рисок
        tick_x = tick + mic_x
        # Длинные и короткие риски
        tick_len = 0.3 if abs(tick) < 0.01 or round(tick, 2) % 0.4 == 0 else 0.15
        
        # Риски слева и справа
        fig_mic.add_shape(type="line", x0=tick_x, y0=scale_y-tick_len, x1=tick_x, y1=scale_y+tick_len, line=dict(color="red", width=1.5))
        
    # Центральная перекрестная линия микроскопа
    fig_mic.add_shape(type="line", x0=-4, y0=scale_y, x1=4, y1=scale_y, line=dict(color="rgba(255,0,0,0.5)", width=1, dash="dash"))
    fig_mic.add_shape(type="line", x0=mic_x, y0=0, x1=mic_x, y1=4, line=dict(color="rgba(255,0,0,0.5)", width=1, dash="dash"))

    # Настройки отображения окуляра
    fig_mic.update_layout(
        xaxis=dict(range=[-3, 3], title="Координата X (мм)", showgrid=False),
        yaxis=dict(range=[0, 4], title="Координата Y (мм)", showgrid=False),
        width=450, height=450,
        showlegend=False,
        margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor='black' # Симулируем темноту в микроскопе
    )
    st.plotly_chart(fig_mic, use_container_width=True)
    st.caption("Используйте ползунки микроскопа слева, чтобы совместить шкалу с границами шейки капли (в самом узком месте).")

with col2:
    st.subheader("💧 Счётчик капель и весы")
    
    # Интерактивные кнопки
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        if st.button("🚀 Запустить генерацию капель", use_container_width=True):
            st.session_state.experiment_running = True
            st.session_state.drops_counted = 0
    with btn_col2:
        if st.button("🔄 Сбросить эксперимент", use_container_width=True):
            st.session_state.drops_counted = 0
            st.session_state.experiment_running = False
            st.rerun()

    # Процесс анимации капания
    status_text = st.empty()
    progress_bar = st.progress(0.0)
    
    if st.session_state.experiment_running and st.session_state.drops_counted < target_drops:
        status_text.markdown("⏳ **Идет динамический отсчет капель в стакан...**")
        for i in range(1, target_drops + 1):
            time.sleep(0.08) # Скорость анимации капания
            st.session_state.drops_counted = i
            progress_bar.progress(i / target_drops)
        st.session_state.experiment_running = False
        st.balloons()
    
    # Вывод текущего состояния весов
    st.markdown("### ⚖️ Показания электронных весов")
    
    # Расчет текущей массы стакана
    total_drops_mass_g = (st.session_state.drops_counted * actual_mass_one_drop) * 1000 # переводим кг -> г
    current_weight = st.session_state.tare_weight + total_drops_mass_g
    
    w_col1, w_col2 = st.columns(2)
    w_col1.metric(label="Масса пустого стакана ($m_0$)", value=f"{st.session_state.tare_weight:.3f} г")
    w_col2.metric(label="Текущая масса стакана ($m_{общ}$)", value=f"{current_weight:.3f} г")
    
    st.info(f"**Капель упало в стакан:** {st.session_state.drops_counted} / {target_drops}")

# ==========================================
# 5. ТАБЛИЦА РЕЗУЛЬТАТОВ И ИСХОДНЫХ ДАННЫХ
# ==========================================
st.markdown("---")
st.subheader("📊 Журнал текущих измерений (Исходные данные для отчета)")

# Формируем структуру данных для вывода студенту
results_data = {
    "Параметр": [
        "Исследуемая жидкость",
        "Установленная температура (T)",
        "Заданное количество капель (N)",
        "Фактически отсчитано капель",
        "Масса пустого стакана (m₀)",
        "Масса стакана с каплями (m₁)",
        "Масса отделившейся жидкости (Δm)"
    ],
    "Значение": [
        selected_liquid,
        f"{temperature} °C",
        f"{target_drops} шт.",
        f"{st.session_state.drops_counted} шт.",
        f"{st.session_state.tare_weight:.3f} г",
        f"{current_weight:.3f} г",
        f"{(current_weight - st.session_state.tare_weight):.3f} г"
    ]
}

st.table(results_data)

st.markdown("""
### 📝 Задание для студентов:
1. По шкале микроскопа определите **диаметр $d$ шейки капли** в момент отрыва (координата X левой и правой границ в самом узком месте).
2. Зафиксируйте массу пустого стакана $m_0$ и полную массу $m_1$ после падения $N$ капель.
3. Рассчитайте массу одной капли: $m = (m_1 - m_0) / N$.
4. Используя закон Тейте ($m \cdot g = \pi \cdot d \cdot \sigma$), вычислите экспериментальное значение коэффициента поверхностного натяжения $\sigma$.
5. Повторите опыт для других температур и постройте график зависимости $\sigma(T)$.
""")

