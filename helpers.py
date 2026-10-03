def generate_stand_svg(target_drops, sigma_true, is_running, is_finished, tare_weight, total_drops_mass_g):
    """
    Автономний динамічний JS/SVG рушій лабораторного стенду з вагою та лічильником.
    Підтримує три стани приладу: наливання, фіксація фіналу та повне ручне скидання.
    """
    # Визначаємо фізичний радіус каплиці на стенді (в пікселях)
    base_drop_r = max(6.0, min(14.0, (sigma_true * 1000) * 0.18))
    
    html_code = f"""
    <div style="background: #161616; padding: 20px; border-radius: 16px; width: 330px; margin: 0 auto; box-shadow: 0 8px 32px rgba(0,0,0,0.6); border: 1px solid #333; text-align: center;">
        <svg id="stand-container" width="300" height="440" viewBox="0 0 400 440" style="background: #111311; border: 3px solid #444; border-radius: 8px;">
            <rect x="0" y="0" width="12" height="440" fill="#3a3a3a" />
            <rect x="0" y="240" width="150" height="10" fill="#2b2b2b" />
            <rect x="135" y="0" width="30" height="80" fill="#444" opacity="0.4" />
            <rect x="140" y="0" width="20" height="80" fill="#111311" />
            <line x1="140" y1="80" x2="160" y2="80" stroke="#777" stroke-width="2" />
            <path id="stand-drop" d="M 140,80 A 10,1 0 0,0 160,80 Z" fill="rgba(100, 200, 255, 0.45)" stroke="lightskyblue" stroke-width="1.5" />
            <circle id="stand-flying-ball" cx="150" cy="80" r="0" fill="rgba(100, 200, 255, 0.55)" stroke="lightskyblue" stroke-width="1" style="display: none;" />
            <rect id="fluid-level" x="97" y="380" width="106" height="0" fill="rgba(100, 200, 255, 0.35)" style="transition: all 0.1s;" />
            <path d="M 95,310 L 95,380 L 205,380 L 205,310" fill="none" stroke="#eee" stroke-width="2.5" opacity="0.9" />
            <rect x="60" y="380" width="180" height="12" fill="#444" rx="3" />
            <rect x="70" y="392" width="160" height="40" fill="#222" rx="4" stroke="#333" stroke-width="2" />
            <text id="scale-display" x="150" y="418" fill="#00ff66" font-family="monospace" font-size="22" font-weight="bold" text-anchor="middle">{tare_weight:.3f} г</text>
            <rect x="185" y="15" width="100" height="30" fill="rgba(0,0,0,0.6)" rx="5" stroke="#333" />
            <text id="drop-counter-display" x="235" y="36" fill="#1cf" font-family="sans-serif" font-size="14" font-weight="bold" text-anchor="middle">Крапель: 0</text>
        </svg>
    </div>
    
    <input type="hidden" id="param-target-drops" value="{target_drops}">
    <input type="hidden" id="param-is-running" value="{"true" if is_running else "false"}">
    <input type="hidden" id="param-is-finished" value="{"true" if is_finished else "false"}">
    <input type="hidden" id="param-base-radius" value="{base_drop_r}">
    <input type="hidden" id="param-tare-weight" value="{tare_weight}">
    <input type="hidden" id="param-total-mass" value="{total_drops_mass_g}">

    <script>
        if (window.standAnimInterval) {{ clearInterval(window.standAnimInterval); }}

        const standDrop = document.getElementById('stand-drop');
        const standBall = document.getElementById('stand-flying-ball');
        const scaleDisplay = document.getElementById('scale-display');
        const fluidLevel = document.getElementById('fluid-level');
        const dropCounterDisplay = document.getElementById('drop-counter-display');

        const targetDrops = parseInt(document.getElementById('param-target-drops').value) || 20;
        const isRunning = document.getElementById('param-is-running').value === "true";
        const isFinished = document.getElementById('param-is-finished').value === "true";
        const baseRadius = parseFloat(document.getElementById('param-base-radius').value) || 8.0;
        
        const tareWeight = parseFloat(document.getElementById('param-tare-weight').value) || 25.000;
        const totalTargetMass = parseFloat(document.getElementById('param-total-mass').value) || 0.0; 
        const massPerDrop = totalTargetMass / targetDrops;

        let currentDropCount = 0;
        let standElapsed = 0;
        const cycleTime = 1400; 
        const fpsMs = 20;

        if (isRunning) {{
            window.standAnimInterval = setInterval(() => {{
                if (!document.getElementById('stand-container')) {{
                    clearInterval(window.standAnimInterval);
                    return;
                }}

                standElapsed += fpsMs;
                let p = (standElapsed % cycleTime) / cycleTime;

                if (currentDropCount >= targetDrops) {{
                    standDrop.setAttribute('d', 'M 140,80 A 10,1 0 0,0 160,80 Z');
                    standBall.style.display = 'none';
                    scaleDisplay.textContent = (tareWeight + totalTargetMass).toFixed(3) + " г";
                    dropCounterDisplay.textContent = "Крапель: " + targetDrops;
                    let finalH = targetDrops * 1.2;
                    fluidLevel.setAttribute('height', finalH.toString());
                    fluidLevel.setAttribute('y', (380 - finalH).toString());
                    clearInterval(window.standAnimInterval);
                    return;
                }}

                if (p <= 0.70) {{
                    standBall.style.display = 'none';
                    let grow = p / 0.70;
                    let curH = grow * baseRadius * 1.4;
                    standDrop.setAttribute('d', `M 140,80 C 140,80 140,${{80+curH}} 150,${{80+curH}} C 160,${{80+curH}} 160,80 160,80 Z`);
                }} else if (p <= 0.92) {{
                    standDrop.setAttribute('d', 'M 140,80 A 10,1 0 0,0 160,80 Z'); 
                    standBall.style.display = 'block';
                    let fall = (p - 0.70) / 0.22;
                    let startY = 80 + baseRadius;
                    let curY = startY + (fall * (370 - startY)); 
                    standBall.setAttribute('cx', '150'); standBall.setAttribute('cy', curY.toFixed(1));
                    standBall.setAttribute('r', (baseRadius * 0.85).toFixed(1));
                }} else {{
                    if (p - 0.92 <= fpsMs / cycleTime) {{
                        currentDropCount++;
                        dropCounterDisplay.textContent = "Крапель: " + currentDropCount;
                        let currentMass = tareWeight + (currentDropCount * massPerDrop);
                        scaleDisplay.textContent = currentMass.toFixed(3) + " г";
                        let curHeight = currentDropCount * 1.2; 
                        fluidLevel.setAttribute('height', curHeight.toString());
                        fluidLevel.setAttribute('y', (380 - curHeight).toString());
                    }}
                    standBall.style.display = 'none';
                }}
            }}, fpsMs);
        }} else {{
            // ІСПРАВЛЕНО: Четкое разделение на финальное удержание макро-массы и полный сброс!
            if (isFinished) {{
                scaleDisplay.textContent = (tareWeight + totalTargetMass).toFixed(3) + " г";
                dropCounterDisplay.textContent = "Крапель: " + targetDrops;
                let finalH = targetDrops * 1.2;
                fluidLevel.setAttribute('height', finalH.toString());
                fluidLevel.setAttribute('y', (380 - finalH).toString());
            }} else {{
                // ПОЛНЫЙ СБРОС (Перезавантаження стенду) — весы сбрасываются строго на m0
                scaleDisplay.textContent = tareWeight.toFixed(3) + " г";
                dropCounterDisplay.textContent = "Крапель: 0";
                fluidLevel.setAttribute('height', '0');
                fluidLevel.setAttribute('y', '380');
            }}
            standDrop.setAttribute('d', 'M 140,80 A 10,1 0 0,0 160,80 Z');
            standBall.style.display = 'none';
        }}
    </script>
    """
    return html_code
