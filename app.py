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
        #ui-layer { position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 99999; }
        
        /* START SCREEN */
        #start-screen { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); display: flex; flex-direction: column; justify-content: center; align-items: center; pointer-events: auto; z-index: 1000000; }
        #btn-start { background: #00ffcc; color: #000; border: none; padding: 20px 50px; font-size: 28px; font-weight: bold; border-radius: 10px; cursor: pointer; box-shadow: 0 0 20px #00ffcc; }
        .title { color: white; font-size: 48px; font-weight: bold; margin-bottom: 50px; text-shadow: 0 0 20px #4a90e2; }

        /* VAB Menu */
        #vab-menu { position: absolute; top: 10px; left: 10px; width: 120px; background: rgba(0,0,0,0.85); border: 2px solid #555; border-radius: 10px; display: none; flex-direction: column; align-items: center; padding: 10px 0; pointer-events: auto; max-height: 85vh; overflow-y: auto; z-index: 100000;}
        .part-btn { width: 100px; height: 50px; margin: 4px 0; background: #1a1a1a; border: 2px solid #444; border-radius: 5px; cursor: pointer; display: flex; flex-direction: row; justify-content: space-around; align-items: center; color: white; font-size: 12px; font-weight: bold;}
        .part-btn.active { border-color: #00ffcc; background: #114444; }
        
        /* CSS Lego Shapes (Accurate Proportions) */
        .m-pod { width: 20px; height: 20px; background: #888; clip-path: polygon(20% 0%, 80% 0%, 100% 100%, 0% 100%);}
        .m-tank-s { width: 20px; height: 20px; background: #eee; border-left: 2px solid #ccc; border-right: 2px solid #ccc;}
        .m-tank-m { width: 20px; height: 30px; background: #eee; border-left: 2px solid #ccc; border-right: 2px solid #ccc;}
        .m-engine { width: 20px; height: 15px; background: #222; clip-path: polygon(20% 0%, 80% 0%, 100% 100%, 0% 100%);}

        /* VAB Stats */
        #vab-stats { position: absolute; top: 10px; right: 10px; width: 160px; background: rgba(0,0,0,0.85); border: 2px solid #555; border-radius: 10px; padding: 15px; color: white; display: none; flex-direction: column; z-index: 100000; pointer-events: none;}
        .stat-row { display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 13px;}
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
        #btn-legs { position: absolute; bottom: 80px; right: 80px; width: 80px; height: 40px; background: rgba(0,0,0,0.5); border: 2px solid #fff; color: white; border-radius: 5px; font-size: 12px; font-weight: bold; pointer-events: auto; display: none; z-index: 100000;}
        #btn-legs.deployed { border-color: #00ffcc; color: #00ffcc; }
        #btn-map { position: absolute; top: 15px; left: 15px; width: 60px; height: 40px; background: rgba(0,0,0,0.5); border: 2px solid #fff; color: white; border-radius: 5px; font-size: 12px; font-weight: bold; pointer-events: auto; display: none; z-index: 100000;}

        /* Minimap */
        #minimap-container { position: absolute; top: 120px; right: 15px; width: 100px; height: 100px; border: 2px solid #555; border-radius: 50%; background: rgba(0,0,0,0.8); overflow: hidden; display: none; z-index: 100000;}
        
        /* Transport Map Overlay */
        #map-overlay { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 5, 15, 0.95); display: none; pointer-events: auto; z-index: 200000;}
        #map-canvas { position: absolute; top: 0; left: 0; width: 100%; height: 100%; }
        #map-title { position: absolute; top: 20px; left: 20px; color: white; font-size: 24px; font-weight: bold;}

        /* Status Message */
        #status-msg { position: absolute; top: 40%; left: 50%; transform: translate(-50%, -50%); font-size: 40px; font-weight: bold; text-align: center; display: none; text-shadow: 2px 2px 5px #000; pointer-events: none; z-index: 1000000;}
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
            <div class="part-btn active" data-type="pod"><div class="m-pod"></div><span>Pod</span></div>
            <div class="part-btn" data-type="tank_small"><div class="m-tank-s"></div><span>Tank S</span></div>
            <div class="part-btn" data-type="tank_med"><div class="m-tank-m"></div><span>Tank M</span></div>
            <div class="part-btn" data-type="engine"><div class="m-engine"></div><span>Engine</span></div>
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

        <button id="btn-map">MAP</button>
        <div id="minimap-container"><canvas id="minimap" width="100" height="100"></canvas></div>

        <div id="hud">
            ALT: <span id="val-alt">0</span> m<br>
            VEL: <span id="val-vel">0</span> m/s<br>
            MASS: <span id="val-mass">0</span> kg<br>
            FUEL: <span id="val-fuel" style="color:#00ffcc">100</span>%
        </div>
        
        <div id="throttle-zone"><div id="throttle-fill"></div></div>
        <div id="arrow-zone">
            <div class="arrow-btn" id="joy-left">◀</div>
            <div class="arrow-btn" id="joy-right">▶</div>
        </div>
        <button id="btn-stage">STAGE</button>
        <button id="btn-legs">LEGS: DOWN</button>

        <div id="status-msg"></div>
    </div>

    <div id="map-overlay">
        <canvas id="map-canvas"></canvas>
        <div id="map-title">SOLAR SYSTEM MAP</div>
    </div>

    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const mapCanvas = document.getElementById('map-canvas');
        const mapCtx = mapCanvas.getContext('2d');
        const minimapCanvas = document.getElementById('minimap');
        const minimapCtx = minimapCanvas.getContext('2d');
        
        function resize() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
            mapCanvas.width = window.innerWidth;
            mapCanvas.height = window.innerHeight;
        }
        window.addEventListener('resize', resize);
        resize();

        let gameState = "menu"; 
        
        let state = {
            x: 0, y: 0, vx: 0, vy: 0, 
            angle: 0, angularVelocity: 0, 
            throttle: 0, 
            currentFuel: 0, maxFuel: 0, dryMass: 0, totalMass: 0,
            legsDeployed: true, 
            cameraY: 0, lastTime: performance.now(),
            particles: [],
            shake: 0, 
            landedMsgTimer: 0
        };

        const GRAVITY = 9.81;
        const GRID = 10;
        let rocketParts = []; 
        let currentSelectedPart = "pod";
        
        // Perfectly aligned sizes (Width is all 20 so they stack perfectly)
        const P = {
            pod:         { w: 20, h: 20, m: 1500, f: 0,    t: 0 },
            tank_small:  { w: 20, h: 30, m: 500,  f: 1000, t: 0 },
            tank_med:    { w: 20, h: 60, m: 1000, f: 3000, t: 0 },
            engine:      { w: 20, h: 20, m: 800,  f: 0,    t: 800 }
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
            addPart("engine", 0, 10);
            addPart("tank_med", 0, 50);
            addPart("tank_med", 0, 110);
            addPart("pod", 0, 140);
            updateStats();
        };

        function updateStats() {
            let mass = 0, fuel = 0, thrust = 0;
            rocketParts.forEach(p => {
                mass += P[p.type].m; fuel += P[p.type].f; thrust += P[p.type].t;
            });
            const totalMass = mass + fuel;
            const twr = thrust > 0 ? (thrust * 1000) / (totalMass * GRAVITY) : 0;
            document.getElementById('stat-mass').innerText = totalMass.toLocaleString() + " kg";
            document.getElementById('stat-fuel').innerText = fuel.toLocaleString() + " kg";
            document.getElementById('stat-thrust').innerText = thrust.toLocaleString() + " kN";
            document.getElementById('stat-twr').innerText = twr.toFixed(2);
        }

        // --- CLICK TO PLACE ---
        document.querySelectorAll('.part-btn').forEach(item => {
            item.addEventListener('pointerdown', (e) => {
                if (gameState !== "vab") return;
                document.querySelectorAll('.part-btn').forEach(b => b.classList.remove('active'));
                item.classList.add('active');
                currentSelectedPart = item.dataset.type;
            });
        });

        canvas.addEventListener('pointerdown', (e) => {
            if (gameState !== "vab") return;
            
            const rect = canvas.getBoundingClientRect();
            let mouseX = e.clientX - rect.left;
            let mouseY = e.clientY - rect.top;
            let worldX = (mouseX - canvas.width/2) / 1.2;
            let worldY = (canvas.height * 0.8 - mouseY) / 1.2;

            let snapX = Math.round(worldX / GRID) * GRID;
            let snapY = Math.round(worldY / GRID) * GRID;
            let minDist = 35; 

            let nw = P[currentSelectedPart].w;
            let nh = P[currentSelectedPart].h;

            if (rocketParts.length > 0) {
                rocketParts.forEach(p => {
                    let pw = P[p.type].w;
                    let ph = P[p.type].h;

                    // Snap Top
                    let dTop = Math.hypot(worldX - p.x, worldY - (p.y + ph/2));
                    if (dTop < minDist) { minDist = dTop; snapX = p.x; snapY = p.y + ph/2 + nh/2; }

                    // Snap Bottom
                    let dBot = Math.hypot(worldX - p.x, worldY - (p.y - ph/2));
                    if (dBot < minDist) { minDist = dBot; snapX = p.x; snapY = p.y - ph/2 - nh/2; }
                });
            }
            addPart(currentSelectedPart, snapX, snapY);
            updateStats();
        });

        function addPart(type, x, y) {
            rocketParts.push({ type, x, y });
        }

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

        // MAP LOGIC
        const mapOverlay = document.getElementById('map-overlay');
        const planetsMap = [
            { name: "Earth", color: "#4a90e2", x: 0.3 },
            { name: "Moon", color: "#9ca3af", x: 0.4 },
            { name: "Mars", color: "#ea580c", x: 0.5 },
            { name: "Jupiter", color: "#d4a373", x: 0.6 },
            { name: "Saturn", color: "#e3d5a1", x: 0.7 },
            { name: "Uranus", color: "#b2e3e6", x: 0.8 },
            { name: "Neptune", color: "#3b5bdb", x: 0.9 }
        ];

        document.getElementById('btn-map').onclick = () => {
            if (gameState !== "flight") return;
            mapOverlay.style.display = 'block';
            mapCtx.fillStyle = "#000511";
            mapCtx.fillRect(0, 0, mapCanvas.width, mapCanvas.height);
            
            planetsMap.forEach(p => {
                mapCtx.fillStyle = p.color;
                mapCtx.beginPath();
                mapCtx.arc(p.x * mapCanvas.width, mapCanvas.height/2, 20, 0, Math.PI*2);
                mapCtx.fill();
                mapCtx.fillStyle = "#fff";
                mapCtx.font = "16px Arial";
                mapCtx.fillText(p.name, p.x * mapCanvas.width - 15, mapCanvas.height/2 + 40);
            });
        };

        mapCanvas.addEventListener('pointerdown', (e) => {
            const rect = mapCanvas.getBoundingClientRect();
            const x = (e.clientX - rect.left) / rect.width;
            const y = (e.clientY - rect.top) / rect.height;
            
            planetsMap.forEach(p => {
                // Check both x and y distance for accurate clicking
                if (Math.abs(x - p.x) < 0.05 && Math.abs(y - 0.5) < 0.1) {
                    state.y = 5000; // Teleport high above the planet safely
                    state.vy = 0; state.vx = 0;
                    state.throttle = 0;
                    state.cameraY = state.y; // Reset camera instantly
                    mapOverlay.style.display = 'none';
                }
            });
        });

        document.getElementById('btn-launch').onclick = function(e) {
            e.stopPropagation();
            if (gameState === "vab") {
                let minX = 9999, maxX = -9999, minY = 9999;
                rocketParts.forEach(p => {
                    let pw = P[p.type].w;
                    let ph = P[p.type].h;
                    if (p.x - pw/2 < minX) minX = p.x - pw/2;
                    if (p.x + pw/2 > maxX) maxX = p.x + pw/2;
                    if (p.y - ph/2 < minY) minY = p.y - ph/2;
                });
                let offsetX = (minX + maxX) / 2;
                rocketParts.forEach(p => { p.x -= offsetX; p.y -= minY; });

                gameState = "flight";
                state.y = 0; // Start EXACTLY on the ground
                state.vy = 0; state.vx = 0;
                state.angle = 0; state.angularVelocity = 0;
                state.throttle = 0;
                state.legsDeployed = true; 
                state.cameraY = 0; 
                state.landedMsgTimer = 0;
                state.shake = 0;

                document.getElementById('vab-menu').style.display = 'none';
                document.getElementById('vab-stats').style.display = 'none';
                document.getElementById('top-bar').style.display = 'none';
                
                document.getElementById('hud').style.display = 'block';
                document.getElementById('minimap-container').style.display = 'block';
                document.getElementById('throttle-zone').style.display = 'block';
                document.getElementById('arrow-zone').style.display = 'flex';
                document.getElementById('btn-legs').style.display = 'block';
                document.getElementById('btn-map').style.display = 'block';
                document.getElementById('throttle-fill').style.height = '0%';
                document.getElementById('status-msg').style.display = 'none';

                let initialStats = { m: 0, f: 0 };
                rocketParts.forEach(p => { initialStats.m += P[p.type].m; initialStats.f += P[p.type].f; });
                state.dryMass = initialStats.m;
                state.maxFuel = initialStats.f;
                state.currentFuel = initialStats.f;
                
                document.getElementById('val-fuel').innerText = "100";
                document.getElementById('val-fuel').style.color = "#00ffcc";
            }
        };

        document.getElementById('btn-reset').onclick = () => window.location.reload();

        function updatePhysics(dt) {
            if (gameState !== "flight") return;

            if (leftPressed) state.angularVelocity -= 1.5 * dt;
            if (rightPressed) state.angularVelocity += 1.5 * dt;
            if (!leftPressed && !rightPressed) state.angularVelocity *= 0.95;
            state.angle += state.angularVelocity;

            let thrust = 0;
            rocketParts.forEach(p => thrust += P[p.type].t);
            state.totalMass = state.dryMass + state.currentFuel;

            let currentGravity = GRAVITY * Math.max(0.1, 1 - (state.y / 100000)); 
            let ay = -currentGravity;
            let ax = 0;

            if (state.throttle > 0 && state.currentFuel > 0 && thrust > 0) {
                let thrustAccel = (thrust * 1000 * state.throttle) / state.totalMass;
                let rad = state.angle * (Math.PI / 180);
                ax += thrustAccel * Math.sin(rad);
                ay += thrustAccel * Math.cos(rad);
                
                state.currentFuel -= 50 * state.throttle * dt; 
                if (state.currentFuel <= 0) {
                    state.currentFuel = 0;
                    state.throttle = 0; 
                    throttleFill.style.height = '0%';
                    document.getElementById('val-fuel').innerText = "0";
                    document.getElementById('val-fuel').style.color = "#ff4444";
                }

                // Exhaust Particles
                for(let i=0; i<5; i++) {
                    let rad = state.angle * (Math.PI / 180);
                    let exhaustX = state.x - Math.sin(rad) * 20;
                    let exhaustY = state.y - Math.cos(rad) * 20;
                    
                    state.particles.push({
                        x: exhaustX + (Math.random()-0.5)*10, 
                        y: exhaustY + (Math.random()-0.5)*10,
                        vx: -Math.sin(rad) * 100 + (Math.random()-0.5)*30,
                        vy: -Math.cos(rad) * 100 + (Math.random()-0.5)*30,
                        life: 1.0, size: Math.random()*10+5, color: "255,150,0"
                    });
                }
            }

            state.vx += ax * dt;
            state.vy += ay * dt;
            state.x += state.vx * dt;
            state.y += state.vy * dt;

            // Ground Collision
            if (state.y <= 0) {
                state.y = 0;
                if (state.vy < -5 || !state.legsDeployed) {
                    // CRASH! CINEMATIC EXPLOSION
                    gameState = "crashed";
                    state.shake = 30; // Massive screen shake
                    
                    // Spawn Fire
                    for(let i=0; i<100; i++) {
                        let col = "255,100,0"; // Orange
                        let r = Math.random();
                        if (r > 0.8) col = "255,255,0"; // Yellow
                        else if (r > 0.5) col = "255,50,0"; // Red

                        state.particles.push({
                            x: state.x + (Math.random()-0.5)*30, 
                            y: state.y + (Math.random()-0.5)*30,
                            vx: (Math.random()-0.5)*400,
                            vy: (Math.random()-0.5)*400,
                            life: 1.0 + Math.random(), 
                            size: Math.random()*15+5, 
                            color: col
                        });
                    }
                    // Spawn Smoke
                    for(let i=0; i<50; i++) {
                        state.particles.push({
                            x: state.x + (Math.random()-0.5)*40, 
                            y: state.y + (Math.random()-0.5)*40,
                            vx: (Math.random()-0.5)*100,
                            vy: (Math.random()-0.5)*100 - 50,
                            life: 2.0 + Math.random()*2, 
                            size: Math.random()*30+15, 
                            color: "100,100,100"
                        });
                    }

                    document.getElementById('status-msg').innerText = "💥 CRASHED";
                    document.getElementById('status-msg').style.color = "#ff4444";
                    document.getElementById('status-msg').style.display = 'block';
                } else {
                    state.vy = 0; state.vx = 0; state.throttle = 0;
                    state.landedMsgTimer += dt;
                    if (state.landedMsgTimer > 0.5) {
                        document.getElementById('status-msg').innerText = "🏆 LANDED SAFELY";
                        document.getElementById('status-msg').style.color = "#00ffcc";
                        document.getElementById('status-msg').style.display = 'block';
                    }
                }
            } else {
                state.landedMsgTimer = 0;
                document.getElementById('status-msg').style.display = 'none';
            }

            state.cameraY += (state.y - state.cameraY) * 5 * dt;
            
            document.getElementById('val-alt').innerText = state.y.toFixed(1);
            document.getElementById('val-vel').innerText = Math.sqrt(state.vx*state.vx + state.vy*state.vy).toFixed(1);
            document.getElementById('val-mass').innerText = state.totalMass.toFixed(0);
            
            let fuelPercent = state.maxFuel > 0 ? (state.currentFuel / state.maxFuel) * 100 : 0;
            if (fuelPercent > 0) {
                document.getElementById('val-fuel').innerText = fuelPercent.toFixed(1);
                if (fuelPercent < 20) document.getElementById('val-fuel').style.color = "#ff4444";
                else document.getElementById('val-fuel').style.color = "#00ffcc";
            }

            // Update Particles
            for(let i = state.particles.length - 1; i >= 0; i--) {
                let p = state.particles[i];
                p.x += p.vx * dt;
                p.y += p.vy * dt;
                if(gameState === "crashed") p.vy += 100 * dt; // Gravity on explosion bits
                p.life -= dt * 1.5;
                if(p.life <= 0) state.particles.splice(i, 1);
            }
            
            state.shake = Math.max(0, state.shake - 50 * dt);
        }

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
            const w = P[p.type].w, h = P[p.type].h;
            
            ctx.save();
            ctx.translate(p.x, py);
            
            if (p.type === "pod") {
                ctx.fillStyle = "#888"; 
                ctx.beginPath(); ctx.moveTo(-w/2, h/2); ctx.lineTo(w/2, h/2); ctx.lineTo(w/3, -h/2); ctx.lineTo(-w/3, -h/2); ctx.fill();
                ctx.fillStyle = "#222"; ctx.beginPath(); ctx.arc(0, 0, w/4, 0, Math.PI*2); ctx.fill();
            } else if (p.type.includes("tank")) {
                let grad = ctx.createLinearGradient(-w/2, 0, w/2, 0); grad.addColorStop(0,"#aaa"); grad.addColorStop(0.5,"#fff"); grad.addColorStop(1,"#888");
                ctx.fillStyle = grad; ctx.fillRect(-w/2, -h/2, w, h);
            } else if (p.type === "engine") {
                ctx.fillStyle = "#222"; ctx.beginPath(); ctx.moveTo(-w/3, -h/2); ctx.lineTo(w/3, -h/2); ctx.lineTo(w/2, h/2); ctx.lineTo(-w/2, h/2); ctx.fill();
            }
            ctx.restore();
        }

        function drawMinimap() {
            minimapCtx.fillStyle = "#000";
            minimapCtx.fillRect(0, 0, 100, 100);
            
            // Draw Earth
            minimapCtx.fillStyle = "#4a90e2";
            minimapCtx.beginPath();
            minimapCtx.arc(50, 50 + (state.y / 100), 5, 0, Math.PI * 2); 
            minimapCtx.fill();

            // Draw Rocket
            minimapCtx.fillStyle = "#00ffcc";
            minimapCtx.beginPath();
            minimapCtx.arc(50, 80, 2, 0, Math.PI * 2);
            minimapCtx.fill();
        }

        function draw() {
            if (gameState === "menu") return; 

            ctx.save();
            
            // Apply Screen Shake
            if (state.shake > 0) {
                ctx.translate((Math.random()-0.5)*state.shake, (Math.random()-0.5)*state.shake);
            }

            if (gameState === "vab") {
                ctx.fillStyle = "#2b3a4a";
            } else {
                if (state.y < 1000) ctx.fillStyle = "#87CEEB"; 
                else if (state.y < 3000) ctx.fillStyle = "#1a3b5c"; 
                else ctx.fillStyle = "#000000"; 
            }
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            ctx.translate(canvas.width/2, canvas.height*0.8);
            
            let zoom = gameState === "vab" ? 1.2 : Math.max(0.4, 1.2 - (state.y/10000));
            ctx.scale(zoom, zoom);

            if (gameState === "vab") {
                ctx.strokeStyle = "rgba(255,255,255,0.1)";
                for(let i=-1000;i<1000;i+=GRID){ctx.beginPath();ctx.moveTo(i,-1000);ctx.lineTo(i,1000);ctx.stroke();ctx.beginPath();ctx.moveTo(-1000,i);ctx.lineTo(1000,i);ctx.stroke();}
                rocketParts.forEach(p => drawPart(p, -p.y));
            } else {
                ctx.translate(-state.x, state.cameraY);

                ctx.fillStyle = "#4a3b2c"; 
                ctx.fillRect(-10000, 0, 20000, 10000);
                
                // Particles
                state.particles.forEach(p => {
                    ctx.fillStyle = `rgba(${p.color}, ${p.life})`;
                    ctx.beginPath();
                    ctx.arc(p.x, -p.y, p.size * p.life, 0, Math.PI*2);
                    ctx.fill();
                });

                if (gameState !== "crashed") {
                    ctx.translate(state.x, -state.y); 
                    ctx.rotate(state.angle * (Math.PI/180));
                    rocketParts.forEach(p => drawPart(p, -p.y));
                }
            }
            ctx.restore();

            if (gameState === "flight" || gameState === "crashed") drawMinimap();
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
