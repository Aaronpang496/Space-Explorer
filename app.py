import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Space Explorer", layout="wide", initial_sidebar_state="collapsed")

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
        
        /* UI LAYER */
        #ui-layer { position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 99999; }
        
        /* START SCREEN */
        #start-screen { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); display: flex; flex-direction: column; justify-content: center; align-items: center; pointer-events: auto; z-index: 1000000; }
        #btn-start { background: #00ffcc; color: #000; border: none; padding: 20px 50px; font-size: 28px; font-weight: bold; border-radius: 10px; cursor: pointer; box-shadow: 0 0 20px #00ffcc; transition: transform 0.1s; }
        #btn-start:active { transform: scale(0.95); }
        .title { color: white; font-size: 48px; font-weight: bold; margin-bottom: 50px; text-shadow: 0 0 20px #4a90e2; text-align: center;}

        /* VAB Menu (Left) */
        #vab-menu { position: absolute; top: 10px; left: 10px; width: 100px; background: rgba(0,0,0,0.85); border: 2px solid #555; border-radius: 10px; display: none; flex-direction: column; align-items: center; padding: 10px 0; pointer-events: auto; max-height: 85vh; overflow-y: auto; z-index: 100000;}
        .part-btn { width: 80px; height: 60px; margin: 4px 0; background: #1a1a1a; border: 2px solid #444; border-radius: 5px; cursor: grab; display: flex; flex-direction: column; justify-content: center; align-items: center; position: relative;}
        .part-btn:active { cursor: grabbing; border-color: #00ffcc; }
        .part-btn span { font-size: 9px; color: #aaa; position: absolute; bottom: 2px;}

        /* CSS Lego Shapes */
        .m-pod { width: 20px; height: 25px; background: #888; border-radius: 5px 5px 0 0; border-bottom: 3px solid #444;}
        .m-nose { width: 20px; height: 20px; background: #fff; clip-path: polygon(50% 0%, 100% 100%, 0% 100%);}
        .m-tank-s { width: 16px; height: 25px; background: #eee; border-left: 2px solid #ccc; border-right: 2px solid #ccc;}
        .m-tank-m { width: 20px; height: 40px; background: #eee; border-left: 2px solid #ccc; border-right: 2px solid #ccc;}
        .m-tank-l { width: 26px; height: 50px; background: #eee; border-left: 2px solid #ccc; border-right: 2px solid #ccc;}
        .m-engine-s { width: 14px; height: 14px; background: #222; clip-path: polygon(20% 0, 80% 0, 100% 100%, 0% 100%);}
        .m-engine-m { width: 20px; height: 18px; background: #222; clip-path: polygon(20% 0, 80% 0, 100% 100%, 0% 100%);}
        .m-engine-l { width: 28px; height: 24px; background: #222; clip-path: polygon(20% 0, 80% 0, 100% 100%, 0% 100%);}
        .m-decoupler { width: 20px; height: 6px; background: #5c3a21;}
        .m-booster { width: 14px; height: 35px; background: #ddd; border-radius: 5px 5px 0 0;}
        .m-strut { width: 6px; height: 30px; background: #666;}

        /* VAB Stats Panel (Right) */
        #vab-stats { position: absolute; top: 10px; right: 10px; width: 150px; background: rgba(0,0,0,0.85); border: 2px solid #555; border-radius: 10px; padding: 15px; color: white; display: none; flex-direction: column; z-index: 100000; pointer-events: none;}
        .stat-row { display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 14px;}
        .stat-val { color: #00ffcc; font-weight: bold;}

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
        
        #btn-stage { position: absolute; bottom: 20px; right: 80px; width: 80px; height: 50px; background: rgba(200, 50, 0, 0.8); border: 2px solid #ffaa00; color: white; border-radius: 5px; font-size: 16px; font-weight: bold; pointer-events: auto; display: none; z-index: 100000;}
    </style>
</head>
<body>
    <canvas id="gameCanvas"></canvas>
    
    <div id="ui-layer">
        <div id="start-screen">
            <div class="title">SPACE EXPLORER</div>
            <button id="btn-start">START BUILDING</button>
        </div>

        <div id="vab-menu">
            <div class="part-btn" data-type="pod"><div class="m-pod"></div><span>Pod</span></div>
            <div class="part-btn" data-type="nose"><div class="m-nose"></div><span>Nose</span></div>
            <div class="part-btn" data-type="tank_small"><div class="m-tank-s"></div><span>Tank S</span></div>
            <div class="part-btn" data-type="tank_med"><div class="m-tank-m"></div><span>Tank M</span></div>
            <div class="part-btn" data-type="tank_large"><div class="m-tank-l"></div><span>Tank L</span></div>
            <div class="part-btn" data-type="decoupler"><div class="m-decoupler"></div><span>Decoupler</span></div>
            <div class="part-btn" data-type="engine_small"><div class="m-engine-s"></div><span>Engine S</span></div>
            <div class="part-btn" data-type="engine_med"><div class="m-engine-m"></div><span>Engine M</span></div>
            <div class="part-btn" data-type="engine_large"><div class="m-engine-l"></div><span>Engine L</span></div>
            <div class="part-btn" data-type="booster"><div class="m-booster"></div><span>Booster</span></div>
            <div class="part-btn" data-type="strut"><div class="m-strut"></div><span>Strut</span></div>
        </div>

        <div id="vab-stats">
            <div class="stat-row"><span>Mass:</span> <span class="stat-val" id="stat-mass">0 kg</span></div>
            <div class="stat-row"><span>Fuel:</span> <span class="stat-val" id="stat-fuel">0 kg</span></div>
            <div class="stat-row"><span>Thrust:</span> <span class="stat-val" id="stat-thrust">0 kN</span></div>
            <div class="stat-row" style="border-top: 1px solid #555; padding-top: 8px; margin-top: 8px;">
                <span>TWR:</span> <span class="stat-val" id="stat-twr" style="color:#ffaa00">0.0</span>
            </div>
        </div>

        <div id="top-bar">
            <button class="top-btn" id="btn-launch">LAUNCH 🚀</button>
            <button class="top-btn" id="btn-reset">RESET 🔄</button>
        </div>

        <div id="hud">
            ALT: <span id="val-alt">0</span> m<br>
            VEL: <span id="val-vel">0</span> m/s<br>
            MASS: <span id="val-mass">0</span> kg
        </div>
        
        <div id="throttle-zone"><div id="throttle-fill"></div></div>
        <div id="arrow-zone">
            <div class="arrow-btn" id="joy-left">◀</div>
            <div class="arrow-btn" id="joy-right">▶</div>
        </div>
        <button id="btn-stage">STAGE</button>
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

        let gameState = "menu"; 
        
        let state = {
            x: 0, y: 0, vx: 0, vy: 0,
            angle: 0, angularVelocity: 0, 
            throttle: 0, 
            currentFuel: 0, maxFuel: 0, dryMass: 0, totalMass: 0,
            cameraY: 0, lastTime: performance.now()
        };

        const GRAVITY = 9.81;
        const GRID = 15;
        let rocketParts = []; 
        
        // --- PART DEFINITIONS (Mass in kg, Fuel in kg, Thrust in kN) ---
        const P = {
            pod:        { w: 30, h: 30, m: 1500, f: 0,   t: 0 },
            nose:       { w: 30, h: 20, m: 200,  f: 0,   t: 0 },
            tank_small: { w: 24, h: 30, m: 500,  f: 1000, t: 0 },
            tank_med:   { w: 30, h: 60, m: 1000, f: 2500, t: 0 },
            tank_large: { w: 45, h: 90, m: 2000, f: 6000, t: 0 },
            decoupler:  { w: 30, h: 8,  m: 100,  f: 0,   t: 0 },
            engine_small:{ w: 18, h: 18, m: 300,  f: 0,   t: 200 },
            engine_med: { w: 24, h: 24, m: 800,  f: 0,   t: 600 },
            engine_large:{ w: 36, h: 36, m: 2000, f: 0,   t: 1500 },
            booster:    { w: 20, h: 50, m: 600,  f: 1500, t: 300 },
            strut:      { w: 10, h: 30, m: 50,   f: 0,   t: 0 }
        };

        const menuPlanets = [
            { color: "#888", dist: 60, size: 3, speed: 0.8, angle: 0 },
            { color: "#e6b800", dist: 90, size: 5, speed: 0.6, angle: 1 },
            { color: "#4a90e2", dist: 120, size: 5.5, speed: 0.5, angle: 2 },
            { color: "#c1440e", dist: 150, size: 4, speed: 0.4, angle: 3 },
            { color: "#d4a373", dist: 210, size: 12, speed: 0.2, angle: 4 },
            { color: "#e3d5a1", dist: 270, size: 10, speed: 0.15, angle: 5, ring: true },
            { color: "#b2e3e6", dist: 330, size: 8, speed: 0.1, angle: 6 },
            { color: "#3b5bdb", dist: 380, size: 7.5, speed: 0.08, angle: 7 }
        ];

        document.getElementById('btn-start').onclick = function() {
            gameState = "vab";
            document.getElementById('start-screen').style.display = 'none';
            document.getElementById('vab-menu').style.display = 'flex';
            document.getElementById('top-bar').style.display = 'flex';
            document.getElementById('vab-stats').style.display = 'flex';
            
            rocketParts = [];
            addPart("engine_med", 0, 12);
            addPart("tank_med", 0, 54);
            addPart("tank_med", 0, 114);
            addPart("pod", 0, 159);
        };

        // --- STATS CALCULATION ---
        function updateStats() {
            let mass = 0;
            let fuel = 0;
            let thrust = 0;

            rocketParts.forEach(p => {
                const part = P[p.type];
                mass += part.m;
                fuel += part.f;
                thrust += part.t;
            });

            // Add fuel to total mass
            const totalMass = mass + fuel;
            const twr = thrust > 0 ? (thrust * 1000) / (totalMass * GRAVITY) : 0;

            document.getElementById('stat-mass').innerText = totalMass.toLocaleString() + " kg";
            document.getElementById('stat-fuel').innerText = fuel.toLocaleString() + " kg";
            document.getElementById('stat-thrust').innerText = thrust.toLocaleString() + " kN";
            document.getElementById('stat-twr').innerText = twr.toFixed(2);
        }

        // --- DRAG AND DROP ---
        let draggedPart = null;
        let dragGhost = null;

        document.querySelectorAll('.part-btn').forEach(item => {
            item.addEventListener('pointerdown', (e) => {
                if (gameState !== "vab") return;
                draggedPart = item.dataset.type;
                
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

                    let snapX = Math.round(worldX / GRID) * GRID;
                    let snapY = Math.round(worldY / GRID) * GRID;
                    let minDist = 45; 

                    if (rocketParts.length > 0) {
                        rocketParts.forEach(p => {
                            let pw = P[p.type].w;
                            let ph = P[p.type].h;
                            let nw = P[draggedPart].w;
                            let nh = P[draggedPart].h;

                            let dTop = Math.hypot(worldX - p.x, worldY - (p.y + ph/2));
                            if (dTop < minDist) { minDist = dTop; snapX = p.x; snapY = p.y + ph/2 + nh/2; }

                            let dBot = Math.hypot(worldX - p.x, worldY - (p.y - ph/2));
                            if (dBot < minDist) { minDist = dBot; snapX = p.x; snapY = p.y - ph/2 - nh/2; }

                            let dRight = Math.hypot(worldX - (p.x + pw/2), worldY - p.y);
                            if (dRight < minDist) { minDist = dRight; snapX = p.x + pw/2 + nw/2; snapY = p.y; }

                            let dLeft = Math.hypot(worldX - (p.x - pw/2), worldY - p.y);
                            if (dLeft < minDist) { minDist = dLeft; snapX = p.x - pw/2 - nw/2; snapY = p.y; }
                        });
                    }

                    addPart(draggedPart, snapX, snapY);
                    updateStats();
                }
                draggedPart = null;
            }
        });

        function addPart(type, x, y) {
            rocketParts.push({ type, x, y, id: Date.now() + Math.random() });
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

        // --- STAGING LOGIC ---
        document.getElementById('btn-stage').onclick = function() {
            // Find all decouplers
            let decouplers = rocketParts.filter(p => p.type === 'decoupler');
            if (decouplers.length === 0) return; // Nothing to stage

            // Sort by Y position (lowest first)
            decouplers.sort((a, b) => a.y - b.y);
            let lowestDecoupler = decouplers[0];

            // Find parts to drop (everything below the decoupler, or side boosters attached via decouplers)
            let partsToKeep = [];
            let partsToDrop = [];

            rocketParts.forEach(p => {
                if (p.y < lowestDecoupler.y) {
                    partsToDrop.push(p); // Everything below drops
                } else {
                    // Check if it's a side booster attached via decoupler
                    let isSideDrop = false;
                    if (p.type === 'booster' || p.type === 'tank_small') {
                        if (Math.abs(p.x) > 20 && p.y <= lowestDecoupler.y + 50) {
                            isSideDrop = true;
                        }
                    }
                    if (isSideDrop) partsToDrop.push(p);
                    else partsToKeep.push(p);
                }
            });

            // Also drop the decoupler itself
            partsToDrop.push(lowestDecoupler);

            rocketParts = partsToKeep;
            updateStats();
            
            // Visual effect (fake explosion of parts)
            alert("STAGE SEPARATED!");
        };

        // --- LAUNCH ---
        document.getElementById('btn-launch').onclick = function() {
            if (gameState === "vab") {
                let minX = 9999, maxX = -9999, minY = 9999;
                rocketParts.forEach(p => {
                    let pw = P[p.type].w, ph = P[p.type].h;
                    if (p.x - pw/2 < minX) minX = p.x - pw/2;
                    if (p.x + pw/2 > maxX) maxX = p.x + pw/2;
                    if (p.y - ph/2 < minY) minY = p.y - ph/2;
                });
                let offsetX = (minX + maxX) / 2;
                rocketParts.forEach(p => { p.x -= offsetX; p.y -= minY; });

                gameState = "flight";
                document.getElementById('vab-menu').style.display = 'none';
                document.getElementById('vab-stats').style.display = 'none';
                this.style.display = 'none';
                document.getElementById('hud').style.display = 'block';
                document.getElementById('throttle-zone').style.display = 'block';
                document.getElementById('arrow-zone').style.display = 'flex';
                document.getElementById('btn-stage').style.display = 'block';

                // Init flight state
                let initialStats = { m: 0, f: 0 };
                rocketParts.forEach(p => { initialStats.m += P[p.type].m; initialStats.f += P[p.type].f; });
                state.dryMass = initialStats.m;
                state.maxFuel = initialStats.f;
                state.currentFuel = initialStats.f;
                state.totalMass = state.dryMass + state.currentFuel;
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

            let thrust = 0;
            rocketParts.forEach(p => thrust += P[p.type].t);

            // Recalculate mass based on current fuel
            state.totalMass = state.dryMass + state.currentFuel;

            let ay = -GRAVITY;
            let ax = 0;

            if (state.throttle > 0 && state.currentFuel > 0 && thrust > 0) {
                let thrustAccel = (thrust * 1000 * state.throttle) / state.totalMass;
                let rad = state.angle * (Math.PI / 180);
                ax += thrustAccel * Math.sin(rad);
                ay += thrustAccel * Math.cos(rad);
                
                state.currentFuel -= 50 * state.throttle * dt; 
                if (state.currentFuel < 0) state.currentFuel = 0;
            }

            state.vx += ax * dt;
            state.vy += ay * dt;
            state.x += state.vx * dt;
            state.y += state.vy * dt;

            if (state.y < 0) {
                state.y = 0;
                if (Math.abs(state.vy) > 5) {
                    gameState = "crashed";
                    document.getElementById('hud').innerText = "CRASHED";
                } else {
                    state.vy = 0; state.vx = 0; state.throttle = 0;
                    document.getElementById('hud').innerText = "LANDED";
                }
            }

            state.cameraY += (state.y - state.cameraY) * 5 * dt;

            document.getElementById('val-alt').innerText = state.y.toFixed(1);
            document.getElementById('val-vel').innerText = Math.sqrt(state.vx*state.vx + state.vy*state.vy).toFixed(1);
            document.getElementById('val-mass').innerText = state.totalMass.toFixed(0);
        }

        // --- DRAWING ---
        function drawMenu(dt) {
            ctx.fillStyle = "#000511";
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            const cx = canvas.width / 2; const cy = canvas.height / 2;

            ctx.fillStyle = "#ffdd00";
            ctx.beginPath(); ctx.arc(cx, cy, 30, 0, Math.PI * 2); ctx.fill();
            ctx.shadowColor = "#ffdd00"; ctx.shadowBlur = 50; ctx.fill(); ctx.shadowBlur = 0; 

            menuPlanets.forEach(p => {
                p.angle += p.speed * dt;
                ctx.strokeStyle = "rgba(255,255,255,0.1)";
                ctx.beginPath(); ctx.arc(cx, cy, p.dist, 0, Math.PI * 2); ctx.stroke();

                let px = cx + Math.cos(p.angle) * p.dist;
                let py = cy + Math.sin(p.angle) * p.dist;
                ctx.fillStyle = p.color;
                ctx.beginPath(); ctx.arc(px, py, p.size, 0, Math.PI * 2); ctx.fill();

                if (p.ring) {
                    ctx.strokeStyle = "rgba(227, 213, 161, 0.6)"; ctx.lineWidth = 3;
                    ctx.beginPath(); ctx.ellipse(px, py, p.size * 2, p.size * 0.5, Math.PI/4, 0, Math.PI * 2); ctx.stroke();
                }
            });
        }

        function drawPart(p, py) {
            const x = p.x, y = py, w = P[p.type].w, h = P[p.type].h;
            if (p.type === "pod") {
                ctx.fillStyle = "#888"; ctx.beginPath(); ctx.moveTo(x-w/2,y+h/2); ctx.lineTo(x+w/2,y+h/2); ctx.lineTo(x+w/3,y-h/2); ctx.lineTo(x-w/3,y-h/2); ctx.fill();
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
            } else if (p.type === "strut") {
                ctx.fillStyle = "#666"; ctx.fillRect(x-w/2, y-h/2, w, h);
            } else if (p.type === "decoupler") {
                ctx.fillStyle = "#5c3a21"; ctx.fillRect(x-w/2, y-h/2, w, h);
            }
        }

        function draw() {
            if (gameState === "menu") return; 

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
