import numpy as np

# Довідкові дані рідин при 20°C
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
    # Масштаб мікроскопа: 1 мм = 50 пікселів.
    svg_mic_x = 200 + (mic_x * 50)
    svg_mic_y = 200 - (mic_y * 50)
    
    # Граничний радіус шийки при відриві
    critical_neck = max(12.0, min(26.0, (sigma_true * 1000) * 0.36))
    
    # Генерація вимірювальних рисок шкали мікроскопа
    ticks_html = ""
    for i in range(-200, 201, 10):
        t_len = 14 if i % 50 == 0 else 7
        ticks_html += f'<line x1="{svg_mic_x + i}" y1="{svg_mic_y - t_len}" x2="{svg_mic_x + i}" y2="{svg_mic_y + t_len}" stroke="red" stroke-width="1" />'

    html_code = f"""
    <div style="background: #111; padding: 10px; border-radius: 8px; width: 420px; margin: 0 auto;">
        <svg width="400" height="400" viewBox="0 0 400 400" style="background: #030703; border: 3px solid #333; border-radius: 50%;">
            <!-- Перевернутий капіляр знизу -->
            <path d="M 165,400 L 170,400 L 170,320 L 155,320 L 155,400" fill="#444" />
            <path d="M 235,400 L 230,400 L 230,320 L 245,320 L 245,400" fill="#444" />
            <line x1="170" y1="320" x2="230" y2="320" stroke="#222" stroke-width="2" />

            <!-- Тіло краплі -->
            <path id="mic-drop-path" d="" fill="rgba(100,200,255,0.55)" stroke="lightskyblue" stroke-width="2" />
            <!-- Летяча сфера -->
            <circle id="mic-fly-sphere" cx="200" cy="-50" r="0" fill="rgba(100,200,255,0.6)" stroke="lightskyblue" stroke-width="1.5" style="display:none;" />

            <!-- Шкала мікроскопа поверх капли -->
            <line x1="0" y1="{svg_mic_y}" x2="400" y2="{svg_mic_y}" stroke="rgba(255,0,0,0.8)" stroke-width="1.5" />
            <line x1="{svg_mic_x}" y1="0" x2="{svg_mic_x}" y2="400" stroke="rgba(255,0,0,0.8)" stroke-width="1.5" />
            {ticks_html}
        </svg>
    </div>

    <script>
        const dropPath = document.getElementById('mic-drop-path');
        const flySphere = document.getElementById('mic-fly-sphere');
        const critNeck = {critical_neck};
        
        function animateMicroscope() {{
            let startTime = null;
            const duration = 4500; 
            
            function frame(timestamp) {{
                if (!startTime) startTime = timestamp;
                let elapsed = timestamp - startTime;
                let p = (elapsed % duration) / duration;
                
                if (p <= 0.3) {{
                    // ФАЗА 1: Сегмент сфери (меніск). Краї чітко на 170 і 230
                    flySphere.style.display = 'none';
                    dropPath.style.display = 'block';
                    let rStage = p / 0.3; 
                    let h = rStage * 18; 
                    let d = `M 170,320 A 30,${{h}} 0 0,1 230,320 Z`;
                    dropPath.setAttribute('d', d);
                    
                }} else if (p <= 0.88) {{
                    // ФАЗА 2: Вытягивание в мешочек с формированием шейки (Чистый симметричный сплайн)
                    let sP = (p - 0.3) / 0.58; 
                    let totalH = 18 + (sP * 72); 
                    let topY = 320 - totalH;
                    
                    let curNeck = 30 - (30 - critNeck) * (sP * sP);
                    let bulbR = curNeck + (36 - curNeck) * Math.sin(sP * Math.PI);
                    
                    let xLeftB = 200 - bulbR;
                    let xRightB = 200 + bulbR;
                    let xLeftN = 200 - curNeck;
                    let xRightN = 200 + curNeck;
                    
                    // Высота контрольных точек для управления "пухлостью" мешочка
                    let yCtrlLower = 310;
                    let yCtrlUpper = topY + (totalH * 0.2);
                    
                    // ВСЕГО ДВЕ КРИВЫЕ: одна вверх, одна вниз. Полная симметрия и плавность без изломов
                    let d = `M 170,320 
                             C 170,${{yCtrlLower}} ${{xLeftB}},${{yCtrlUpper}} 200,${{topY}} 
                             C ${{xRightB}},${{yCtrlUpper}} 230,${{yCtrlLower}} 230,320 Z`;
                    dropPath.setAttribute('d', d);


                    
                }} else if (p <= 0.94) {{
                    // ФАЗА 3: Відрив та релаксація в сферу
                    let rP = (p - 0.88) / 0.06; 
                    let hRest = 4 * (1 - rP);
                    let dRest = `M 170,320 A 30,${{hRest}} 0 0,1 230,320 Z`;
                    dropPath.setAttribute('d', dRest);
                    
                    dropPath.style.display = 'block';
                    flySphere.style.display = 'block';
                    
                    let sphereR = critNeck * 1.15;
                    let startY = 320 - 90;
                    let curY = startY - (rP * 40); 
                    
                    flySphere.setAttribute('cx', '200');
                    flySphere.setAttribute('cy', curY);
                    flySphere.setAttribute('r', sphereR);
                    
                }} else {{
                    // ФАЗА 4: Політ сфери в небуття
                    let fP = (p - 0.94) / 0.06; 
                    let startY = 320 - 90 - 40;
                    let curY = startY - (fP * 260); 
                    
                    flySphere.setAttribute('cy', curY);
                }}
                requestAnimationFrame(frame);
            }}
            requestAnimationFrame(frame);
        }}
        animateMicroscope();
    </script>
    """
    return html_code

