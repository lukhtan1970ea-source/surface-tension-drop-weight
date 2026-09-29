import numpy as np

# Довідкові дані рідин при 20°C
LIQUIDS = {
    "Вода (H2O)": {"sigma_20": 72.75, "rho_20": 0.998, "temp_coeff": -0.165},
    "Етанол (C2H5OH)": {"sigma_20": 22.27, "rho_20": 0.789, "temp_coeff": -0.086},
    "Гліцерин (C3H8O3)": {"sigma_20": 63.40, "rho_20": 1.261, "temp_coeff": -0.060},
    "Ацетон ((CH3)2CO)": {"sigma_20": 23.46, "rho_20": 0.791, "temp_coeff": -0.112}
}

def get_physical_properties(liquid_name, temp_c):
    """Обчислює поверхневий натяг та щільність залежно від температури"""
    data = LIQUIDS[liquid_name]
    dt = temp_c - 20.0
    sigma = (data["sigma_20"] + data["temp_coeff"] * dt) / 1000.0  # Н/м
    rho = (data["rho_20"] * (1 - 0.001 * dt)) * 1000.0            # кг/м3
    return max(0.005, sigma), max(500.0, rho)

def generate_microscope_svg(sigma_true, mic_x, mic_y):
    """
    Генерує ПЕРЕВЕРНУТУ анімацію капіляра та капли під мікроскопом.
    Капіляр знизу, крапля росте ВГОРУ і відлітає ВГОРУ (в небуття).
    """
    # Масштаб для мікроскопа: 1 мм = 60 пікселів (великий план)
    svg_mic_x = 200 + (mic_x * 60)
    svg_mic_y = 300 - (mic_y * 60)  # Інверсія осі Y для мікроскопа
    
    # Діаметр шийки залежить від фізики рідини
    neck_radius = max(12.0, min(35.0, (sigma_true * 1000) * 0.45))
    
    html_code = f"""
    <div style="background-color: #111; padding: 15px; border-radius: 8px; width: 420px; margin: 0 auto; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
        <svg width="400" height="400" viewBox="0 0 400 400" style="background: #0a100a; border: 3px solid #333; border-radius: 50%;">
            <!-- Перевернутий капіляр (знаходиться знизу) -->
            <path d="M 140,400 L 170,400 L 170,320 L 155,320 L 155,400" fill="#666" />
            <path d="M 260,400 L 230,400 L 230,320 L 245,320 L 245,400" fill="#666" />
            <line x1="170" y1="320" x2="230" y2="320" stroke="#444" stroke-width="2" />

            <!-- Ростуча крапля (росте ВГОРУ) -->
            <path id="mic-drop" d="" fill="rgba(100, 200, 255, 0.4)" stroke="deepskyblue" stroke-width="2" />

            <!-- Шкала мікроскопа (Перехрестя) -->
            <line x1="0" y1="{svg_mic_y}" x2="400" y2="{svg_mic_y}" stroke="rgba(255, 0, 0, 0.7)" stroke-width="1.5" />
            <line x1="{svg_mic_x}" y1="0" x2="{svg_mic_x}" y2="400" stroke="rgba(255, 0, 0, 0.7)" stroke-width="1.5" />
            <g id="mic-ticks"></g>
        </svg>
    </div>

    <script>
        // Генерація вимірювальних рисок (крок 0.2 мм = 12 пікселів)
        const ticksG = document.getElementById('mic-ticks');
        const mx = {svg_mic_x};
        const my = {svg_mic_y};
        for(let i = -180; i <= 180; i += 12) {{
            let tickLen = (i % 60 === 0) ? 12 : 6;
            let l = document.createElementNS("http://w3.org", "line");
            l.setAttribute("x1", mx + i); l.setAttribute("y1", my - tickLen);
            l.setAttribute("x2", mx + i); l.setAttribute("y2", my + tickLen);
            l.setAttribute("stroke", "red"); l.setAttribute("stroke-width", "1");
            ticksG.appendChild(l);
        }}

        // Анімація безперервного повільного росту краплі вгору
        const micDrop = document.getElementById('mic-drop');
        const neckR = {neck_radius};
        
        function runMicAnimation() {{
            let startTime = null;
            const cycleDuration = 3500; // Повільний цикл (3.5 секунди), щоб встигнути виміряти
            
            function frame(timestamp) {{
                if (!startTime) startTime = timestamp;
                let elapsed = timestamp - startTime;
                let progress = (elapsed % cycleDuration) / cycleDuration;
                
                let curNeck = 30 - (30 - neckR) * (progress * progress);
                let dropHeight = progress * 80;
                
                if (progress > 0.95) {{
                    // Ефект відриву: крапля різко летить вгору (в небуття)
                    let flyProgress = (progress - 0.95) / 0.05;
                    let flyY = 320 - dropHeight - (flyProgress * 300);
                    // Малюємо краплю, що летить окремо
                    let d = `M ${{200-curNeck}},${{flyY}} A ${{curNeck*1.3}},${{curNeck*1.5}} 0 1,1 ${{200+curNeck}},${{flyY}} Z`;
                    micDrop.setAttribute('d', d);
                }} else {{
                    // Звичайний ріст кривої Безьє вгору від капіляра
                    let topY = 320 - dropHeight;
                    let bulbR = curNeck + (40 - curNeck) * Math.sin(progress * Math.PI);
                    
                    let d = `M 170,320 
                             Q 200-${{curNeck}},320-${{dropHeight*0.4}} 200-${{bulbR}},${{topY+dropHeight*0.1}} 
                             A ${{bulbR}},${{bulbR*1.1}} 0 0,1 200+${{bulbR}},${{topY+dropHeight*0.1}} 
                             Q 200+${{curNeck}},320-${{dropHeight*0.4}} 230,320 Z`;
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
    """Генерує звичайну (НЕ перевернуту) анімацію стенду зі склянкою та весами"""
    neck_radius_pixels = max(8.0, min(25.0, (sigma_true * 1000) * 0.35))
    
    html_code = f"""
    <div style="background-color: #111; padding: 15px; border-radius: 8px; width: 340px; margin: 0 auto; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
        <svg width="320" height="460" viewBox="0 0 320 460" style="background: #151515; border: 2px solid #333;">
            <!-- Нормальний капіляр зверху -->
            <path d="M 120,0 L 140,0 L 140,60 L 130,60 L 130,0" fill="#777" />
            <path d="M 200,0 L 180,0 L 180,60 L 190,60 L 190,0" fill="#777" />
            <line x1="140" y1="60" x2="180" y2="60" stroke="#555" stroke-width="2" />

            <!-- Анімаційні елементи -->
            <path id="stand-drop" d="" fill="rgba(100, 200, 255, 0.4)" stroke="deepskyblue" stroke-width="1.5" />
            <ellipse id="falling-drop" cx="160" cy="-40" rx="{neck_radius_pixels * 1.2}" ry="{neck_radius_pixels * 1.4}" fill="rgba(100, 200, 255, 0.5)" stroke="deepskyblue" stroke-width="1.5" style="display: none;" />

            <!-- Склянка -->
            <path d="M 90,360 L 90,440 L 230,440 L 230,360" fill="none" stroke="#fff" stroke-width="3" />
            <rect id="fluid-level" x="93" y="438" width="134" height="2" fill="rgba(100, 200, 255, 0.3)" />
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
            const growTime = 600; 
            const fallTime = 200; 
            
            function frame(timestamp) {{
                if (!startTime) startTime = timestamp;
                let elapsed = timestamp - startTime;
                
                if (elapsed < growTime) {{
                    fallingDrop.style.display = 'none';
                    standDrop.style.display = 'block';
                    let p = elapsed / growTime;
                    
                    let curNeck = 20 - (20 - neckR) * (p * p);
                    let dLen = p * 45;
                    let curY = 60 + dLen;
                    let bulb = curNeck + (25 - curNeck) * Math.sin(p * Math.PI);
                    
                    let d = `M 140,60 
                             Q 160-${{curNeck}},60+${{dLen*0.4}} 160-${{bulb}},${{curY*0.9}} 
                             A ${{bulb}},${{bulb*1.1}} 0 0,0 160+${{bulb}},${{curY*0.9}} 
                             Q 160+${{curNeck}},60+${{dLen*0.4}} 180,60 Z`;
                    standDrop.setAttribute('d', d);
                    requestAnimationFrame(frame);
                }} else if (elapsed < growTime + fallTime) {{
                    standDrop.style.display = 'none';
                    fallingDrop.style.display = 'block';
                    
                    let pFall = (elapsed - growTime) / growTime;
                    let yCurr = 105 + (330 * pFall * pFall);
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
