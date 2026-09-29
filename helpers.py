import numpy as np

# Справочные данные жидкостей при 20°C
LIQUIDS = {
    "Вода (H2O)": {"sigma_20": 72.75, "rho_20": 0.998, "temp_coeff": -0.165},
    "Этанол (C2H5OH)": {"sigma_20": 22.27, "rho_20": 0.789, "temp_coeff": -0.086},
    "Глицерин (C3H8O3)": {"sigma_20": 63.40, "rho_20": 1.261, "temp_coeff": -0.060},
    "Ацетон ((CH3)2CO)": {"sigma_20": 23.46, "rho_20": 0.791, "temp_coeff": -0.112}
}

def get_physical_properties(liquid_name, temp_c):
    """Вычисляет sigma и rho с учетом температурной зависимости"""
    data = LIQUIDS[liquid_name]
    dt = temp_c - 20.0
    sigma = (data["sigma_20"] + data["temp_coeff"] * dt) / 1000.0
    rho = (data["rho_20"] * (1 - 0.001 * dt)) * 1000.0
    return max(0.005, sigma), max(500.0, rho)

def generate_svg_animation(target_drops, sigma_true, mic_x, mic_y, js_trigger):
    """Генерирует HTML5 + SVG + JS код для плавной отрисовки капель на клиенте"""
    # Масштабирование визира: 1 мм = 40 пикселей
    svg_mic_x = 200 + (mic_x * 40)
    svg_mic_y = 100 - (mic_y * 40)
    
    # Расчет критического радиуса шейки капли для визуализации
    neck_radius_pixels = max(8.0, min(30.0, (sigma_true * 1000) * 0.35))
    
    html_code = f"""
    <div style="background-color: #111; padding: 15px; border-radius: 8px; width: 420px; margin: 0 auto; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
        <svg width="400" height="500" viewBox="0 0 400 500" style="background: #151515; border: 2px solid #333;">
            <!-- Капилляр -->
            <path d="M 150,0 L 175,0 L 175,80 L 160,80 L 160,0" fill="#777" />
            <path d="M 250,0 L 225,0 L 225,80 L 240,80 L 240,0" fill="#777" />
            <line x1="175" y1="80" x2="225" y2="80" stroke="#555" stroke-width="2" />

            <!-- Анимированные капли -->
            <path id="drop" d="" fill="rgba(173, 216, 230, 0.5)" stroke="lightblue" stroke-width="2" />
            <ellipse id="falling-drop" cx="200" cy="-50" rx="{neck_radius_pixels * 1.3}" ry="{neck_radius_pixels * 1.5}" fill="rgba(173, 216, 230, 0.6)" stroke="lightblue" stroke-width="2" style="display: none;" />

            <!-- Стакан для сбора капель -->
            <path d="M 120,400 L 120,480 L 280,480 L 280,400" fill="none" stroke="#fff" stroke-width="4" />
            <rect id="fluid-level" x="123" y="478" width="154" height="2" fill="rgba(173, 216, 230, 0.4)" />

            <!-- Перекрестие микроскопа -->
            <line x1="0" y1="{svg_mic_y}" x2="400" y2="{svg_mic_y}" stroke="rgba(255, 0, 0, 0.6)" stroke-width="1.5" stroke-dasharray="4,4" />
            <line x1="{svg_mic_x}" y1="0" x2="{svg_mic_x}" y2="500" stroke="rgba(255, 0, 0, 0.6)" stroke-width="1.5" stroke-dasharray="4,4" />
            
            <g id="ticks"></g>
        </svg>
    </div>

    <script>
        const ticksG = document.getElementById('ticks');
        const mx = {svg_mic_x};
        const my = {svg_mic_y};
        for(let i = -160; i <= 160; i += 16) {{
            let tickLen = (i % 64 === 0) ? 10 : 5;
            let l1 = document.createElementNS("http://w3.org", "line");
            l1.setAttribute("x1", mx + i); l1.setAttribute("y1", my - tickLen);
            l1.setAttribute("x2", mx + i); l1.setAttribute("y2", my + tickLen);
            l1.setAttribute("stroke", "red"); l1.setAttribute("stroke-width", "1");
            ticksG.appendChild(l1);
        }}

        const drop = document.getElementById('drop');
        const fallingDrop = document.getElementById('falling-drop');
        const fluidLevel = document.getElementById('fluid-level');
        
        const totalDropsTarget = {target_drops};
        const neckR = {neck_radius_pixels};
        let currentDrops = 0;
        
        function animate() {{
            let startTime = null;
            const growthDuration = 1000; 
            const fallDuration = 250;    
            
            function frame(timestamp) {{
                if (!startTime) startTime = timestamp;
                let elapsed = timestamp - startTime;
                
                if (elapsed < growthDuration) {{
                    fallingDrop.style.display = 'none';
                    drop.style.display = 'block';
                    let progress = elapsed / growthDuration;
                    
                    let currentNeck = 25 - (25 - neckR) * (progress * progress);
                    let dropLen = progress * 65;
                    let curY = 80 + dropLen;
                    let bulbR = currentNeck + (35 - currentNeck) * Math.sin(progress * Math.PI);
                    
                    let d = `M 175,80 
                             Q 200-${{currentNeck}},80+${{dropLen*0.4}} 200-${{bulbR}},${{curY*0.9}} 
                             A ${{bulbR}},${{bulbR*1.1}} 0 0,0 200+${{bulbR}},${{curY*0.9}} 
                             Q 200+${{currentNeck}},80+${{dropLen*0.4}} 225,80 Z`;
                    drop.setAttribute('d', d);
                    
                    requestAnimationFrame(frame);
                }} else if (elapsed < growthDuration + fallDuration) {{
                    drop.style.display = 'none';
                    fallingDrop.style.display = 'block';
                    
                    let fallElapsed = elapsed - growthDuration;
                    let fallProgress = fallElapsed / fallDuration;
                    
                    let yStart = 80 + 65;
                    let yEnd = 470;
                    let currentY = yStart + (yEnd - yStart) * (fallProgress * fallProgress);
                    
                    fallingDrop.setAttribute('cy', currentY);
                    requestAnimationFrame(frame);
                }} else {{
                    currentDrops++;
                    let newHeight = currentDrops * (75 / totalDropsTarget);
                    fluidLevel.setAttribute('y', 480 - newHeight);
                    fluidLevel.setAttribute('height', newHeight);
                    
                    if (currentDrops < totalDropsTarget) {{
                        startTime = null;
                        requestAnimationFrame(frame);
                    }} else {{
                        fallingDrop.style.display = 'none';
                        drop.style.display = 'block';
                        drop.setAttribute('d', 'M 175,80 Q 200,80 200,80 A 0,0 0 0,0 200,80 Q 200,80 225,80 Z');
                    }}
                }}
            }}
            requestAnimationFrame(frame);
        }}

        if ({js_trigger}) {{
            animate();
        }}
    </script>
    """
    return html_code

