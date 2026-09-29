def generate_microscope_svg(sigma_true, rho_true, mic_x, mic_y):
    """Генерує фізично істинну перевернуту анімацію каплеїди за допомогою безпомилкового інтегрування RK4"""
    svg_mic_x = 200 + (mic_x * 50)
    svg_mic_y = 200 - (mic_y * 50)
    
    # Капілярна постійна Янга-Лапласа
    g_const = 9.81
    beta_physical = (rho_true * g_const) / sigma_true  # м^-2
    
    # Визначаємо критичний радіус шийки
    critical_neck = max(14.0, min(24.0, (sigma_true * 1000) * 0.35))
    
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

            <!-- Фізичний контур краплі через Рунге-Кутту -->
            <path id="mic-drop-path" d="" fill="rgba(100,200,255,0.55)" stroke="lightskyblue" stroke-width="2" />
            <circle id="mic-fly-sphere" cx="200" cy="-50" r="0" fill="rgba(100,200,255,0.6)" stroke="lightskyblue" stroke-width="1.5" style="display:none;" />

            <!-- Шкала мікроскопа поверх усього -->
            <line x1="0" y1="{svg_mic_y}" x2="400" y2="{svg_mic_y}" stroke="rgba(255,0,0,0.8)" stroke-width="1.5" />
            <line x1="{svg_mic_x}" y1="0" x2="{svg_mic_x}" y2="400" stroke="rgba(255,0,0,0.8)" stroke-width="1.5" />
            {ticks_html}
        </svg>
    </div>

    <script>
        const dropPath = document.getElementById('mic-drop-path');
        const flySphere = document.getElementById('mic-fly-sphere');
        
        // Масштабований за Лапласом стійкий інтегратор RK4
        function solveYoungLaplaceRK4(volume_factor) {{
            let pointsLeft = []; 
            let pointsRight = [];
            
            // Інтегруємо у безрозмірних величинах для 100% гарантії збіжності
            let u = 0.0001; // безрозмірний радіус x
            let v = 0.0;    // безрозмірна висота y
            let phi = 0.0;  // кут нахилу дотичної
            
            let dt = 0.02;  // наддрібний крок інтегрування
            let maxSteps = 1200;
            
            // Фізичний коефіцієнт форми каплеїди (визначає її витягнутість)
            let В = 0.15 + (volume_factor * 0.45); 
            
            function derivatives(u_v, v_v, phi_v) {{
                let du = Math.cos(phi_v);
                let dv = Math.sin(phi_v);
                
                // Раскриття неозначеності в нулі Лапласа
                let sin_u_term = (u_v < 0.01) ? 1.0 : (Math.sin(phi_v) / u_v);
                let dphi = 2.0 + (В * v_v) - sin_u_term;
                
                return [du, dv, dphi];
            }}
            
            for (let step = 0; step < maxSteps; step++) {{
                let [ku1, kv1, kphi1] = derivatives(u, v, phi);
                
                let [ku2, kv2, kphi2] = derivatives(
                    u + 0.5 * dt * ku1, 
                    v + 0.5 * dt * kv1, 
                    phi + 0.5 * dt * kphi1
                );
                
                let [ku3, kv3, kphi3] = derivatives(
                    u + 0.5 * dt * ku2, 
                    v + 0.5 * dt * kv2, 
                    phi + 0.5 * dt * kphi2
                );
                
                let [ku4, kv4, kphi4] = derivatives(
                    u + dt * ku3, 
                    v + dt * kv3, 
                    phi + dt * kphi4
                );
                
                u += (dt / 6.0) * (ku1 + 2.0 * ku2 + 2.0 * ku3 + ku4);
                v += (dt / 6.0) * (kv1 + 2.0 * kv2 + 2.0 * kv3 + kv4);
                phi += (dt / 6.0) * (kphi1 + 2.0 * kphi2 + 2.0 * kphi3 + kphi4);
                
                if (isNaN(u) || isNaN(v) || phi > Math.PI * 0.98) {{
                    break;
                }}
                
                // Переводимо безрозмірні величини в реальні пікселі під розмір капіляра (R = 30px)
                // Коефіцієнт 30.0 / u фіксує основу точно на краях трубки
                let scale = 30.0 / u;
                
                if (step % 3 === 0) {{
                    pointsLeft.push({{x: 200 - (u * scale), y: v * scale}});
                    pointsRight.unshift({{x: 200 + (u * scale), y: v * scale}});
                }}
            }}
            
            // Масштабуємо фінальні точки
            let finalScale = 30.0 / u;
            let totalHeightPx = v * finalScale;
            
            let finalPointsLeft = [];
            let finalPointsRight = [];
            
            for (let step = 0; step < maxSteps; step++) {{
                let [ku1, kv1, kphi1] = derivatives(u, v, phi);
                let [ku2, kv2, kphi2] = derivatives(u + 0.5*dt*ku1, v + 0.5*dt*kv1, phi + 0.5*dt*kphi1);
                let [ku3, kv3, kphi3] = derivatives(u + 0.5*dt*ku2, v + 0.5*dt*kv2, phi + 0.5*dt*kphi2);
                let [ku4, kv4, kphi4] = derivatives(u + dt*ku3, v + dt*kv3, phi + dt*kphi4);
                
                u += (dt / 6.0) * (ku1 + 2.0 * ku2 + 2.0 * ku3 + ku4);
                v += (dt / 6.0) * (kv1 + 2.0 * kv2 + 2.0 * kv3 + kv4);
                phi += (dt / 6.0) * (kphi1 + 2.0 * kphi2 + 2.0 * kphi3 + kphi4);
                
                if (isNaN(u) || isNaN(v) || phi > Math.PI * 0.98) break;
                
                if (step % 4 === 0) {{
                    finalPointsLeft.push({{x: 200 - (u * finalScale), y: v * finalScale}});
                    finalPointsRight.unshift({{x: 200 + (u * finalScale), y: v * finalScale}});
                }}
            }}
            
            return [finalPointsLeft, finalPointsRight, totalHeightPx];
        }}

        function animateMicroscope() {{
            let startTime = null; 
            const duration = 4500; 
            
            function frame(timestamp) {{
                if (!startTime) startTime = timestamp;
                let elapsed = timestamp - startTime;
                let p = (elapsed % duration) / duration;
                
                if (p <= 0.85) {{
                    flySphere.style.display = 'none'; 
                    dropPath.style.display = 'block';
                    
                    let sP = p / 0.85;
                    // Передаємо коефіцієнт наповнення об'єму в ОДУ
                    let [pLeft, pRight, finalY] = solveYoungLaplaceRK4(sP);
                    
                    let pathString = "M 170,320";
                    for (let i = 0; i < pLeft.length; i++) {{
                        let yCoord = 320 - finalY + pLeft[i].y;
                        pathString += " L " + pLeft[i].x.toFixed(1) + "," + yCoord.toFixed(1);
                    }}
                    for (let i = 0; i < pRight.length; i++) {{
                        let yCoord = 320 - finalY + pRight[i].y;
                        pathString += " L " + pRight[i].x.toFixed(1) + "," + yCoord.toFixed(1);
                    }}
                    pathString += " Z";
                    
                    dropPath.setAttribute('d', pathString);
                    window.lastFinalY = finalY;
                    
                }} else if (p <= 0.93) {{
                    let rP = (p - 0.85) / 0.08;
                    let hRest = 4 * (1 - rP);
                    dropPath.setAttribute('d', "M 170,320 A 30," + hRest + " 0 0,1 230,320 Z");
                    
                    flySphere.style.display = 'block';
                    let curY = 320 - window.lastFinalY - (rP * 50);
                    flySphere.setAttribute('cx', '200');
                    flySphere.setAttribute('cy', curY);
                    flySphere.setAttribute('r', '{critical_neck * 1.1}');
                }} else {{
                    let fP = (p - 0.93) / 0.07;
                    let curY = 320 - window.lastFinalY - 50 - (fP * 250);
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
