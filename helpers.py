def generate_stand_svg(target_drops, sigma_true, is_running):
    """
    Автономний динамічний JS/SVG рушій лабораторного стенду з вагою.
    Синхронізує візуальний політ кожної краплі з реальним часом, 
    плавним набранням маси на табло електронних ваг та рівнем рідини у склянці.
    """
    
    # Визначаємо фізичний радіус каплиці на стенді залежно від поверхневого натягу (в пікселях)
    base_drop_r = max(6.0, min(14.0, (sigma_true * 1000) * 0.18))
    
    html_code = f"""
    <div style="background: #161616; padding: 15px; border-radius: 16px; width: 330px; margin: 0 auto; box-shadow: 0 8px 32px rgba(0,0,0,0.6); border: 1px solid #333; text-align: center;">
        <svg id="stand-container" width="300" height="440" viewBox="0 0 300 440" style="background: #111311; border: 3px solid #444; border-radius: 8px;">
            
            <!-- Металевий штатив установки сталагмометра -->
            <rect x="0" y="0" width="12" height="440" fill="#3a3a3a" />
            <rect x="0" y="240" width="150" height="10" fill="#2b2b2b" />
            
            <!-- Скляна трубка дозатора рідини -->
            <rect x="135" y="0" width="30" height="80" fill="#444" opacity="0.4" />
            <rect x="140" y="0" width="20" height="80" fill="#111311" />
            <line x1="140" y1="80" x2="160" y2="80" stroke="#777" stroke-width="2" />

            <!-- Динамічна капілярна капля на зрізі дозатора -->
            <path id="stand-drop" d="M 140,80 A 10,1 0 0,0 160,80 Z" fill="rgba(100, 200, 255, 0.45)" stroke="lightskyblue" stroke-width="1.5" />
            
            <!-- Летяча сфера відриву -->
            <circle id="stand-flying-ball" cx="160" cy="80" r="0" fill="rgba(100, 200, 255, 0.55)" stroke="lightskyblue" stroke-width="1" style="display: none;" />

            <!-- ЛАБОРАТОРНА ХІМІЧНА СКЛЯНКА НА ВАГАХ -->
            <!-- Задній план склянки та динамічний рівень налитої фракції рідини -->
            <rect id="fluid-level" x="98" y="380" width="104" height="0" fill="rgba(100, 200, 255, 0.25)" style="transition: height 0.3s;" />
            <!-- Стінки склянки -->
            <path d="M 95,310 L 95,380 L 205,380 L 205,310" fill="none" stroke="#eee" stroke-width="2.5" opacity="0.9" />

            <!-- МЕХАНІЧНА ПЛАТФОРМА ЛАБОРАТОРНИХ ВАГ -->
            <rect x="60" y="380" width="180" height="12" fill="#444" rx="3" />
            <rect x="70" y="392" width="160" height="40" fill="#222" rx="4" stroke="#333" stroke-width="2" />
            
            <!-- ЕЛЕКТРОННЕ СВІТЛОДІОДНЕ ТАБЛО ВАГ (Синхронізується в реальному часі!) -->
            <text id="scale-display" x="150" y="418" fill="#00ff66" font-family="monospace" font-size="22" font-weight="bold" text-anchor="middle">0.000 г</text>
        </svg>
    </div>
    
    <!-- Передаємо константи з Python у приховані змінні для JS-двигуна -->
    <input type="hidden" id="param-target-drops" value="{target_drops}">
    <input type="hidden" id="param-is-running" value="{"true" if is_running else "false"}">
    <input type="hidden" id="param-base-radius" value="{base_drop_r}">
    <script>
        // Повне скидання фонових процесів стенду при оновленні
        if (window.standAnimInterval) { clearInterval(window.standAnimInterval); }

        const standDrop = document.getElementById('stand-drop');
        const standBall = document.getElementById('stand-flying-ball');
        const scaleDisplay = document.getElementById('scale-display');
        const fluidLevel = document.getElementById('fluid-level');

        // Зчитуємо константи, які прийшли з Python
        const targetDrops = parseInt(document.getElementById('param-target-drops').value) || 20;
        const isRunning = document.getElementById('param-is-running').value === "true";
        const baseRadius = parseFloat(document.getElementById('param-base-radius').value) || 8.0;

        // Емуляція ваги: беремо усереднену реалістичну вагу всієї фракції
        const totalTargetMass = targetDrops * 0.042; // базовий орієнтир маси
        const massPerDrop = totalTargetMass / targetDrops;

        let currentDropCount = 0;
        let standElapsed = 0;
        const cycleTime = 1200; // швидкість капання на стенді: 1.2 секунди на краплю
        const fpsMs = 20;

        if (isRunning) {
            window.standAnimInterval = setInterval(() => {
                if (!document.getElementById('stand-container')) {
                    clearInterval(window.standAnimInterval);
                    return;
                }

                standElapsed += fpsMs;
                let p = (standElapsed % cycleTime) / cycleTime;

                if (currentDropCount >= targetDrops) {
                    // Дозатор виконав норму, зупиняємо процес
                    standDrop.setAttribute('d', 'M 140,80 A 10,1 0 0,0 160,80 Z');
                    standBall.style.display = 'none';
                    scaleDisplay.textContent = totalTargetMass.toFixed(3) + " г";
                    fluidLevel.setAttribute('height', (targetDrops * 1.5).toString());
                    fluidLevel.setAttribute('y', (380 - targetDrops * 1.5).toString());
                    clearInterval(window.standAnimInterval);
                    return;
                }

                if (p <= 0.75) {
                    // ФАЗА 1: Крапля плавно наливається і роздувається на кінчику трубки
                    standBall.style.display = 'none';
                    let grow = p / 0.75;
                    let curH = 1 + (grow * baseRadius * 1.3);
                    let curR = 10 + (grow * (baseRadius - 10));
                    standDrop.setAttribute('d', `M 140,80 C 140,80 140,${80+curH} 150,${80+curH} C 160,${80+curH} 160,80 160,80 Z`);
                } else if (p <= 0.95) {
                    // ФАЗА 2: Політ відірваної сфери вниз до склянки
                    standDrop.setAttribute('d', 'M 140,80 A 10,1 0 0,0 160,80 Z'); // меніск затягнувся
                    standBall.style.display = 'block';
                    
                    let fall = (p - 0.75) / 0.20;
                    let startY = 80 + baseRadius;
                    let curY = startY + (fall * (375 - startY)); // летимо точно до дна (Y=375)
                    
                    standBall.setAttribute('cx', '150');
                    standBall.setAttribute('cy', curY.toFixed(1));
                    standBall.setAttribute('r', (baseRadius * 0.85).toFixed(1));
                } else {
                    // ФАЗА 3: Крапля вдарилася об дно! Оновлюємо масу та рівень рідини
                    if (p - 0.95 <= fpsMs / cycleTime) {
                        currentDropCount++;
                        
                        // Плавне збільшення показань на табло в момент удару краплі!
                        let currentMass = currentDropCount * massPerDrop;
                        scaleDisplay.textContent = currentMass.toFixed(3) + " г";
                        
                        // Рідина у склянці піднімається
                        let curHeight = currentDropCount * 1.5; // 1.5px на кожну краплю
                        fluidLevel.setAttribute('height', curHeight.toString());
                        fluidLevel.setAttribute('y', (380 - curHeight).toString());
                    }}
            }, fpsMs);
        } else {
            // Якщо кран перекрито — табло ваг та склянка чисті
            scaleDisplay.textContent = "0.000 г";
            fluidLevel.setAttribute('height', '0');
            fluidLevel.setAttribute('y', '380');
            standDrop.setAttribute('d', 'M 140,80 A 10,1 0 0,0 160,80 Z');
            standBall.style.display = 'none';
        }
    </script>
    """
    return html_code

