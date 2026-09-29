                } else if (p <= 0.88) {{
                    // ФАЗА 2: Наливание плотной грушевидной капли (Двухкруговая модель)
                    let sP = (p - 0.25) / 0.63; 
                    
                    // Высота капли плавно растет вверх
                    let totalH = 16 + (sP * 74); 
                    let topY = 320 - totalH;
                    
                    // Физические радиусы шейки и пуза
                    let curNeck = 30 - (30 - critNeck) * (sP * sP);
                    let bulbR = curNeck + (12 * Math.sin(sP * Math.PI / 2)); 
                    
                    // Координаты для сборки гладкого контура груши
                    let xLeftN = 200 - curNeck;
                    let xRightN = 200 + curNeck;
                    let xLeftB = 200 - bulbR;
                    let xRightB = 200 + bulbR;
                    
                    // Шейка (талия) находится в нижней трети, пузо - в верхней
                    let yNeck = 320 - (totalH * 0.25);
                    let yBulbCenter = topY + bulbR;

                    // БЕЗОПАСНАЯ ГЕОМЕТРИЯ:
                    // Плавные дуги (A) с нулевыми флагами вращения (0 0,0 и 0 0,1) 
                    // создают идеальное сужение у трубки и круглую луковицу сверху
                    let d = `M 170,320 
                             A 25,25 0 0,1 ${xLeftN},${yNeck}
                             A ${bulbR},${bulbH = totalH * 0.4} 0 0,1 ${xLeftB},${yBulbCenter}
                             A ${bulbR},${bulbR} 0 0,1 ${xRightB},${yBulbCenter}
                             A ${bulbR},${bulbH} 0 0,1 ${xRightN},${yNeck}
                             A 25,25 0 0,1 230,320 Z`;
                            
                    dropPath.setAttribute('d', d);
