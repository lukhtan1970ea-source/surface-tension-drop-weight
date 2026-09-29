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
    # Масштаб: 1 мм = 50 пикселей. Центр окуляра — (200, 200)
    svg_mic_x = 200 + (mic_x * 50)
    svg_mic_y = 200 - (mic_y * 50)
    
    # Расчет радиуса шейки (от 15 до 30 пикселей)
    neck_radius = max(15.0, min(30.0, (sigma_true * 1000) * 0.4))
    
    html_code = f"""
    <div style="background-color: #111; padding: 15px; border-radius: 8px; width: 420px; margin: 0 auto; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
        <svg width="400" height="400" viewBox="0 0 400 400" style="background: #050a05; border: 3px solid #333; border-radius: 50%;">
            <!-- Перевернутый капилляр снизу (ось по центру X=200) -->
            <path d="M 160,400 L 170,400 L 170,300 L 155,300 L 155,400" fill="#555" />
            <path d="M 240,400 L 230,400 L 230,300 L 245,300 L 245,400" fill="#555" />
            <line x1="170" y1="300" x2="230" y2="300" stroke="#333" stroke-width="2" />

            <!-- Ростущая капля вверх -->
            <path id="mic-drop" d="" fill="rgba(135, 206, 250, 0.5)" stroke="lightskyblue" stroke-width="2" />

            <!-- Шкала микроскопа -->
            <line x1="0" y1="{svg_mic_y}" x2="400" y2="{svg_mic_y}" stroke="rgba(255, 0, 0, 0.7)" stroke-width="1.5" />
            <line x1="{svg_mic_x}" y1="0" x2="{svg_mic_x}" y2="400" stroke="rgba(255, 0, 0, 0.7)" stroke-width="1.5" />
            <g id="mic-ticks"></g>
        </svg>
    </div>

    <script>
        // Генерация рисок шкалы (шаг 0.2 мм = 10 пикселей)
        const ticksG = document.getElementById('mic-ticks');
        const mx = {svg_mic_x};
        const my = {svg_mic_y};
        for(let i = -200; i <= 200; i += 10) {{
            let tickLen = (i % 50 === 0) ? 14 : 7;
            let l = document.createElementNS("http://w3.org", "line");
            l.setAttribute("x1", mx + i); l.setAttribute("y1", my - tickLen);
            l.setAttribute("x2", mx + i); l.setAttribute("y2", my + tickLen);
            l.setAttribute("stroke", "red"); l.setAttribute("stroke-width", "1");
            ticksG.appendChild(l);
        }}

        const micDrop = document.getElementById('mic-drop');
        const neckR = {neck_radius};
        
        function runMicAnimation() {{
            let startTime = null;
            const cycleDuration = 4000; // Полноценные 4 секунды для неспешного замера
            
            function frame(timestamp) {{
                if (!startTime) startTime = timestamp;
                let elapsed = timestamp - startTime;
                let progress = (elapsed % cycleDuration) / cycleDuration;
                
                if (progress > 0.94) {{
                    // Капля оторвалась и улетела вверх
                    let flyP = (progress - 0.94) / 0.06;
                    let flyY = 220 - (flyP * 300);
                    let r = neckR * 1.2;
                    // Округлая форма оторвавшейся капли
                    micDrop.setAttribute('d', `M ${{200 - r}},${{flyY}} A ${{r}},${{r * 1.2}} 0 1,1 ${{200 + r}},${{flyY}} Z`);
                }} else {{
                    // Физически правильное раздувание капли строго по центру X=200
                    let dropHeight = progress * 90;
                    let topY = 300 - dropHeight;
                    let curNeck = 30 - (30 - neckR) * (progress * progress);
                    let bulbR = curNeck + (38 - curNeck) * Math.sin(progress * Math.PI);
                    
                    let d = `M 170,300 
                             Q ${{200 - curNeck}},${{300 - dropHeight * 0.3}} ${{200 - bulbR}},${{topY + dropHeight * 0.1}} 
                             A ${{bulbR}},${{bulbR * 1.1}} 0 0,1 ${{200 + bulbR}},${{topY + dropHeight * 0.1}} 
                             Q ${{200 + curNeck}},${{300 - dropHeight * 0.3}} 230,300 Z`;
                    micDrop.setAttribute('d', d);
                }}
                requestAnimationFrame(frame);
            }}
            requestAnimationFrame(frame);
        }}
        runMicAnimation();
    </script>
    """
    return html_code

