import numpy as np

def generate_microscope_svg(sigma_true, rho_true, mic_x, mic_y):
    """Генерує перевернуту анімацію на основі інтегрування рівняння Янга-Лапласа (RK4)"""
    svg_mic_x = 200 + (mic_x * 50)
    svg_mic_y = 200 - (mic_y * 50)
    
    # Капілярна постійна для JS (в px^-2). Масштаб: 1 мм = 50 пікселів.
    beta_px = ((rho_true * 9.81) / sigma_true) / 2500000000.0
    
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
        
        function solveYoungLaplace(b_param) {{
            let pointsLeft = []; let pointsRight = [];
            let s = 0.0; let x = 0.0001; let y = 0.0; let phi = 0.0;
            let ds = 0.4; let maxSteps = 400;
            
            pointsLeft.push({{x: 200 - x, y: y}});
            pointsRight.unshift({{x: 200 + x, y: y}});
            
            // ІСПРАВЛЕНО: Розкриття неопределенності при x -> 0 для запобігання NaN
            function derivatives(x_v, y_v, phi_v) {{
                let dx_ds = Math.cos(phi_v);
                let dy_ds = Math.sin(phi_v);
                
                let curvature_term = (x_v < 0.01) ? (1.0 / b_param) : (Math.sin(phi_v) / x_v);
                let dphi_ds = (2.0 / b_param) + (beta * y_v) - curvature_term;
                
                return [dx_ds, dy_ds, dphi_ds];
            }}
            
            for (let step = 0; step < maxSteps; step++) {{
                let [kx1, ky1, kphi1] = derivatives(x, y, phi);
                let [kx2, ky2, kphi2] = derivatives(x + 0.5*ds*kx1, y + 0.5*ds*ky1, phi + 0.5*ds*kphi1);
                let [kx3, ky3, kphi3] = derivatives(x + 0.5*ds*kx2, y + 0.5*ds*ky2, phi + 0.5*ds*kphi2);
                let [kx4, ky4, kphi4] = derivatives(x + ds*kx3, y + ds*ky3, phi + ds*kphi4);
                
                x += (ds / 6.0) * (kx1 + 2.0*kx2 + 2.0*kx3 + kx4);
                y += (ds / 6.0) * (ky1 + 2.0*ky2 + 2.0*ky3 + ky4);
                phi += (ds / 6.0) * (kphi1 + 2.0*kphi2 + 2.0*kphi3 + kphi4);
                
                if (x >= 30.0 || phi > Math.PI * 1.5 || y > 180) break;
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
                    // Фізичний параметр b плавно зменшується, збільшуючи об'єм та витягуючи краплю
                    let b_param = 38.0 - ((p / 0.85) * 19.5); 
                    let [pLeft, pRight, finalX, finalY] = solveYoungLaplace(b_param);
                    
                    let pathString = `M 170,320`;
                    for (let pt of pLeft) pathString += ` L ${pt.x.toFixed(1)},${(320 - finalY + pt.y).toFixed(1)}`;
                    for (let pt of pRight) pathString += ` L ${pt.x.toFixed(1)},${(320 - finalY + pt.y).toFixed(1)}`;
                    pathString += ` Z`;
                    
                    dropPath.setAttribute('d', pathString);
                    window.lastFinalY = finalY;
                }} else if (p <= 0.93) {{
                    let rP = (p - 0.85) / 0.08;
                    let hRest = 4 * (1 - rP);
                    dropPath.setAttribute('d', `M 170,320 A 30,${hRest} 0 0,1 230,320 Z`);
                    flySphere.style.display = 'block';
                    let curY = 320 - window.lastFinalY - (rP * 50);
                    flySphere.setAttribute('cx', '200');
                    flySphere.setAttribute('cy', curY);
                    flySphere.setAttribute('r', '16');
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


def generate_stand_svg(target_drops, sigma_true, is_running):
    critical_neck = max(8.0, min(18.0, (sigma_true * 1000) * 0.26))
    animation_style = ""
    if is_running:
        animation_style = f"""
        @keyframes standCycle {{
            0% {{ d: path('M 145,60 A 15,2 0 0,0 175,60 Z'); }}
            25% {{ d: path('M 145,60 A 15,12 0 0,0 175,60 Z'); }}
            50% {{ d: path('M 145,60 C 145,65 150,72 146,80 A 14,14 0 0,0 174,80 C 170,72 175,65 175,60 Z'); }}
            75% {{ d: path('M 145,60 C 145,65 {160 - critical_neck},72 {160 - critical_neck * 1.3},90 A {critical_neck * 1.3},{critical_neck * 1.3} 0 0,0 {160 + critical_neck * 1.3},90 C {160 + critical_neck},72 175,65 175,60 Z'); }}
            76% {{ d: path('M 145,60 A 15,1 0 0,0 175,60 Z'); }}
            100% {{ d: path('M 145,60 A 15,1 0 0,0 175,60 Z'); }}
        }}
        @keyframes flySphereCycle {{
            0% {{ transform: translateY(0px); opacity: 0; }}
            75% {{ transform: translateY(0px); opacity: 0; }}
            76% {{ transform: translateY(40px); opacity: 1; }}
            98% {{ transform: translateY(320px); opacity: 1; }}
            100% {{ transform: translateY(330px); opacity: 0; }}
        }}
        .stand-drop-tear {{ animation: standCycle 1.0s infinite linear; }}
        .stand-fly-sphere {{ animation: flySphereCycle 1.0s infinite linear; }}
        """

    html_code = f"""
    <div style="background: #111; padding: 10px; border-radius: 8px; width: 340px; margin: 0 auto;">
        <svg width="320" height="460" viewBox="0 0 320 460" style="background: #151515; border: 2px solid #333;">
            <style>{animation_style}</style>
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
