import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="SFS Builder", layout="wide", initial_sidebar_state="collapsed")

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
        body { margin: 0; overflow: hidden; background-color: #1e293b; font-family: 'Arial', sans-serif; touch-action: none; user-select: none; }
        canvas { display: block; }
        #ui-layer { position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 9999; }
        
        /* VAB Menu */
        #vab-menu { position: absolute; top: 10px; left: 10px; width: 120px; background: rgba(0,0,0,0.85); border: 2px solid #555; border-radius: 10px; display: flex; flex-direction: column; align-items: center; padding: 10px 0; pointer-events: auto; max-height: 90vh; overflow-y: auto; z-index: 10000;}
        .part-item { width: 100px; height: 60px; margin: 5px 0; background: #222; border: 2px solid #555; border-radius: 5px; color: white; font-size: 14px; font-weight: bold; display: flex; justify-content: center; align-items: center; text-align: center; cursor: grab;}
        .part-item:active { cursor: grabbing; border-color: #00ffcc; }
        
        /* Top Bar */
        #top-bar { position: absolute; top: 15px; left: 50%; transform: translateX(-50%); display: flex; gap: 10px; pointer-events: auto; z-index: 10000;}
        .top-btn { background: #1e3a8a; color: white; border: 2px solid #60a5fa; padding: 10px 20px; font-size: 16px; font-weight: bold; border-radius: 5px; cursor: pointer; font-family: inherit;}
        
        /* Flight HUD */
        #hud { position: absolute; top: 15px; right: 15px; color: #fff; font-size: 14px; background: rgba(0,0,0,0.6); padding: 10px; border-radius: 5px; text-align: right; border-left: 3px solid #00ffcc; display: none; z-index: 10000;}
        
        /* Flight Controls */
        #throttle-zone { position: absolute; right: 20px; bottom: 80px; width: 40px; height: 180px; background: rgba(0,0,0,0.5); border: 2px solid #fff; border-radius: 20px; pointer-events: auto; display: none; z-index: 10000; }
        #throttle-fill { position: absolute; bottom: 0; width: 100%; height: 0%; background: #ffaa00; border-radius: 18px;}
        
        #joy-left { position: absolute; left: 20px; bottom: 20px; width: 60px; height: 80px; background: rgba(0,0,0,0.5); border: 2px solid #fff; border-radius: 10px; display: none; justify-content: center; align-items: center; font-size: 30px; color: white; pointer-events: auto; z-index: 10000;}
        #joy-right { position: absolute; left: 100px; bottom: 20px; width: 60px; height: 80px; background: rgba(0,0,0,0.5); border: 2px solid #fff; border-radius: 10px; display: none; justify-content: center; align-items: center; font-size: 30px; color: white; pointer-events: auto; z-index: 10000;}
    </style>
</head>
<body>
    <canvas id="gameCanvas"></canvas>
    
    <div id="ui-layer">
        <div id="vab-menu">
            <div class="part-item" draggable="true" data-type="pod">Pod</div>
            <div class="part-item" draggable="true" data-type="tank">Tank</div>
            <div class="part-item" draggable="true" data-type="engine">Engine</div>
            <div class="part-item" draggable="true" data-type="decoupler">Decoupler</div>
        </div>

        <div id="top-bar">
            <button class="top-btn" id="btn-clear">CLEAR</button>
            <button class="top-btn" id="btn-launch">LAUNCH</button>
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
            x: 0, y: 0, vx: 0, vy: 0,
            angle: 0, angularVelocity: 0, 
            throttle: 0, fuel: 100,
            cameraY: 0, lastTime: performance.now(),
            particles: []
        };

        const GRAVITY = 9.81;
        let rocketParts = []; 
        let draggedType = null;
        
        // Grid size for snapping
        const GRID = 15; 

        const partTypes = {
            pod: { width: 30, height: 30 },
            tank: { width: 30, height: 60 },
            engine: { width: 24, height: 24 },
            decoupler: { width: 26, height: 10 }
        };

        // --- DRAG AND DROP LOGIC ---
        document.querySelectorAll('.part-item').forEach(item => {
            item.addEventListener('dragstart', (e) => {
                draggedType = e.target.dataset.type;
            });
        });

        canvas.addEventListener('dragover', (e) => {
            e.preventDefault(); // Allow drop
        });

        canvas.addEventListener('drop', (e) => {
            e.preventDefault();
            if (state.mode === "vab" && draggedType) {
                const rect = canvas.getBoundingClientRect();
                const worldX = (e.clientX - rect.left - canvas.width/2) / 1.5;
                const worldY = ((canvas.height * 0.7) - (e.clientY - rect.top)) / 1.5;
                
                // Snap to grid
                const snappedX = Math.round(worldX / GRID) * GRID;
                const snappedY = Math.round(worldY / GRID) * GRID;

                addPart(draggedType, snappedX, snappedY);
                draggedType = null;
            }
        });

        // Fallback for mobile tap-to-place
        canvas.addEventListener('pointerdown', (e) => {
            if (state.mode === "vab" && draggedType) {
                const rect = canvas.getBoundingClientRect();
                const worldX = (e.clientX - rect.left - canvas.width/2) / 1.5;
                const worldY = ((canvas.height * 0.7) - (e.clientY - rect.top)) / 1.5;
                const snappedX = Math.round(worldX / GRID) * GRID;
                const snappedY = Math.round(worldY / GRID) * GRID;
                addPart(draggedType, snappedX, snappedY);
                draggedType = null;
            }
        });

        function addPart(type, x, y) {
            rocketParts.push({ ...partTypes[type], x: x, y: y, type: type });
        }

        // Default rocket
        addPart("engine", 0, 12);
        addPart("tank", 0, 54);
        addPart("tank", 0, 114);
        addPart("pod", 0, 159);

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

        // --- PHYSICS ---
        function updatePhysics(dt) {
            if (state.mode !== "flight") return;

            // Rotation
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
                
                // Spawn fire particles
                for(let i=0; i<3; i++) {
                    state.particles.push({
                        x: state.x - Math.sin(rad)*20 + (Math.random()-0.5)*10,
                        y: state.y - Math.cos(rad)*20 + (Math.random()-0.5)*10,
                        vx: -Math.sin(rad)*50 + (Math.random()-0.5)*20,
                        vy: -Math.cos(rad)*50 + (Math.random()-0.5)*20,
                        life: 1.0, size: Math.random()*8+4, color: "255,150,0"
                    });
                }
            }

            state.vx += ax * dt;
            state.vy += ay * dt;
            state.x += state.vx * dt;
            state.y += state.vy * dt;

            if (state.y < 0) {
                state.y = 0;
                if (Math.abs(state.vy) > 5) {
                    // EXPLODE
                    state.mode = "crashed";
                    for(let i=0; i<50; i++) {
                        state.particles.push({
                            x: state.x, y: state.y,
                            vx: (Math.random()-0.5)*200,
                            vy: (Math.random()-0.5)*200,
                            life: 1.5, size: Math.random()*15+5, color: "255,50,0"
                        });
                    }
                    document.getElementById('hud').innerText = "CRASHED";
                } else {
                    state.vy = 0; state.vx = 0; state.angle = 0; state.angularVelocity = 0;
                }
            }

            // Update particles
            for (let i = state.particles.length - 1; i >= 0; i--) {
                let p = state.particles[i];
                p.x += p.vx * dt;
                p.y += p.vy * dt;
                p.life -= dt;
                if (p.life <= 0) state.particles.splice(i, 1);
            }

            state.cameraY += (state.y - state.cameraY) * 5 * dt;

            document.getElementById('val-alt').innerText = state.y.toFixed(1);
            document.getElementById('val-vel').innerText = Math.sqrt(state.vx*state.vx + state.vy*state.vy).toFixed(1);
        }

        // --- RENDERING ---
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
            ctx.fillStyle = "#ddd";
            ctx.fillRect(x - w/2, y - h/2 + 5, w, 2);
            ctx.fillRect(x - w/2, y + h/2 - 7, w, 2);
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
            ctx.fillStyle = state.mode === "vab" ? "#1e293b" : "#87CEEB";
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            ctx.save();
            ctx.translate(canvas.width / 2, canvas.height * 0.7); 
            
            let zoom = state.mode === "vab" ? 1.5 : Math.max(0.5, 1.5 - (state.y / 50000));
            ctx.scale(zoom, zoom);

            if (state.mode === "vab") {
                // Grid
                ctx.strokeStyle = "rgba(255,255,255,0.05)";
                for(let i=-1000; i<1000; i+=GRID) { ctx.beginPath(); ctx.moveTo(i, -1000); ctx.lineTo(i, 1000); ctx.stroke(); }
                for(let i=-1000; i<1000; i+=GRID) { ctx.beginPath(); ctx.moveTo(-1000, i); ctx.lineTo(1000, i); ctx.stroke(); }

                rocketParts.forEach(p => {
                    let py = -p.y;
                    if (p.type === "pod") drawPod(p.x, py, p.width, p.height);
                    if (p.type === "tank") drawTank(p.x, py, p.width, p.height);
                    if (p.type === "engine") drawEngine(p.x, py, p.width, p.height);
                    if (p.type === "decoupler") drawDecoupler(p.x, py, p.width, p.height);
                });
            } else {
                // Ground
                ctx.fillStyle = "#2e4a2e";
                ctx.fillRect(-10000, 0, 20000, -10000);

                // Particles
                state.particles.forEach(p => {
                    ctx.fillStyle = `rgba(${p.color}, ${p.life})`;
                    ctx.beginPath();
                    ctx.arc(p.x, -p.y + state.cameraY, p.size * p.life, 0, Math.PI * 2);
                    ctx.fill();
                });

                // Rocket
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
