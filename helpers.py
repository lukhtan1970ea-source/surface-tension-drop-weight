def generate_stand_svg(target_drops, sigma_true, is_running):
    """Генерує стабільну анімацію лабораторного стенду з вагами"""
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
