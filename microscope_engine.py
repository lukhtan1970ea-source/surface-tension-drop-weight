def generate_microscope_svg(sigma_true, rho_true, mic_x, mic_y):
    """Генерує фізично істинну перевернуту анімацію на основі інтегрування RK4"""
    svg_mic_x = 200 + (mic_x * 50)
    svg_mic_y = 200 - (mic_y * 50)
    
    # Капілярна постійна для JS (в px^-2). Масштаб: 1 мм = 50 пікселів.
    beta_px = ((rho_true * 9.81) / sigma_true) / 2500000000.0
    critical_neck = max(14.0, min(24.0, (sigma_true * 1000) * 0.35))
    
    ticks_html = ""
    for i in range(-200, 201, 10):
        t_len = 14 if i % 50 == 0 else 7
        ticks_html += f'<line x1="{svg_mic_x + i}" y1="{svg_mic_y - t_len}" x2="{svg_mic_x + i}" y2="{svg_mic_y + t_len}" stroke="red" stroke-width="1" />'

    html_code = f"""
    <div style="background: #111; padding: 10px; border-radius: 8px; width: 420px; margin: 0 auto;">
        <svg width="400" height="400" viewBox="0 0 400 400" style="background: #030703; border: 3px solid #333; border-radius: 50%;">
            <path d="M 165,400 L 170,400 L 170,320 L 155,320 L 155,400" fill="#444" />
            <path d="M 235,400 L 230,400 L 230,320 L 245,320 L 245,400" fill="#444" />
            <line x1="170" y1="320" x2="230" y2="320" stroke="#222" stroke-width="2" />

            <path id="mic-drop-path" d="" fill="rgba(100,200,255,0.55)" stroke="lightskyblue" stroke-width="2" />
            <circle id="mic-fly-sphere" cx="200" cy="-50" r="0" fill="rgba(100,200,255,0.6)" stroke="lightskyblue" stroke-width="1.5" style="display:none;" />

            <line x1="0" y1="{svg_mic_y}" x2="400" y2="{svg_mic_y}" stroke="rgba(255,0,0,0.8)" stroke-width="1.5" />
            <line x1="{svg_mic_x}" y1="0" x2="{svg_mic_x}" y2="400" stroke="rgba(255,0,0,0.8)" stroke-width="1.5" />
            {ticks_html}
        </svg>
    </div>

    <script>
        const dropPath = document.getElementById('mic-drop-path');
        const flySphere = document.getElementById('mic-fly-sphere');
        const beta = {beta_px}; 
        
        function solveYoungLaplaceRK4(b_param) {{
            let pointsLeft = []; let pointsRight = [];
            let s = 0.0; let x = 0.0001; let y = 0.0; let phi = 0.0;
            let ds = 0.35; let maxSteps = 350;
            
            pointsLeft.push({{x: 200 - x, y: y}});
            pointsRight.unshift({{x: 200 + x, y: y}});
            
            function derivatives(x_v, y_v, phi_v) {{
                let dx = Math.cos(phi_v); let dy = Math.sin(phi_v);
                let sin_x_term = (x_v < 0.05) ? (1.0 / b_param) : (Math.sin(phi_v) / x_v);
                let dphi = (2.0 / b_param) - (beta * y_v) - sin_x_term;
                return [dx, dy, dphi];
            }}
            
            for (let step = 0; step < maxSteps; step++) {{
                let [kx1, ky1, kphi1] = derivatives(x, y, phi);
                let [kx2, ky2, kphi2] = derivatives(x + 0.5*ds*kx1, y + 0.5*ds*ky1, phi + 0.5*ds*kphi1);
                let [kx3, ky3, kphi3] = derivatives(x + 0.5*ds*kx2, y + 0.5*ds*ky2, phi + 0.5*ds*kphi2);
                let [kx4, ky4, kphi4] = derivatives(x + ds*kx3, y + ds*ky3, phi + ds*kphi4);
                
                x += (ds / 6.0) * (kx1 + 2.0*kx2 + 2.0*kx3 + kx4);
                y += (ds / 6.0) * (ky1 + 2.0*ky2 + 2.0*ky3 + ky4);
                phi += (ds / 6.0) * (kphi1 + 2.0*kphi2 + 2.0*kphi3 + kphi4);
                
                if (x >= 30.0 || phi > Math.PI * 1.4 || y > 160) break;
                pointsLeft.push({{x: 200 - x, y: y}});
                pointsRight.unshift({{x: 200 + x, y: y}});
            }}
            return [pointsLeft, pointsRight, x, y];
        }}

        function animateMicroscope() {{
            let startTime = null; const duration = 4500; 
            function frame(timestamp) {{
                if (!startTime) startTime = timestamp;
                let elapsed = timestamp - startTime;
                let p = (elapsed % duration) / duration;
                
                if (p <= 0.85) {{
                    flySphere.style.display = 'none'; dropPath.style.display = 'block';
                    let b_param = 44.0 - ((p / 0.85) * 24.5); 
                    let [pLeft, pRight, finalX, finalY] = solveYoungLaplaceRK4(b_param);
                    
                    let pathString = `M 170,320`;
                    for (let pt of pLeft) pathString += ` L \${{pt.x.toFixed(1)}},\${{(320 - finalY + pt.y).toFixed(1)}}`;
                    for (let pt of pRight) pathString += ` L \${{pt.x.toFixed(1)}},\${{(320 - finalY + pt.y).toFixed(1)}}`;
                    pathString += ` Z`;
                    
                    dropPath.setAttribute('d', pathString);
                    window.lastFinalY = finalY;
                }} else if (p <= 0.93) {{
                    let rP = (p - 0.85) / 0.08;
                    dropPath.setAttribute('d', `M 170,320 A 30,\${{4 * (1 - rP)}} 0 0,1 230,320 Z`);
                    flySphere.style.display = 'block';
                    flySphere.setAttribute('cx', '200');
                    flySphere.setAttribute('cy', 320 - window.lastFinalY - (rP * 50));
                    flySphere.setAttribute('r', '{critical_neck * 1.1}');
                }} else {{
                    let fP = (p - 0.93) / 0.07;
                    flySphere.setAttribute('cy', 320 - window.lastFinalY - 50 - (fP * 250));
                }}
                requestAnimationFrame(frame);
            }}
            requestAnimationFrame(frame);
        }}
        animateMicroscope();
    </script>
    """
    return html_code