def generate_stand_svg(target_drops, sigma_true, is_running):
    critical_neck = max(8.0, min(18.0, (sigma_true * 1000) * 0.26))
    animation_style = ""
    if is_running:
        animation_style = f"""
        @keyframes standCycle {{
            0% {{ d: path('M 145,60 A 15,2 0 0,0 175,60 Z'); opacity: 1; }}
            25% {{ d: path('M 145,60 A 15,12 0 0,0 175,60 Z'); opacity: 1; }}
            50% {{ d: path('M 145,60 C 145,65 150,75 146,85 A 14,15 0 0,0 174,85 C 170,75 175,65 175,60 Z'); opacity: 1; }}
            75% {{ d: path('M 145,60 C 145,65 {160 - critical_neck},75 {160 - critical_neck * 1.3},100 A {critical_neck * 1.3},{critical_neck * 1.4} 0 0,0 {160 + critical_neck * 1.3},100 C {160 + critical_neck},75 175,65 175,60 Z'); opacity: 1; }}
            76% {{ d: path('M 145,60 A 15,1 0 0,0 175,60 Z'); opacity: 1; }}
            100% {{ d: path('M 145,60 A 15,1 0 0,0 175,60 Z'); opacity: 1; }}
        }}
        @keyframes flySphereCycle {{
            0% {{ transform: translateY(0px); opacity: 0; }}
            75% {{ transform: translateY(0px); opacity: 0; }}
            76% {{ transform: translateY(50px); opacity: 1; }}
            98% {{ transform: translateY(320px); opacity: 1; }}
            100% {{ transform: translateY(330px); opacity: 0; }}
        }}
        .stand-drop-tear {{ animation: standCycle 1.0s infinite linear; }}
        .stand-fly-sphere {{ animation: flySphereCycle 1.0s infinite linear; }}
        """

    html_code = f"""
    <div style="background: #111; padding: 10px; border-radius: 8px; width: 340px; margin: 0 auto;">
        <svg width="320" height="460" viewBox="0 0 320 460" style="background: #151515; border: 2px solid #333;">
            <style>
                {animation_style}
            </style>
            <rect x="140" y="0" width="40" height="60" fill="#555" />
            <rect x="145" y="0" width="30" height="60" fill="#151515" />
            <path d="M 145,60 A 15,2 0 0,0 175,60 Z" class="{"stand-drop-tear" if is_running else ""}" fill="rgba(100,200,255,0.55)" stroke="lightskyblue" stroke-width="1.5" />
            <circle cx="160" cy="65" r="{critical_neck * 1.2}" class="{"stand-fly-sphere" if is_running else ""}" fill="rgba(100,200,255,0.6)" stroke="lightskyblue" stroke-width="1" style="display: {"block" if is_running else "none"};" />
            <path d="M 90,370 L 90,440 L 230,440 L 230,370" fill="none" stroke="#fff" stroke-width="3" />
            <rect x="93" y="{"395" if is_running else "438"}" width="134" height="{"43" if is_running else "2"}" fill="rgba(100, 200, 255, 0.35)" style="transition: all 2s;" />
        </svg>
    </div>
    """
    return html_code
