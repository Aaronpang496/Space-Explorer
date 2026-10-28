import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="SFS Clone", layout="wide", initial_sidebar_state="collapsed")

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
        
        /* UI LAYER */
        #ui-layer { position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 99999; }
        
        /* START SCREEN OVERLAY */
        #start-screen { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); display: flex; flex-direction: column; justify-content: center; align-items: center; pointer-events: auto; z-index: 1000000; }
        #btn-start { background: #00ffcc; color: #000; border: none; padding: 20px 50px; font-size: 28px; font-weight: bold; border-radius: 10px; cursor: pointer; box-shadow: 0 0 20px #00ffcc; transition: transform 0.1s; }
        #btn-start:active { transform: scale(0.95); }
        .title { color: white; font-size: 48px; font-weight: bold; margin-bottom: 50px; text-shadow: 0 0 20px #4a90e2; }

        /* VAB MENU */
        #vab-menu { position: absolute; top: 10px; left: 10px; width: 90px; background: rgba(0,0,0,0.85); border: 2px solid #555; border-radius: 10px; display: none; flex-direction: column; align-items: center; padding: 10px 0; pointer-events: auto; max-height: 90vh; overflow-y: auto; z-index: 100000;}
        .part-btn { width: 70px; height: 60px; margin: 4px 0; background: #222; border: 2px solid #555; border-radius: 5px; color: white; font-size: 10px; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; cursor: grab;}
        .part-btn:active { cursor: grabbing; border-color: #00ffcc; }
        
        /* Top Bar */
        #top-bar { position: absolute; top: 15px; left: 50%; transform: translateX(-50%); display: none; gap: 10px; pointer-events: auto; z-index: 100000;}
        .top-btn { background: #1e3a8a; color: white; border: 2px solid #60a5fa; padding: 10px 20px; font-size: 16px; font-weight: bold; border-radius: 5px; cursor: pointer;}
        
        /* Flight HUD */
        #hud { position: absolute; top: 15px; right: 15px; color: #fff; font-size: 14px; background: rgba(0,0,0,0.6); padding: 10px; border-radius: 5px; text-align: right; border-left: 3px solid #00ffcc; display: none; z-index: 100000;}
        
        /* Flight Controls */
        #throttle-zone { position: absolute; right: 20px; bottom: 80px; width: 40px; height: 180px; background: rgba(0,0,0,0.5); border: 2px solid #fff; border-radius: 20px; pointer-events: auto; display: none; z-index: 100000; }
        #throttle-fill { position: absolute; bottom: 0; width: 100%; height: 0%; background: #ffaa00; border-radius: 18px;}
        
        #arrow-zone { position: absolute; left: 20px; bottom: 20px; display: none; gap: 20px; pointer-events: auto; z-index: 100000;}
        .arrow-btn { width: 60px; height: 80px; background: rgba(0,0,0,0.5); border: 2px solid #fff; border-radius: 10px; color: white; font-size: 30px; display: flex; justify-content: center; align-items: center; cursor: pointer;}
        
        #btn-legs { position: absolute; bottom: 80px; right: 80px; width: 80px; height: 40px; background: rgba(0,0,0,0.5); border: 2px solid #fff; color: white; border-radius: 5px; font-size: 12px; font-weight: bold; pointer-events: auto; display: none; z-index: 100000;}
        #btn-legs.deployed { border-color: #00ffcc; color: #00ffcc; }
    </style>
</head>
<body>
    <canvas id="gameCanvas"></canvas>
    
    <div id="ui-layer">
        <!-- START SCREEN -->
        <div id="start-screen">
            <div class="title">SPACEFLIGHT SIMULATOR</div>
            <button id="btn-start">START GAME</button>
        </div>

        <!-- VAB Menu -->
        <div id="vab-menu">
            <div class="part-btn" data-type="pod"><span>Pod</span></div>
            <div class="part-btn" data-type="nose"><span>Nose</span></div>
            <div class="part-btn" data-type="tank_small"><span>Tank S</span></div>
            <div class="part-btn" data-type="tank_med"><span>Tank M</span></div>
            <div class="part-btn" data-type="tank_large"><span>Tank L</span></div>
            <div class="part-btn" data-type="decoupler"><span>Decoupler</span></div>
            <div class="part-btn" data-type="engine_small"><span>Engine S</span></div>
            <div class="part-btn" data-type="engine_med"><span>Engine M</span></div>
            <div class="part-btn" data-type="engine_large"><span>Engine L</span></div>
            <div class="part-btn" data-type="booster"><span>Booster</span></div>
        </div>

        <div id="top-bar">
            <button class="top-btn" id="btn-launch">LAUNCH 🚀</button>
            <button class="top-btn" id="btn-reset">RESET 🔄</button>
        </div>

        <div id="hud">
            ALT: <span id="val-alt">0</span> m<br>
            VEL: <span id="val-vel">0</span> m/s
        </div>
        
        <div id="throttle-zone"><div id="throttle-fill"></div></div>
        <div id="arrow-zone">
            <div class="arrow-btn" id="joy-left">◀</div>
            <div class="arrow-btn" id="joy-right">▶</div>
        </div>
        <button id="btn-legs">LEGS: UP</button>
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
        let gameState = "menu"; // "menu", "vab", "flight"
        
        let state = {
            x: 0, y: 0, vx: 0, vy: 0,
            angle: 0, angularVelocity: 0, 
            throttle: 0, fuel: 100,
            legsDeployed: false,
            cameraY: 0,
            lastTime: performance.now()
        };

        const GRAVITY = 9.81;
        const GRID = 15;
        let rocketParts = []; 
        
        // --- MENU PLANETS (8 Planets) ---
        const menuPlanets = [
            { name: "Mercury", color: "#888", dist: 60, size: 3, speed: 0.8, angle: 0 },
            { name: "Venus", color: "#e6b800", dist: 90, size: 5, speed: 0.6, angle: 1 },
            { name: "Earth", color: "#4a90e2", dist: 120, size: 5.5, speed: 0.5, angle: 2 },
            { name: "Mars", color: "#c1440e", dist: 150, size: 4, speed: 0.4, angle: 3 },
            { name: "Jupiter", color: "#d4a373", dist: 210, size: 12, speed: 0.2, angle: 4 },
            { name: "Saturn", color: "#e3d5a1", dist: 270, size: 10, speed: 0.15, angle: 5 },
            { name: "Uranus", color: "#b2e3e6", dist: 330, size: 8, speed: 0.1, angle: 6 },
            { name: "Neptune", color: "#3b5bdb", dist: 380, size: 7.5, speed: 0.08, angle: 7 }
        ];

        // --- PART DEFINITIONS ---
        const P = {
            pod:        { w: 30, h: 30 },
            nose:       { w: 30, h: 20 },
            tank_small: { w: 24, h: 30 },
            tank_med:   { w: 30, h: 60 },
            tank_large: { w: 45, h: 90 },
            decoupler:  { w: 30, h: 8 },
            engine_small:{ w: 18, h: 18 },
            engine_med: { w: 24, h: 24 },
            engine_large:{ w: 36, h: 36 },
            booster:    { w: 20, h: 50 }
        };

        // --- START BUTTON LOGIC ---
        document.getElementById('btn-start').onclick = function() {
            gameState = "vab";
            document.getElementById('start-screen').style.display = 'none';
            document.getElementById('vab-menu').style.display = 'flex';
            document.getElementById('top-bar').style.display = 'flex';
            
            // Build default rocket
            rocketParts = [];
            addPart("engine_med", 0, 12);
            addPart("tank_med", 0, 54);
            addPart("tank_med", 0, 114);
            addPart("pod", 0, 159);
        };

        // --- DRAG AND DROP SYSTEM ---
        let draggedPart = null;
        let dragGhost = null;

        document.querySelectorAll('.part-btn').forEach(item => {
            item.addEventListener('pointerdown', (e) => {
                if (gameState !== "vab") return;
                draggedPart = item.dataset.type;
                
                // Create a ghost element to follow the finger
                dragGhost = document.createElement('div');
                dragGhost.style.position = 'absolute';
                dragGhost.style.width = P[draggedPart].w + 'px';
                dragGhost.style.height = P[draggedPart].h + 'px';
                dragGhost.style.backgroundColor = draggedPart.includes('tank') ? '#fff' : (draggedPart.includes('engine') ? '#222' : '#888');
                dragGhost.style.border = '2px dashed #00ffcc';
                dragGhost.style.pointerEvents = 'none';
                dragGhost.style.zIndex = 999999;
                document.body.appendChild(dragGhost);
            });
        });

        window.addEventListener('pointermove', (e) => {
            if (dragGhost && draggedPart) {
                dragGhost.style.left = (e.clientX - P[draggedPart].w/2) + 'px';
                dragGhost.style.top = (e.clientY - P[draggedPart].h/2) + 'px';
            }
        });

        window.addEventListener('pointerup', (e) => {
            if (draggedPart) {
                if (dragGhost) document.body.removeChild(dragGhost);
                dragGhost = null;

                if (e.target === canvas && gameState === "vab") {
                    const rect = canvas.getBoundingClientRect();
                    let mouseX = e.clientX - rect.left;
                    let mouseY = e.clientY - rect.top;

                    let worldX = (mouseX - canvas.width/2) / 1.2;
                    let worldY = (canvas.height * 0.8 - mouseY) / 1.2;

                    worldX = Math.round(worldX / GRID) * GRID;
                    worldY = Math.round(worldY / GRID) * GRID;

                    // MAGNETIC SNAPPING
                    let snapX = worldX;
                    let snapY = worldY;

                    if (rocketParts.length > 0) {
                        let minDist = 999;
                        rocketParts.forEach(p => {
                            let topY = p.y + P[p.type].h/2;
                            let dTop = Math.hypot(worldX - p.x, worldY - topY);
                            if (dTop < minDist) { minDist = dTop; snapX = p.x; snapY = topY + P[draggedPart].h/2; }

                            let botY = p.y - P[p.type].h/2;
                            let dBot = Math.hypot(worldX - p.x, worldY - botY);
                            if (dBot < minDist) { minDist = dBot; snapX = p.x; snapY = botY - P[draggedPart].h/2; }
                        });
                    }
                    addPart(draggedPart, snapX, snapY);
                }
                draggedPart = null;
            }
        });

        function addPart(type, x, y) {
            rocketParts.push({ type, x, y });
        }

        // --- FLIGHT CONTROLS ---
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

        document.getElementById('btn-legs').onclick = function() {
            state.legsDeployed = !state.legsDeployed;
            this.innerText = state.legsDeployed ? "LEGS: DOWN" : "LEGS: UP";
            if(state.legsDeployed) this.classList.add('deployed');
            else this.classList.remove('deployed');
        };

        // --- LAUNCH ---
        document.getElementById('btn-launch').onclick = function() {
            if (gameState === "vab") {
                let minX = 9999, maxX = -9999, minY = 9999;
                rocketParts.forEach(p => {
                    if (p.x - P[p.type].w/2 < minX) minX = p.x - P[p.type].w/2;
                    if (p.x + P[p.type].w/2 > maxX) maxX = p.x + P[p.type].w/2;
                    if (p.y - P[p.type].h/2 < minY) minY = p.y - P[p.type].h/2;
                });
                let offsetX = (minX + maxX) / 2;
                rocketParts.forEach(p => { p.x -= offsetX; p.y -= minY; });

                gameState = "flight";
                document.getElementById('vab-menu').style.display = 'none';
                this.style.display = 'none';
                document.getElementById('hud').style.display = 'block';
                document.getElementById('throttle-zone').style.display = 'block';
                document.getElementById('arrow-zone').style.display = 'flex';
                document.getElementById('btn-legs').style.display = 'block';
            }
        };

        document.getElementById('btn-reset').onclick = () => window.location.reload();

        // --- PHYSICS ---
        function updatePhysics(dt) {
            if (gameState !== "flight") return;

            if (leftPressed) state.angularVelocity -= 1.5 * dt;
            if (rightPressed) state.angularVelocity += 1.5 * dt;
            if (!leftPressed && !rightPressed) state.angularVelocity *= 0.95;
            state.angle += state.angularVelocity;

            let ay = -GRAVITY;
            let ax = 0;
            let hasEngine = rocketParts.some(p => p.type.includes("engine") || p.type === "booster");

            if (state.throttle > 0 && state.fuel > 0 && hasEngine) {
                let thrustAccel = 30 * state.throttle;
                let rad = state.angle * (Math.PI / 180);
                ax += thrustAccel * Math.sin(rad);
                ay += thrustAccel * Math.cos(rad);
                state.fuel -= 5 * state.throttle * dt;
            }

            state.vx += ax * dt;
            state.vy += ay * dt;
            state.x += state.vx * dt;
            state.y += state.vy * dt;

            if (state.y < 0) {
                state.y = 0;
                if (Math.abs(state.vy) > 5 || !state.legsDeployed) {
                    gameState = "crashed";
                    document.getElementById('hud').innerText = "CRASHED";
                } else {
                    state.vy = 0; state.vx = 0; state.throttle = 0;
                    document.getElementById('hud').innerText = "LANDED SAFELY";
                }
            }

            state.cameraY += (state.y - state.cameraY) * 5 * dt;
        }

        // --- DRAWING ---
        function drawMenu(dt) {
            // Black space background
            ctx.fillStyle = "#000511";
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            const cx = canvas.width / 2;
            const cy = canvas.height / 2;

            // Sun
            ctx.fillStyle = "#ffdd00";
            ctx.beginPath();
            ctx.arc(cx, cy, 30, 0, Math.PI * 2);
            ctx.fill();
            ctx.shadowColor = "#ffdd00";
            ctx.shadowBlur = 50;
            ctx.fill();
            ctx.shadowBlur = 0; // Reset

            // Planets
            menuPlanets.forEach(p => {
                p.angle += p.speed * dt;

                // Orbit line
                ctx.strokeStyle = "rgba(255,255,255,0.1)";
                ctx.beginPath();
                ctx.arc(cx, cy, p.dist, 0, Math.PI * 2);
                ctx.stroke();

                // Planet position
                let px = cx + Math.cos(p.angle) * p.dist;
                let py = cy + Math.sin(p.angle) * p.dist;

                // Draw Planet
                ctx.fillStyle = p.color;
                ctx.beginPath();
                ctx.arc(px, py, p.size, 0, Math.PI * 2);
                ctx.fill();

                // Saturn's Ring
                if (p.name === "Saturn") {
                    ctx.strokeStyle = "rgba(227, 213, 161, 0.6)";
                    ctx.lineWidth = 3;
                    ctx.beginPath();
                    ctx.ellipse(px, py, p.size * 2, p.size * 0.5, Math.PI/4, 0, Math.PI * 2);
                    ctx.stroke();
                }
            });
        }

        function drawPart(p, py) {
            const x = p.x, y = py, w = P[p.type].w, h = P[p.type].h;
            if (p.type === "pod") {
                ctx.fillStyle = "#888"; ctx.beginPath(); ctx.moveTo(x-w/2,y+h/2); ctx.lineTo(x+w/2,y+h/2); ctx.lineTo(x+w/3,y-h/2); ctx.lineTo(x-w/3,y-h/2); ctx.fill();
                // Window
                ctx.fillStyle = "#222"; ctx.beginPath(); ctx.arc(x, y, w/4, 0, Math.PI*2); ctx.fill();
            } else if (p.type === "nose") {
                ctx.fillStyle = "#fff"; ctx.beginPath(); ctx.moveTo(x-w/2,y+h/2); ctx.lineTo(x+w/2,y+h/2); ctx.lineTo(x,y-h/2); ctx.fill();
            } else if (p.type.includes("tank")) {
                let grad = ctx.createLinearGradient(x-w/2,0,x+w/2,0); grad.addColorStop(0,"#aaa"); grad.addColorStop(0.5,"#fff"); grad.addColorStop(1,"#888");
                ctx.fillStyle = grad; ctx.fillRect(x-w/2, y-h/2, w, h);
            } else if (p.type.includes("engine")) {
                ctx.fillStyle = "#222"; ctx.beginPath(); ctx.moveTo(x-w/3,y-h/2); ctx.lineTo(x+w/3,y-h/2); ctx.lineTo(x+w/2,y+h/2); ctx.lineTo(x-w/2,y+h/2); ctx.fill();
            } else if (p.type === "booster") {
                ctx.fillStyle = "#ddd"; ctx.fillRect(x-w/2, y-h/2, w, h);
            }
        }

        function draw() {
            if (gameState === "menu") return; // Menu is drawn separately

            ctx.fillStyle = gameState === "vab" ? "#2b3a4a" : "#87CEEB";
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            ctx.save();
            ctx.translate(canvas.width/2, canvas.height*0.8);
            let zoom = gameState === "vab" ? 1.2 : Math.max(0.5, 1.2 - (state.y/50000));
            ctx.scale(zoom, zoom);

            if (gameState === "vab") {
                ctx.strokeStyle = "rgba(255,255,255,0.1)";
                for(let i=-1000;i<1000;i+=GRID){ctx.beginPath();ctx.moveTo(i,-1000);ctx.lineTo(i,1000);ctx.stroke();ctx.beginPath();ctx.moveTo(-1000,i);ctx.lineTo(1000,i);ctx.stroke();}
                rocketParts.forEach(p => drawPart(p, -p.y));
            } else {
                ctx.fillStyle = "#4a3b2c"; ctx.fillRect(-10000, 0, 20000, -10000);
                ctx.translate(state.x, -state.cameraY);
                ctx.rotate(state.angle * (Math.PI/180));
                rocketParts.forEach(p => drawPart(p, -p.y));
            }
            ctx.restore();
        }

        function loop(time) {
            let dt = (time - state.lastTime) / 1000;
            state.lastTime = time;
            if (dt > 0.1) dt = 0.1;

            if (gameState === "menu") {
                drawMenu(dt);
            } else {
                updatePhysics(dt);
                draw();
            }
            requestAnimationFrame(loop);
        }
        requestAnimationFrame(loop);
    </script>
</body>
</html>
"""

components.html(game_html, height=900, scrolling=False)