def generate_stand_svg(target_drops, sigma_true, js_trigger):
    neck_radius_pixels = max(10.0, min(22.0, (sigma_true * 1000) * 0.3))
    
    html_code = f"""
    <div style="background-color: #111; padding: 15px; border-radius: 8px; width: 340px; margin: 0 auto; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
        <svg width="320" height="460" viewBox="0 0 320 460" style="background: #151515; border: 2px solid #333;">
            <!-- Капилляр сверху -->
            <path d="M 125,0 L 145,0 L 145,60 L 135,60 L 135,0" fill="#666" />
            <path d="M 195,0 L 175,0 L 175,60 L 185,60 L 185,0" fill="#666" />
            <line x1="145" y1="60" x2="175" y2="60" stroke="#444" stroke-width="2" />

            <!-- Капля на конце трубки -->
            <path id="stand-drop" d="" fill="rgba(135, 206, 250, 0.5)" stroke="lightskyblue" stroke-width="1.5" />
            <!-- Падающая капля -->
            <ellipse id="falling-drop" cx="160" cy="-50" rx="{neck_radius_pixels * 1.2}" ry="{neck_radius_pixels * 1.4}" fill="rgba(135, 206, 250, 0.6)" stroke="lightskyblue" stroke-width="1.5" style="display: none;" />

            <!-- Стакан -->
            <path d="M 90,360 L 90,440 L 230,440 L 230,360" fill="none" stroke="#fff" stroke-width="3" />
            <rect id="fluid-level" x="93" y="438" width="134" height="2" fill="rgba(135, 206, 250, 0.3)" />
        </svg>
    </div>

    <script>
        const standDrop = document.getElementById('stand-drop');
        const fallingDrop = document.getElementById('falling-drop');
        const fluidLevel = document.getElementById('fluid-level');
        
        const totalDrops = {target_drops};
        const neckR = {neck_radius_pixels};
        let count = 0;
        
        function animateStand() {{
            let startTime = null;
            const growTime = 700; 
            const fallTime = 250; 
            
            function frame(timestamp) {{
                if (!startTime) startTime = timestamp;
                let elapsed = timestamp - startTime;
                
                if (elapsed < growTime) {{
                    fallingDrop.style.display = 'none';
                    standDrop.style.display = 'block';
                    let p = elapsed / growTime;
                    
                    let dLen = p * 40;
                    let curY = 60 + dLen;
                    let curNeck = 15 - (15 - neckR) * (p * p);
                    let bulb = curNeck + (22 - curNeck) * Math.sin(p * Math.PI);
                    
                    let d = `M 145,60 
                             Q ${{160 - curNeck}},${{60 + dLen * 0.3}} ${{160 - bulb}},${{curY * 0.9}} 
                             A ${{bulb}},${{bulb * 1.1}} 0 0,0 ${{160 + bulb}},${{curY * 0.9}} 
                             Q ${{160 + curNeck}},${{60 + dLen * 0.3}} 175,60 Z`;
                    standDrop.setAttribute('d', d);
                    requestAnimationFrame(frame);
                }} else if (elapsed < growTime + fallTime) {{
                    standDrop.style.display = 'none';
                    fallingDrop.style.display = 'block';
                    
                    let pFall = (elapsed - growTime) / fallTime;
                    let yCurr = 100 + (300 * pFall * pFall); // Равноускоренное падение строго вниз (X=160)
                    fallingDrop.setAttribute('cy', yCurr);
                    requestAnimationFrame(frame);
                }} else {{
                    count++;
                    let h = count * (75 / totalDrops);
                    fluidLevel.setAttribute('y', 440 - h);
                    fluidLevel.setAttribute('height', h);
                    
                    if (count < totalDrops) {{
                        startTime = null;
                        requestAnimationFrame(frame);
                    }} else {{
                        fallingDrop.style.display = 'none';
                        standDrop.setAttribute('d', '');
                    }}
                }}
            }}
            requestAnimationFrame(frame);
        }}

        if ({js_trigger}) {{
            animateStand();
        }}
    </script>
    """
    return html_code
