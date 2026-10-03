def generate_microscope_svg(sigma_true, rho_true, mic_x=0.0, mic_y=0.0):
    """
    Високоточний JS/SVG рушій каплеїди з прямим підключенням до слайдерів Streamlit.
    """
    # Перерахунок міліметрів у масштабні пікселі (1 мм = 40 пікселів)
    svg_mic_x = 200 + (mic_x * 40)
    svg_mic_y = 200 - (mic_y * 40)

    # Генеруємо трьохступеневу ГОСТ-шкалу з кроком 4 пікселі (0.1 мм)
    ticks_html = ""
    for i in range(-160, 181, 4):
        tick_index = i / 4
        t_len = 5
        stroke_w = 0.7
        if tick_index % 10 === 0:
            t_len = 14
            stroke_w = 1.3
        elif tick_index % 5 === 0:
            t_len = 9
            stroke_w = 1.0
        ticks_html += f'<line x1="{svg_mic_x + i}" y1="{svg_mic_y - t_len}" x2="{svg_mic_x + i}" y2="{svg_mic_y + t_len}" stroke="rgba(255,0,0,0.85)" stroke-width="{stroke_w}" />'

    svg_html = f"""
    <div style="background: #161616; padding: 20px; border-radius: 16px; width: 420px; margin: 0 auto; box-shadow: 0 8px 32px rgba(0,0,0,0.6); border: 1px solid #333; text-align: center;">
        <svg id="drop-container" width="400" height="400" viewBox="0 0 400 400" style="background: #010401; border: 4px solid #555; border-radius: 50%;">
            <!-- Скляний капіляр знизу -->
            <rect x="162" y="340" width="76" height="60" fill="#333" opacity="0.85" />
            <rect x="165" y="340" width="70" height="60" fill="#010401" />
            <line x1="165" y1="340" x2="235" y2="340" stroke="#666" stroke-width="3" />

            <!-- Контур краплі -->
            <path id="fluid-drop" d="" fill="rgba(100, 210, 255, 0.43)" stroke="lightskyblue" stroke-width="2.3" stroke-linejoin="round" />
            <circle id="flying-ball" cx="200" cy="500" r="0" fill="rgba(100, 210, 255, 0.55)" stroke="lightskyblue" stroke-width="2" style="display: none;" />

            <!-- РУХОМА ВИМІРЮВАЛЬНА ШКАЛА (Зв'язана з Python) -->
            <g id="microscope-grid">
                <line x1="0" y1="{svg_mic_y}" x2="400" y2="{svg_mic_y}" stroke="rgba(255,0,0,0.85)" stroke-width="1.5" />
                <line x1="{svg_mic_x}" y1="0" x2="{svg_mic_x}" y2="400" stroke="rgba(255,0,0,0.85)" stroke-width="1.5" />
                {ticks_html}
            </g>
        </svg>
    </div>

    <script>
        if (window.dropAnimInterval) {{ clearInterval(window.dropAnimInterval); }}
        
        const pathDrop = document.getElementById('fluid-drop');
        const ballFly = document.getElementById('flying-ball');

        function generatePearContour(progress) {{
            let points = []; let steps = 140; 
            let totalH = 2.0 + (progress * 115.0); 
            let baseR = 35;                      
            let maxBulbR = baseR + (progress * 18); 
            let neckR = baseR - (Math.pow(progress, 2.0) * 3.5); 

            for (let i = 0; i <= steps; i++) {{
                let t = i / steps; let y = 340 - (t * totalH); let r = baseR;
                if (t < 0.35) {{
                    let k = t / 0.35; let smooth = 0.5 - 0.5 * Math.cos(k * Math.PI);
                    r = baseR - (baseR - neckR) * smooth;
                }} else if (t < 0.75) {{
                    let k = (t - 0.35) / 0.40; let smooth = Math.sin(k * Math.PI / 2);
                    r = neckR + (maxBulbR - neckR) * smooth;
                }} else {{
                    let k = (t - 0.75) / 0.25; r = maxBulbR * Math.sqrt(Math.max(0.0, 1.0 - k * k));
                }}
                points.push({{x: 200 - r, y: y}});
            }}
            let dPath = `M 165,340`;
            for (let pt of points) dPath += ` L ` + pt.x.toFixed(1) + `,` + pt.y.toFixed(1);
            for (let i = points.length - 1; i >= 0; i--) {{
                dPath += ` L ` + (200 + (200 - points[i].x)).toFixed(1) + `,` + points[i].y.toFixed(1);
            }}
            dPath += ` Z`;
            return {{d: dPath, h: totalH, r: maxBulbR}};
        }}

        const loopDuration = 4800; 
        let currentElapsed = 0;
        const frameRateMs = 20;

        window.dropAnimInterval = setInterval(() => {{
            if (!document.getElementById('drop-container')) {{
                clearInterval(window.dropAnimInterval);
                return;
            }}

            currentElapsed += frameRateMs;
            let p = (currentElapsed % loopDuration) / loopDuration;

            if (p <= 0.82) {{
                ballFly.style.display = 'none'; pathDrop.style.display = 'block';
                let progress = p / 0.82; let contour = generatePearContour(progress);
                pathDrop.setAttribute('d', contour.d);
                window.lastH = contour.h; window.lastR = contour.r;
            } else if (p <= 0.88) {{
                let snapProgress = (p - 0.82) / 0.06;
                let stretchH = window.lastH + (snapProgress * 18);
                let snapNeckR = (35 - (0.82 * 3.5)) * (1.0 - snapProgress) + 2.5 * snapProgress;
                let points = [];
                for (let i = 0; i <= 140; i++) {{
                    let t = i / 140; let y = 340 - (t * stretchH); let r = 35;
                    if (t < 0.45) {{
                        let k = t / 0.45; let smooth = 0.5 - 0.5 * Math.cos(k * Math.PI);
                        r = 35 - (35 - snapNeckR) * smooth;
                    }} else if (t < 0.75) {{
                        let k = (t - 0.45) / 0.30; r = snapNeckR + (window.lastR * 1.02 - snapNeckR) * Math.sin(k * Math.PI / 2);
                    }} else {{
                        let k = (t - 0.75) / 0.25; r = window.lastR * 1.02 * Math.sqrt(Math.max(0.0, 1.0 - k * k));
                    }}
                    points.push({{x: 200 - r, y: y}});
                }}
                let dPath = `M 165,340`;
                for (let pt of points) dPath += ` L ` + pt.x.toFixed(1) + `,` + pt.y.toFixed(1);
                for (let i = points.length - 1; i >= 0; i--) {{
                    dPath += ` L ` + (200 + (200 - points[i].x)).toFixed(1) + `,` + points[i].y.toFixed(1);
                }}
                dPath += ` Z`; pathDrop.setAttribute('d', dPath);
            } else if (p <= 0.96) {{
                let fallProgress = (p - 0.88) / 0.08;
                let restH = 6 * (1.0 - fallProgress) + 1.0;
                pathDrop.setAttribute('d', `M 165,340 A 35,6 0 0,1 235,340 Z`);
                ballFly.style.display = 'block';
                let ballRadius = window.lastR * 0.84;
                let startY = 340 - window.lastH - 18;
                let curY = startY - (fallProgress * 280); 
                ballFly.setAttribute('cx', '200'); ballFly.setAttribute('cy', curY); ballFly.setAttribute('r', ballRadius);
            } else {{
                ballFly.style.display = 'none';
            }}
        }}, frameRateMs);
    </script>
    """
    return svg_html
