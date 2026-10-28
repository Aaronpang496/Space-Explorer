import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="SFS Clone | Explosions", layout="wide", initial_sidebar_state="collapsed")

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
        body { margin: 0; overflow: hidden; background-color: #2b3a4a; font-family: 'Arial', sans-serif; touch-action: none; user-select: none; }
        canvas { display: block; }
        #ui-layer { position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 9999; }
        
        /* VAB Menu */
        #vab-menu { position: absolute; top: 10px; left: 10px; width: 100px; background: rgba(0,0,0,0.85); border: 2px solid #555; border-radius: 10px; display: flex; flex-direction: column; align-items: center; padding: 10px 0; pointer-events: auto; max-height: 90vh; overflow-y: auto; z-index: 10000;}
        .part-item { width: 80px; height: 50px; margin: 5px 0; background: #222; border: 2px solid #555; border-radius: 5px; color: white; font-size: 12px; display: flex; justify-content: center; align-items: center; text-align: center; cursor: pointer; transition: all 0.2s;}
        .part-item.active { border-color: #00ffcc; background: #114444; box-shadow: 0 0 10px #00ffcc;}
        
        /* Top Bar */
        #top-bar { position: absolute; top: 15px; left: 50%; transform: translateX(-50%); display: flex; gap: 10px; pointer-events: auto; z-index: 10000;}
        .top-btn { background: #1e3a8a; color: white; border: 2px solid #60a5fa; padding: 10px 20px; font-size: 16px; font-weight: bold; border-radius: 5px; cursor: pointer; font-family: inherit; box-shadow: 0 4px 6px rgba(0,0,0,0.3);}
        .top-btn:active { transform: scale(0.95); }
        
        /* Flight HUD */
        #hud { position: absolute; top: 15px; right: 15px; color: #fff; font-size: 14px; background: rgba(0,0,0,0.6); padding: 10px; border-radius: 5px; text-align: right; border-left: 3px solid #00ffcc; display: none; z-index: 10000;}
        
        /* Flight Controls */
        #throttle-zone { position: absolute; right: 20px; bottom: 80px; width: 40px; height: 180px; background: rgba(0,0,0,0.5); border: 2px solid #fff; border-radius: 20px; pointer-events: auto; display: none; z-index: 10000; }
        #throttle-fill { position: absolute; bottom: 0; width: 100%; height: 0%; background: linear-gradient(to top, #ff0000, #ffff00); border-radius: 18px;}
        
        #joy-left { position: absolute; left: 20px; bottom: 20px; width: 60px; height: 80px; background: rgba(0,0,0,0.5); border: 2px solid #fff; border-radius: 10px; display: none; justify-content: center; align-items: center; font-size: 30px; color: white; pointer-events: auto; z-index: 10000;}
        #joy-right { position: absolute; left: 100px; bottom: 20px; width: 60px; height: 80px; background: rgba(0,0,0,0.5); border: 2px solid #fff; border-radius: 10px; display: none; justify-content: center; align-items: center; font-size: 30px; color: white; pointer-events: auto; z-index: 10000;}
    </style>
</head>
<body>
    <canvas id="gameCanvas"></canvas>
    
    <div id="ui-layer">
        <div id="vab-menu">
            <div class="part-item active" data-type="pod">Pod</div>
            <div class="part-item" data-type="tank">Tank</div>
            <div class="part-item" data-type="engine">Engine</div>
            <div class="part-item" data-type="decoupler">Decoupler</div>
        </div>

        <div id="top-bar">
            <button class="top-btn" id="btn-clear">CLEAR</button>
            <button class="top-btn" id="btn-launch">LAUNCH</button>
            <button class="top-btn" id="btn-reset">RESET</button>
        </div>

        <div id="hud">
            ALT: <span id="val-alt">0</span> m<br>
            VEL: <span id="val-vel">0</span> m/s
        </div>
        
        <div id="throttle-zone"><div id="throttle-fill"></div></div>
        <div id="joy-left">◀</div>
        <div id="joy-right">▶</div>
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

        let state = {
            mode: "vab", 
            activePart: "pod",
            x: 0, y: 0, 
            vx: 0, vy: 0,
            angle: 0, 
            angularVelocity: 0, 
            throttle: 0,
            fuel: 100,
            cameraY: 0,
            lastTime: performance.now(),
            screenShake: 0,
            particles: [] // NEW: Particle System
        };

        const GRAVITY = 9.81;
        let rocketParts = []; 

        const partTypes = {
            pod: { width: 32, height: 36, type: "pod" },
            tank: { width: 30, height: 60, type: "tank" },
            engine: { width: 24, height: 26, type: "engine" },
            decoupler: { width: 26, height: 8, type: "decoupler" }
        };

        // --- UI LOGIC ---
        document.querySelectorAll('.part-item').forEach(item => {
            item.onclick = () => {
                document.querySelectorAll('.part-item').forEach(i => i.classList.remove('active'));
                item.classList.add('active');
                state.activePart = item.dataset.type;
            }
        });

        canvas.addEventListener('pointerdown', (e) => {
            if (state.mode === "vab") {
                const rect = canvas.getBoundingClientRect();
                const worldX = (e.clientX - rect.left - canvas.width/2) / 1.5;
                const worldY = ((canvas.height * 0.7) - (e.clientY - rect.top)) / 1.5;
                const snappedX = Math.round(worldX / 10) * 10;
                const snappedY = Math.round(worldY / 10) * 10;
                addPart(state.activePart, snappedX, snappedY);
            }
        });

        function addPart(type, x, y) {
            rocketParts.push({ ...partTypes[type], x: x, y: y, type: type });
        }

        addPart("engine", 0, 10);
        addPart("tank", 0, 50);
        addPart("tank", 0, 110);
        addPart("decoupler", 0, 150);
        addPart("pod", 0, 170);

        document.getElementById('btn-clear').onclick = () => { rocketParts = []; };

        // --- LAUNCH LOGIC ---
        document.getElementById('btn-launch').onclick = function() {
            if (state.mode === "vab") {
                let minX = 9999, maxX = -9999, minY = 9999;
                rocketParts.forEach(p => {
                    if (p.x - p.width/2 < minX) minX = p.x - p.width/2;
                    if (p.x + p.width/2 > maxX) maxX = p.x + p.width/2;
                    if (p.y - p.height/2 < minY) minY = p.y - p.height/2;
                });
                let offsetX = (minX + maxX) / 2;
                rocketParts.forEach(p => { p.x -= offsetX; p.y -= minY; });

                state.mode = "flight";
                document.getElementById('vab-menu').style.display = 'none';
                document.getElementById('btn-launch').style.display = 'none';
                document.getElementById('hud').style.display = 'block';
                document.getElementById('throttle-zone').style.display = 'block';
                document.getElementById('joy-left').style.display = 'flex';
                document.getElementById('joy-right').style.display = 'flex';
            }
        };

        document.getElementById('btn-reset').onclick = () => window.location.reload();

        // --- FLIGHT INPUTS ---
        let isDraggingThrottle = false;
        let leftPressed = false;
        let rightPressed = false;
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

        document.getElementById('joy-left').addEventListener('pointerdown', () => { leftPressed = true; });
        document.getElementById('joy-left').addEventListener('pointerup', () => { leftPressed = false; });
        document.getElementById('joy-right').addEventListener('pointerdown', () => { rightPressed = true; });
        document.getElementById('joy-right').addEventListener('pointerup', () => { rightPressed = false; });

        // --- PARTICLE SPAWNER ---
        function spawnParticles(x, y, count, type) {
            for (let i = 0; i < count; i++) {
                let angle = Math.random() * Math.PI * 2;
                let speed = Math.random() * 100;
                state.particles.push({
                    x: x, y: y,
                    vx: Math.cos(angle) * speed,
                    vy: Math.sin(angle) * speed,
                    life: 1.0,
                    maxLife: 1.0,
                    size: Math.random() * 20 + 10,
                    type: type
                });
            }
        }

        // --- PHYSICS ---
        function updatePhysics(dt) {
            if (state.mode === "crashed") {
                // Update particles on crash
                for (let i = state.particles.length - 1; i >= 0; i--) {
                    let p = state.particles[i];
                    p.x += p.vx * dt;
                    p.y += p.vy * dt;
                    p.vy += GRAVITY * dt; // Gravity affects particles
                    p.life -= dt * 0.5;
                    if (p.life <= 0) state.particles.splice(i, 1);
                }
                state.screenShake = Math.max(0, state.screenShake - dt * 5);
                return;
            }

            if (state.mode !== "flight") return;

            // Engine Smoke/Fire
            if (state.throttle > 0 && state.fuel > 0) {
                // Spawn fire particles at the bottom of the rocket
                let rad = state.angle * (Math.PI / 180);
                let ex = state.x - Math.sin(rad) * 30;
                let ey = state.y - Math.cos(rad) * 30;
                
                spawnParticles(ex, ey, 2, "fire");
            }

            // Update particles
            for (let i = state.particles.length - 1; i >= 0; i--) {
                let p = state.particles[i];
                p.x += p.vx * dt;
                p.y += p.vy * dt;
                p.life -= dt * 2; // Fade out
                if (p.life <= 0) state.particles.splice(i, 1);
            }

            if (leftPressed) state.angularVelocity -= 1.5 * dt;
            if (rightPressed) state.angularVelocity += 1.5 * dt;
            if (!leftPressed && !rightPressed) state.angularVelocity *= 0.95;
            state.angle += state.angularVelocity;

            let ay = -GRAVITY;
            let ax = 0;
            let hasEngine = rocketParts.some(p => p.type === "engine");

            if (state.throttle > 0 && state.fuel > 0 && hasEngine) {
                let thrustAccel = 30 * state.throttle;
                let rad = state.angle * (Math.PI / 180);
                ax += thrustAccel * Math.sin(rad);
                ay += thrustAccel * Math.cos(rad);
                state.fuel -= 5 * state.throttle * dt;
                if (state.fuel <= 0) { state.fuel = 0; state.throttle = 0; throttleFill.style.height = '0%'; }
            }

            state.vx += ax * dt;
            state.vy += ay * dt;
            state.x += state.vx * dt;
            state.y += state.vy * dt;

            // --- CRASH LOGIC ---
            if (state.y < 0) {
                state.y = 0;
                let impactSpeed = Math.abs(state.vy);
                
                if (impactSpeed > 5) {
                    // EXPLODE!
                    state.mode = "crashed";
                    state.screenShake = 30;
                    document.getElementById('hud').style.display = 'none';
                    document.getElementById('throttle-zone').style.display = 'none';
                    document.getElementById('joy-left').style.display = 'none';
                    document.getElementById('joy-right').style.display = 'none';
                    
                    // Spawn massive explosion
                    spawnParticles(state.x, state.y, 150, "explosion");
                    spawnParticles(state.x, state.y, 50, "smoke");
                } else {
                    state.vy = 0; state.vx = 0; state.angle = 0; state.angularVelocity = 0;
                }
            }

            state.cameraY += (state.y - state.cameraY) * 5 * dt;

            document.getElementById('val-alt').innerText = state.y.toFixed(1);
            document.getElementById('val-vel').innerText = Math.sqrt(state.vx*state.vx + state.vy*state.vy).toFixed(1);
        }

        // --- DRAWING ---
        function drawPod(x, y, w, h) {
            ctx.fillStyle = "#7a7a7a";
            ctx.beginPath();
            ctx.moveTo(x - w/2, y + h/2);
            ctx.lineTo(x + w/2, y + h/2);
            ctx.lineTo(x + w/3, y - h/2);
            ctx.lineTo(x - w/3, y - h/2);
            ctx.fill();
            ctx.fillStyle = "#444";
            ctx.beginPath();
            ctx.arc(x, y, w/4, 0, Math.PI*2);
            ctx.fill();
        }

        function drawTank(x, y, w, h) {
            const grad = ctx.createLinearGradient(x - w/2, 0, x + w/2, 0);
            grad.addColorStop(0, "#aaa");
            grad.addColorStop(0.3, "#fff");
            grad.addColorStop(0.7, "#fff");
            grad.addColorStop(1, "#888");
            ctx.fillStyle = grad;
            ctx.fillRect(x - w/2, y - h/2, w, h);
        }

        function drawEngine(x, y, w, h) {
            const grad = ctx.createLinearGradient(x - w/2, 0, x + w/2, 0);
            grad.addColorStop(0, "#111");
            grad.addColorStop(0.5, "#555");
            grad.addColorStop(1, "#111");
            ctx.fillStyle = grad;
            ctx.beginPath();
            ctx.moveTo(x - w/3, y - h/2);
            ctx.lineTo(x + w/3, y - h/2);
            ctx.lineTo(x + w/2, y + h/2);
            ctx.lineTo(x - w/2, y + h/2);
            ctx.fill();
        }

        function drawDecoupler(x, y, w, h) {
            ctx.fillStyle = "#5c3a21";
            ctx.fillRect(x - w/2, y - h/2, w, h);
        }

        function draw() {
            // Apply screen shake
            ctx.save();
            if (state.screenShake > 0) {
                let sx = (Math.random() - 0.5) * state.screenShake;
                let sy = (Math.random() - 0.5) * state.screenShake;
                ctx.translate(sx, sy);
            }

            // Sky
            let grad = ctx.createLinearGradient(0, 0, 0, canvas.height);
            if (state.mode === "vab") {
                grad.addColorStop(0, "#1e293b");
                grad.addColorStop(1, "#0f172a");
            } else {
                let alt = state.y;
                if (alt < 5000) {
                    grad.addColorStop(0, "#4a90e2"); grad.addColorStop(1, "#87CEEB");
                } else if (alt < 25000) {
                    grad.addColorStop(0, "#0b1a3a"); grad.addColorStop(1, "#1a3b5c");
                } else {
                    grad.addColorStop(0, "#000000"); grad.addColorStop(1, "#000000");
                }
            }
            ctx.fillStyle = grad;
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            ctx.translate(canvas.width / 2, canvas.height * 0.7); 
            let zoom = state.mode === "vab" ? 1.5 : Math.max(0.5, 1.5 - (state.y / 50000));
            ctx.scale(zoom, zoom);

            if (state.mode === "vab") {
                ctx.strokeStyle = "rgba(255,255,255,0.05)";
                for(let i=-1000; i<1000; i+=10) { ctx.beginPath(); ctx.moveTo(i, -1000); ctx.lineTo(i, 1000); ctx.stroke(); }
                for(let i=-1000; i<1000; i+=10) { ctx.beginPath(); ctx.moveTo(-1000, i); ctx.lineTo(1000, i); ctx.stroke(); }

                rocketParts.forEach(p => {
                    let py = -p.y;
                    if (p.type === "pod") drawPod(p.x, py, p.width, p.height);
                    if (p.type === "tank") drawTank(p.x, py, p.width, p.height);
                    if (p.type === "engine") drawEngine(p.x, py, p.width, p.height);
                    if (p.type === "decoupler") drawDecoupler(p.x, py, p.width, p.height);
                });
            } else {
                ctx.fillStyle = "#2e4a2e";
                ctx.fillRect(-10000, 0, 20000, -10000);

                // Draw Rocket
                if (state.mode !== "crashed") {
                    ctx.save();
                    ctx.translate(state.x, -state.cameraY);
                    ctx.rotate(state.angle * (Math.PI / 180));
                    
                    rocketParts.forEach(p => {
                        let py = -p.y;
                        if (p.type === "pod") drawPod(p.x, py, p.width, p.height);
                        if (p.type === "tank") drawTank(p.x, py, p.width, p.height);
                        if (p.type === "engine") drawEngine(p.x, py, p.width, p.height);
                        if (p.type === "decoupler") drawDecoupler(p.x, py, p.width, p.height);
                    });
                    ctx.restore();
                }

                // Draw Particles (Fire, Smoke, Explosion)
                state.particles.forEach(p => {
                    let color = "";
                    if (p.type === "fire") color = `rgba(255, ${150 * p.life}, 0, ${p.life})`;
                    if (p.type === "explosion") color = `rgba(255, 50, 0, ${p.life})`;
                    if (p.type === "smoke") color = `rgba(100, 100, 100, ${p.life * 0.5})`;
                    
                    ctx.fillStyle = color;
                    ctx.beginPath();
                    ctx.arc(p.x, -p.y + state.cameraY, p.size * p.life, 0, Math.PI * 2);
                    ctx.fill();
                });
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
    </script>
</body>
</html>
"""

components.html(game_html, height=900, scrolling=False)
