import numpy as np

LIQUIDS = {
    "Вода (H2O)": {"sigma_20": 72.75, "rho_20": 0.998, "temp_coeff": -0.165},
    "Етанол (C2H5OH)": {"sigma_20": 22.27, "rho_20": 0.789, "temp_coeff": -0.086},
    "Гліцерин (C3H8O3)": {"sigma_20": 63.40, "rho_20": 1.261, "temp_coeff": -0.060},
    "Ацетон ((CH3)2CO)": {"sigma_20": 23.46, "rho_20": 0.791, "temp_coeff": -0.112}
}

def get_physical_properties(liquid_name, temp_c):
    data = LIQUIDS[liquid_name]
    dt = temp_c - 20.0
    sigma = (data["sigma_20"] + data["temp_coeff"] * dt) / 1000.0
    rho = (data["rho_20"] * (1 - 0.001 * dt)) * 1000.0
    return max(0.005, sigma), max(500.0, rho)

def generate_microscope_svg(sigma_true, mic_x, mic_y):
    # Координаты визира (1 мм = 50 пикселей)
    svg_mic_x = 200 + (mic_x * 50)
    svg_mic_y = 200 - (mic_y * 50)
    
    # Расчет критической ширины шейки (в пикселях)
    w = max(12.0, min(28.0, (sigma_true * 1000) * 0.38))
    wb = w * 1.5 # Ширина самой капли
    
    # Формируем риски шкалы
    ticks_html = ""
    for i in range(-200, 201, 10):
        t_len = 14 if i % 50 == 0 else 7
        ticks_html += f'<line x1="{svg_mic_x + i}" y1="{svg_mic_y - t_len}" x2="{svg_mic_x + i}" y2="{svg_mic_y + t_len}" stroke="red" stroke-width="1" />'

    # Перевёрнутая каплевидная форма (растёт вверх от Y=320)
    # M (старт слева) -> C (кривая к вершине капли) -> A (округлая маковка) -> C (симметричный спуск вниз справа) -> Z (закрытие)
    path_d = f"M {200-w},320 C {200-w},290 {200-wb},270 {200-wb},240 A {wb},{wb*1.2} 0 0,1 {200+wb},240 C {200+wb},270 {200+w},290 {200+w},320 Z"

    html_code = f"""
    <div style="background: #111; padding: 10px; border-radius: 8px; width: 420px; margin: 0 auto;">
        <svg width="400" height="400" viewBox="0 0 400 400" style="background: #030803; border: 3px solid #333; border-radius: 50%;">
            <style>
                @keyframes growUpAnimation {{
                    0% {{ transform: scaleY(0.2) scaleX(0.6) translate(0, 0); opacity: 0.8; }}
                    85% {{ transform: scaleY(1.0) scaleX(1.0) translate(0, -10px); opacity: 1; }}
                    93% {{ transform: scaleY(1.0) scaleX(0.8) translate(0, -250px); opacity: 0.3; }}
                    100% {{ transform: scaleY(0.2) scaleX(0.6) translate(0, 0); opacity: 0; }}
                }}
                .drop-tear-mic {{
                    transform-origin: 200px 320px;
                    animation: growUpAnimation 4.5s infinite cubic-bezier(0.4, 0, 0.6, 1);
                }}
            </style>
            
            <!-- Перевернутый капилляр -->
            <rect x="165" y="320" width="70" height="80" fill="#444" />
            <rect x="170" y="320" width="60" height="80" fill="#080f08" />
            
            <!-- Настоящая каплевидная форма -->
            <path d="{path_d}" class="drop-tear-mic" fill="rgba(100,200,255,0.55)" stroke="lightskyblue" stroke-width="2" />

            <!-- Шкала микроскопа -->
            <line x1="0" y1="{svg_mic_y}" x2="400" y2="{svg_mic_y}" stroke="rgba(255,0,0,0.8)" stroke-width="1.5" />
            <line x1="{svg_mic_x}" y1="0" x2="{svg_mic_x}" y2="400" stroke="rgba(255,0,0,0.8)" stroke-width="1.5" />
            {ticks_html}
        </svg>
    </div>
    """
    return html_code

def generate_stand_svg(target_drops, sigma_true, is_running):
    w = max(8.0, min(20.0, (sigma_true * 1000) * 0.28))
    wb = w * 1.5
    
    # Нормальная каплевидная форма (растёт и падает вниз от Y=60)
    path_d = f"M {160-w},60 C {160-w},90 {160-wb},110 {160-wb},140 A {wb},{wb*1.2} 0 0,0 {160+wb},140 C {160+wb},110 {160+w},90 {160+w},60 Z"
    
    animation_style = ""
    if is_running:
        animation_style = """
        @keyframes dropFallingCycle {
            0% { transform: scale(0.3) translate(0, 0); opacity: 0.7; }
            65% { transform: scale(1.0) translate(0, 5px); opacity: 1; }
            90% { transform: scale(0.9) translate(0, 290px); opacity: 1; }
            100% { transform: scale(0.3) translate(0, 310px); opacity: 0; }
        }
        .drop-tear-stand {
            transform-origin: 160px 60px;
            animation: dropFallingCycle 0.9s infinite ease-in;
        }
        """
    
    html_code = f"""
    <div style="background: #111; padding: 10px; border-radius: 8px; width: 340px; margin: 0 auto;">
        <svg width="320" height="460" viewBox="0 0 320 460" style="background: #151515; border: 2px solid #333;">
            <style>
                {animation_style}
            </style>
            
            <!-- Капилляр -->
            <rect x="135" y="0" width="50" height="60" fill="#555" />
            <rect x="140" y="0" width="40" height="60" fill="#151515" />

            <!-- Каплевидный контур -->
            <path d="{path_d}" class="{"drop-tear-stand" if is_running else ""}" fill="rgba(100,200,255,0.55)" stroke="lightskyblue" stroke-width="2" style="display: {"block" if is_running else "none"};" />

            <!-- Стакан -->
            <path d="M 90,370 L 90,440 L 230,440 L 230,370" fill="none" stroke="#fff" stroke-width="3" />
            <!-- Жидкость -->
            <rect x="93" y="{"390" if is_running else "438"}" width="134" height="{"48" if is_running else "2"}" fill="rgba(100, 200, 255, 0.35)" style="transition: all 2s;" />
        </svg>
    </div>
    """
    return html_code
