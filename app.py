import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="SFS Clone | Balanced Camera", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    .block-container { padding: 0rem !important; margin: 0rem !important; max-width: 100% !important; }
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    iframe { border: none; }
</style>
""", unsafe_allow_html=True)

game_html = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body { margin: 0; overflow: hidden; background-color: #000; font-family: 'Arial', sans-serif; touch-action: none; user-select: none; }
        canvas { display: block; }
        #ui-layer { position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 9999; }
        
        /* Top Right Telemetry */
        #hud { position: absolute; top: 15px; right: 15px; color: #fff; font-size: 14px; text-align: right; line-height: 1.4; text-shadow: 1px 1px 2px #000; font-weight: bold;}
        #hud span { color: #00ffcc; }
        
        /* Bottom Left Fuel Gauge */
        #fuel-gauge { position: absolute; bottom: 20px; left: 20px; display: flex; flex-direction: column; align-items: flex-start; gap: 2px;}
        .fuel-bar { width: 50px; height: 10px; background: #fff; border: 1px solid #000; transition: opacity 0.2s;}
        .fuel-label { color: #fff; font-size: 12px; margin-bottom: 5px; font-weight: bold; text-shadow: 1px 1px 2px #000;}

        /* Bottom Right Throttle */
        #throttle-zone { position: absolute; right: 20px; bottom: 80px; width: 40px; height: 180px; background: rgba(0,0,0,0.4); border: 2px solid #fff; border-radius: 5px; pointer-events: auto; }
        #throttle-fill { position: absolute; bottom: 0; width: 100%; height: 0%; background: #fff; }
        
        /* Bottom Center Arrows */
        #arrow-zone { position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%); display: flex; gap: 30px; pointer-events: auto;}
        .arrow-btn { width: 60px; height: 60px; background: rgba(0,0,0,0.5); border: 2px solid #fff; border-radius: 10px; color: white; font-size: 30px; display: flex; justify-content: center; align-items: center; cursor: pointer;}
        
        /* Landing Legs Button */
        #btn-legs { position: absolute; bottom: 80px; right: 80px; width: 80px; height: 40px; background: rgba(0,0,0,0.5); border: 2px solid #fff; color: white; border-radius: 5px; font-size: 12px; font-weight: bold; pointer-events: auto;}
        #btn-legs.deployed { border-color: #00ffcc; color: #00ffcc; }

        /* Top Bar */
        #top-bar { position: absolute; top: 15px; left: 50%; transform: translateX(-50%); display: flex; gap: 10px; pointer-events: auto; }
        .top-btn { background: rgba(0,0,0,0.5); color: white; border: 2px solid #fff; padding: 8px 16px; font-size: 14px; font-weight: bold; border-radius: 5px; cursor: pointer;}
        
        /* Messages */
        #message-overlay { position: absolute; top: 40%; left: 50%; transform: translate(-50%, -50%); font-size: 30px; font-weight: bold; text-align: center; display: none; text-shadow: 2px 2px 5px #000; pointer-events: none;}
        .crash-msg { color: #ff4444; }
        .land-msg { color: #00ffcc; }
    </style>
</head>
<body>
    <canvas id="gameCanvas"></canvas>
    
    <div id="ui-layer">
        <div id="hud">
            Height: <span id="val-alt">0</span> m<br>
            Velocity: <span id="val-vel">0</span> m/s
        </div>

        <div id="fuel-gauge">
            <div class="fuel-label">Liquid fuel:</div>
            <div class="fuel-bar"></div>
            <div class="fuel-bar"></div>
            <div class="fuel-bar"></div>
            <div class="fuel-bar"></div>
            <div class="fuel-bar"></div>
        </div>

        <div id="top-bar">
            <button class="top-btn" id="btn-launch">LAUNCH 🚀</button>
            <button class="top-btn" id="btn-reset">RESET 🔄</button>
        </div>

        <button id="btn-legs">LEGS: UP</button>

        <div id="throttle-zone"><div id="throttle-fill"></div></div>
        
        <div id="arrow-zone">
            <div class="arrow-btn" id="btn-left">◀</div>
            <div class="arrow-btn" id="btn-right">▶</div>
        </div>

        <div id="message-overlay"></div>
    </div>

    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        
        function resize() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }
        window.addEventListener('resize', resize);
        resize();

        // --- GAME STATE ---
        let state = {
            mode: "pad", // "pad", "flight", "crashed", "landed"
            x: 0, y: 0, 
            vx: 0, vy: 0,
            angle: 0, 
            angularVelocity: 0, 
            throttle: 0,
            fuel: 100,
            legsDeployed: false,
            cameraY: 0, 
            lastTime: performance.now()
        };

        const GRAVITY = 9.81;
        const PAD_Y = 0; 
        const THRUST_POWER = 35; 

        const rocket = {
            bodyWidth: 30,
            bodyHeight: 100,
            noseHeight: 30,
            engineWidth: 20,
            engineHeight: 20,
        };

        // --- INPUT HANDLING ---
        let leftPressed = false;
        let rightPressed = false;
        let isDraggingThrottle = false;
        const throttleZone = document.getElementById('throttle-zone');
        const throttleFill = document.getElementById('throttle-fill');

        throttleZone.addEventListener('pointerdown', (e) => { isDraggingThrottle = true; throttleZone.setPointerCapture(e.pointerId); });
        throttleZone.addEventListener('pointerup', () => { isDraggingThrottle = false; });
        throttleZone.addEventListener('pointermove', (e) => {
            if (!isDraggingThrottle) return;
            const rect = throttleZone.getBoundingClientRect();
            let y = e.clientY - rect.top;
            if (y < 0) y = 0; if (y > 180) y = 180;
            let percent = 100 - (y / 180) * 100;
            state.throttle = percent / 100;
            throttleFill.style.height = percent + '%';
        });

        document.getElementById('btn-left').addEventListener('pointerdown', () => { leftPressed = true; });
        document.getElementById('btn-left').addEventListener('pointerup', () => { leftPressed = false; });
        document.getElementById('btn-right').addEventListener('pointerdown', () => { rightPressed = true; });
        document.getElementById('btn-right').addEventListener('pointerup', () => { rightPressed = false; });

        document.getElementById('btn-legs').onclick = () => {
            state.legsDeployed = !state.legsDeployed;
            const btn = document.getElementById('btn-legs');
            if (state.legsDeployed) {
                btn.innerText = "LEGS: DOWN";
                btn.classList.add('deployed');
            } else {
                btn.innerText = "LEGS: UP";
                btn.classList.remove('deployed');
            }
        };

        // --- PHYSICS LOOP ---
        function updatePhysics(dt) {
            if (state.mode === "pad") {
                state.y = rocket.bodyHeight/2 + rocket.engineHeight + PAD_Y;
                state.vx = 0; state.vy = 0; state.angle = 0; state.angularVelocity = 0;
            } 
            else if (state.mode === "flight") {
                // Rotation
                if (leftPressed) state.angularVelocity -= 1.5 * dt;
                if (rightPressed) state.angularVelocity += 1.5 * dt;
                if (!leftPressed && !rightPressed) state.angularVelocity *= 0.95;
                state.angle += state.angularVelocity;

                // Thrust
                let ay = -GRAVITY;
                let ax = 0;

                if (state.throttle > 0 && state.fuel > 0) {
                    let rad = state.angle * (Math.PI / 180);
                    ax += THRUST_POWER * state.throttle * Math.sin(rad);
                    ay += THRUST_POWER * state.throttle * Math.cos(rad);
                    
                    state.fuel -= 10 * state.throttle * dt;
                    if (state.fuel <= 0) { state.fuel = 0; state.throttle = 0; throttleFill.style.height = '0%'; }
                    updateFuelUI();
                }

                // Integrate
                state.vx += ax * dt;
                state.vy += ay * dt;
                state.x += state.vx * dt;
                state.y += state.vy * dt;

                // Camera Follow (Smooth)
                state.cameraY += (state.y - state.cameraY) * 5 * dt;

                // --- LANDING / CRASH LOGIC ---
                let bottomOfRocket = state.y - (rocket.bodyHeight/2 + rocket.engineHeight);
                
                if (bottomOfRocket <= PAD_Y) {
                    let impactSpeed = Math.abs(state.vy);
                    
                    if (impactSpeed > 5) {
                        state.mode = "crashed";
                        showMessage("💥 CRASHED", "crash-msg");
                    } else if (!state.legsDeployed) {
                        state.mode = "crashed";
                        showMessage("💥 CRUSHED (NO GEAR)", "crash-msg");
                    } else {
                        state.mode = "landed";
                        state.y = PAD_Y + rocket.bodyHeight/2 + rocket.engineHeight;
                        state.vy = 0; state.vx = 0; state.angle = 0; state.angularVelocity = 0;
                        state.throttle = 0;
                        throttleFill.style.height = '0%';
                        showMessage("🏆 LANDED SAFELY", "land-msg");
                    }
                }

                // Update HUD
                document.getElementById('val-alt').innerText = (state.y - PAD_Y).toFixed(1);
                document.getElementById('val-vel').innerText = Math.sqrt(state.vx*state.vx + state.vy*state.vy).toFixed(1);
                
                if (state.vy < -5) {
                    document.getElementById('val-vel').style.color = "#ff4444";
                } else {
                    document.getElementById('val-vel').style.color = "#00ffcc";
                }
            }
        }

        function updateFuelUI() {
            const bars = document.querySelectorAll('.fuel-bar');
            const numBars = bars.length;
            const barsToShow = Math.ceil((state.fuel / 100) * numBars);
            bars.forEach((bar, index) => {
                bar.style.opacity = (index < barsToShow) ? '1' : '0.1';
            });
        }

        function showMessage(text, className) {
            const msg = document.getElementById('message-overlay');
            msg.innerText = text;
            msg.className = className;
            msg.style.display = 'block';
        }

        // --- RENDER LOOP ---
        function draw() {
            // Sky
            let alt = state.y;
            if (alt < 5000) {
                let grad = ctx.createLinearGradient(0, 0, 0, canvas.height);
                grad.addColorStop(0, "#4a90e2");
                grad.addColorStop(1, "#87CEEB");
                ctx.fillStyle = grad;
            } else if (alt < 25000) {
                ctx.fillStyle = "#0b1a3a";
            } else {
                ctx.fillStyle = "#000000";
            }
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // --- BALANCED CAMERA ZOOM ---
            ctx.save();
            ctx.translate(canvas.width / 2, canvas.height * 0.7); 
            
            let zoom = Math.max(0.8, 1.5 - (state.y / 50000));
            
            ctx.scale(zoom, zoom);
            ctx.translate(0, -state.cameraY);

            // Ground
            if (state.cameraY < 2000) {
                ctx.fillStyle = "#4a3b2c"; 
                ctx.fillRect(-100000, PAD_Y, 200000, -10000);
                ctx.fillStyle = "#666666";
                ctx.fillRect(-50, PAD_Y - 5, 100, 5);
            }

            // Draw Rocket
            if (state.mode !== "crashed") {
                ctx.save();
                ctx.translate(state.x, state.y);
                ctx.rotate(state.angle * (Math.PI / 180));

                // Fire
                if (state.throttle > 0 && state.fuel > 0 && state.mode === "flight") {
                    let fireLen = 40 + (state.throttle * 60);
                    ctx.fillStyle = "rgba(255, 100, 0, 0.8)";
                    ctx.beginPath();
                    ctx.moveTo(-rocket.engineWidth/2, rocket.bodyHeight/2 + rocket.engineHeight);
                    ctx.lineTo(rocket.engineWidth/2, rocket.bodyHeight/2 + rocket.engineHeight);
                    ctx.lineTo(0, rocket.bodyHeight/2 + rocket.engineHeight + fireLen);
                    ctx.fill();
                }

                // Landing Legs
                if (state.legsDeployed) {
                    ctx.strokeStyle = "#888";
                    ctx.lineWidth = 4;
                    ctx.beginPath();
                    ctx.moveTo(-rocket.bodyWidth/2, rocket.bodyHeight/2); 
                    ctx.lineTo(-rocket.bodyWidth/2 - 15, rocket.bodyHeight/2 + 20); 
                    ctx.moveTo(rocket.bodyWidth/2, rocket.bodyHeight/2); 
                    ctx.lineTo(rocket.bodyWidth/2 + 15, rocket.bodyHeight/2 + 20); 
                    ctx.stroke();
                }

                // Engine
                ctx.fillStyle = "#222";
                ctx.beginPath();
                ctx.moveTo(-rocket.engineWidth/2, rocket.bodyHeight/2 + rocket.engineHeight);
                ctx.lineTo(rocket.engineWidth/2, rocket.bodyHeight/2 + rocket.engineHeight);
                ctx.lineTo(rocket.bodyWidth/3, rocket.bodyHeight/2);
                ctx.lineTo(-rocket.bodyWidth/3, rocket.bodyHeight/2);
                ctx.fill();

                // Body
                ctx.fillStyle = "#fff";
                ctx.fillRect(-rocket.bodyWidth/2, -rocket.bodyHeight/2, rocket.bodyWidth, rocket.bodyHeight);

                // Nose
                ctx.fillStyle = "#888";
                ctx.beginPath();
                ctx.moveTo(-rocket.bodyWidth/2, -rocket.bodyHeight/2);
                ctx.lineTo(rocket.bodyWidth/2, -rocket.bodyHeight/2);
                ctx.lineTo(0, -rocket.bodyHeight/2 - rocket.noseHeight);
                ctx.fill();

                ctx.restore();
            }

            ctx.restore();
        }

        function loop(timestamp) {
            let dt = (timestamp - state.lastTime) / 1000;
            state.lastTime = timestamp;
            if (dt > 0.1) dt = 0.1; 

            updatePhysics(dt);
            draw();
            requestAnimationFrame(loop);
        }
        requestAnimationFrame(loop);

        // --- BUTTONS ---
        document.getElementById('btn-launch').onclick = () => {
            if (state.mode === "pad") {
                state.mode = "flight";
                document.getElementById('btn-launch').style.display = 'none';
                document.getElementById('btn-legs').style.display = 'block';
            }
        };

        document.getElementById('btn-reset').onclick = () => {
            state.mode = "pad";
            state.x = 0; state.y = 150; 
            state.vx = 0; state.vy = 0; state.angle = 0; state.angularVelocity = 0;
            state.throttle = 0; state.fuel = 100; state.legsDeployed = false;
            state.cameraY = state.y;
            throttleFill.style.height = '0%';
            document.getElementById('btn-launch').style.display = 'block';
            document.getElementById('btn-legs').style.display = 'none';
            document.getElementById('btn-legs').innerText = "LEGS: UP";
            document.getElementById('btn-legs').classList.remove('deployed');
            document.getElementById('message-overlay').style.display = 'none';
            updateFuelUI();
        };

        updateFuelUI();
    </script>
</body>
</html>
"""

components.html(game_html, height=900, scrolling=False)
