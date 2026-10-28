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
        #start-screen { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); display: flex; flex-direction: column; justify-content: center; align-items: center; pointer-events: auto; z-index: 1000000; }
        #btn-start { background: #00ffcc; color: #000; border: none; padding: 20px 50px; font-size: 28px; font-weight: bold; border-radius: 10px; cursor: pointer; box-shadow: 0 0 20px #00ffcc; }
        .title { color: white; font-size: 48px; font-weight: bold; margin-bottom: 50px; text-shadow: 0 0 20px #4a90e2; }

        /* VAB Menu */
        #vab-menu { position: absolute; top: 10px; left: 10px; width: 110px; background: rgba(0,0,0,0.85); border: 2px solid #555; border-radius: 10px; display: none; flex-direction: column; align-items: center; padding: 10px 0; pointer-events: auto; max-height: 85vh; overflow-y: auto; z-index: 100000;}
        .part-btn { width: 90px; height: 60px; margin: 4px 0; background: #1a1a1a; border: 2px solid #444; border-radius: 5px; cursor: grab; display: flex; flex-direction: column; justify-content: center; align-items: center; position: relative;}
        .part-btn:active { cursor: grabbing; border-color: #00ffcc; }
        .part-btn span { font-size: 9px; color: #aaa; position: absolute; bottom: 2px;}

        /* CSS Lego Shapes */
        .m-pod { width: 20px; height: 25px; background: #888; border-radius: 5px 5px 0 0; border-bottom: 3px solid #444;}
        .m-nose { width: 20px; height: 20px; background: #fff; clip-path: polygon(50% 0%, 100% 100%, 0% 100%);}
        .m-tank-s { width: 16px; height: 25px; background: #eee; border-left: 2px solid #ccc; border-right: 2px solid #ccc;}
        .m-tank-m { width: 20px; height: 40px; background: #eee; border-left: 2px solid #ccc; border-right: 2px solid #ccc;}
        .m-tank-l { width: 26px; height: 50px; background: #eee; border-left: 2px solid #ccc; border-right: 2px solid #ccc;}
        .m-engine-s { width: 16px; height: 14px; background: #222; clip-path: polygon(20% 0, 80% 0, 100% 100%, 0% 100%);}
        .m-engine-m { width: 20px; height: 18px; background: #222; clip-path: polygon(20% 0, 80% 0, 100% 100%, 0% 100%);}
        .m-engine-l { width: 26px; height: 24px; background: #222; clip-path: polygon(20% 0, 80% 0, 100% 100%, 0% 100%);}
        .m-decoupler { width: 20px; height: 6px; background: #5c3a21;}
        .m-booster { width: 14px; height: 35px; background: #ddd; border-radius: 5px 5px 0 0;}
        .m-legs { width: 20px; height: 15px; background: #555; clip-path: polygon(0 0, 100% 0, 80% 100%, 20% 100%);}

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

        #btn-rotate { position: absolute; top: 220px; right: 10px; width: 60px; height: 60px; background: rgba(0, 0, 0, 0.85); border: 2px solid #00ffcc; color: white; border-radius: 10px; font-size: 24px; display: none; justify-content: center; align-items: center; pointer-events: auto; z-index: 100000; cursor: pointer;}
        #trash-can { position: absolute; bottom: 20px; right: 20px; width: 60px; height: 60px; background: rgba(255,0,0,0.3); border: 2px dashed #ff4444; border-radius: 50%; display: none; justify-content: center; align-items: center; font-size: 30px; pointer-events: auto; z-index: 100000; }
        #trash-can.hover { background: rgba(255,0,0,0.8); border-style: solid; }

        /* Map Overlay */
        #map-overlay { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 5, 15, 0.95); display: none; pointer-events: auto; z-index: 200000;}
        #map-canvas { position: absolute; top: 0; left: 0; width: 100%; height: 100%; }
        #map-title { position: absolute; top: 20px; left: 20px; color: white; font-size: 24px; font-weight: bold;}
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
            <div class="part-btn" data-type="legs"><div class="m-legs"></div><span>Legs</span></div>
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
        <button id="btn-legs">LEGS: UP</button>

        <div id="btn-rotate">🔄</div>
        <div id="trash-can">🗑️</div>
    </div>

    <div id="map-overlay">
        <canvas id="map-canvas"></canvas>
        <div id="map-title">SOLAR SYSTEM</div>
    </div>

    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const mapCanvas = document.getElementById('map-canvas');
        const mapCtx = mapCanvas.getContext('2d');
        
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
            x: 0, y: 50, vx: 0, vy: 0, 
            angle: 0, angularVelocity: 0, 
            throttle: 0, 
            currentFuel: 0, maxFuel: 0, dryMass: 0, totalMass: 0,
            legsDeployed: false,
            cameraY: 50, lastTime: performance.now(),
            particles: []
        };

        const GRAVITY = 9.81;
        const GRID = 15;
        let rocketParts = []; 
        let currentRotation = 0; 
        
        const P = {
            pod:         { w: 30, h: 30, m: 1500, f: 0,    t: 0 },
            nose:        { w: 30, h: 20, m: 200,  f: 0,    t: 0 },
            tank_small:  { w: 24, h: 30, m: 500,  f: 1000, t: 0 },
            tank_med:    { w: 30, h: 60, m: 1000, f: 3000, t: 0 },
            tank_large:  { w: 45, h: 90, m: 2500, f: 9000, t: 0 },
            decoupler:   { w: 30, h: 8,  m: 100,  f: 0,    t: 0 },
            engine_small:{ w: 24, h: 18, m: 300,  f: 0,    t: 250 },
            engine_med:  { w: 30, h: 24, m: 800,  f: 0,    t: 800 },
            engine_large:{ w: 45, h: 36, m: 2000, f: 0,    t: 2000 },
            booster:     { w: 20, h: 50, m: 600,  f: 1800, t: 400 },
            legs:        { w: 30, h: 20, m: 100,  f: 0,    t: 0 }
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
            document.getElementById('btn-rotate').style.display = 'flex';
            document.getElementById('trash-can').style.display = 'flex';
            
            rocketParts = [];
            addPart("engine_med", 0, 12, 0);
            addPart("tank_med", 0, 54, 0);
            addPart("tank_med", 0, 114, 0);
            addPart("pod", 0, 159, 0);
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

        let draggedPart = null;
        let dragGhost = null;
        let isDraggingExisting = false;

        function createGhost(type, angle) {
            dragGhost = document.createElement('div');
            dragGhost.style.position = 'absolute';
            dragGhost.style.width = P[type].w + 'px';
            dragGhost.style.height = P[type].h + 'px';
            dragGhost.style.backgroundColor = type.includes('tank') ? '#fff' : (type.includes('engine') ? '#222' : '#888');
            dragGhost.style.border = '2px dashed #00ffcc';
            dragGhost.style.pointerEvents = 'none';
            dragGhost.style.zIndex = 999999;
            dragGhost.style.transform = `rotate(${angle}deg)`;
            document.body.appendChild(dragGhost);
        }

        document.querySelectorAll('.part-btn').forEach(item => {
            item.addEventListener('pointerdown', (e) => {
                if (gameState !== "vab" || draggedPart) return;
                draggedPart = item.dataset.type;
                currentRotation = 0;
                createGhost(draggedPart, currentRotation);
                isDraggingExisting = false;
            });
        });

        canvas.addEventListener('pointerdown', (e) => {
            if (gameState !== "vab" || draggedPart) return;
            const rect = canvas.getBoundingClientRect();
            let mouseX = e.clientX - rect.left;
            let mouseY = e.clientY - rect.top;
            let worldX = (mouseX - canvas.width/2) / 1.2;
            let worldY = (canvas.height * 0.8 - mouseY) / 1.2;

            for (let i = rocketParts.length - 1; i >= 0; i--) {
                let p = rocketParts[i];
                let angle = p.angle || 0;
                let pw = (angle % 180 === 0) ? P[p.type].w : P[p.type].h;
                let ph = (angle % 180 === 0) ? P[p.type].h : P[p.type].w;
                
                if (Math.abs(worldX - p.x) < pw/2 && Math.abs(worldY - p.y) < ph/2) {
                    draggedPart = p.type;
                    currentRotation = angle;
                    rocketParts.splice(i, 1);
                    updateStats(); 
                    createGhost(draggedPart, currentRotation);
                    isDraggingExisting = true;
                    break;
                }
            }
        });

        window.addEventListener('pointermove', (e) => {
            if (dragGhost && draggedPart) {
                dragGhost.style.left = (e.clientX - P[draggedPart].w/2) + 'px';
                dragGhost.style.top = (e.clientY - P[draggedPart].h/2) + 'px';
            }
        });

        const trashCan = document.getElementById('trash-can');
        trashCan.addEventListener('pointerenter', () => trashCan.classList.add('hover'));
        trashCan.addEventListener('pointerleave', () => trashCan.classList.remove('hover'));

        window.addEventListener('pointerup', (e) => {
            if (!draggedPart) return;

            const tr = trashCan.getBoundingClientRect();
            if (e.clientX >= tr.left && e.clientX <= tr.right && e.clientY >= tr.top && e.clientY <= tr.bottom) {
                draggedPart = null;
                if (dragGhost) document.body.removeChild(dragGhost);
                dragGhost = null;
                updateStats(); 
                return;
            }

            if (e.target === canvas && gameState === "vab") {
                const rect = canvas.getBoundingClientRect();
                let mouseX = e.clientX - rect.left;
                let mouseY = e.clientY - rect.top;
                let worldX = (mouseX - canvas.width/2) / 1.2;
                let worldY = (canvas.height * 0.8 - mouseY) / 1.2;

                let snapX = Math.round(worldX / GRID) * GRID;
                let snapY = Math.round(worldY / GRID) * GRID;
                let minDist = 45; 

                let nw = (currentRotation % 180 === 0) ? P[draggedPart].w : P[draggedPart].h;
                let nh = (currentRotation % 180 === 0) ? P[draggedPart].h : P[draggedPart].w;

                if (rocketParts.length > 0) {
                    rocketParts.forEach(p => {
                        let pw = (p.angle % 180 === 0) ? P[p.type].w : P[p.type].h;
                        let ph = (p.angle % 180 === 0) ? P[p.type].h : P[p.type].w;

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
                addPart(draggedPart, snapX, snapY, currentRotation);
                updateStats();
            } else if (isDraggingExisting) {
                addPart(draggedPart, worldX, worldY, currentRotation);
                updateStats();
            }

            if (dragGhost) document.body.removeChild(dragGhost);
            dragGhost = null;
            draggedPart = null;
        });

        document.getElementById('btn-rotate').onclick = () => {
            if (gameState === "vab") {
                currentRotation = (currentRotation + 90) % 360;
                if (dragGhost) dragGhost.style.transform = `rotate(${currentRotation}deg)`;
            }
        };

        function addPart(type, x, y, angle = 0) {
            rocketParts.push({ type, x, y, angle: angle });
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

        document.getElementById('btn-stage').onclick = function() {
            let sideDecouplers = rocketParts.filter(p => p.type === 'decoupler' && Math.abs(p.x) > 10);
            if (sideDecouplers.length > 0) {
                let dropX = sideDecouplers[0].x;
                let partsToDrop = rocketParts.filter(p => Math.abs(p.x - dropX) < 5);
                rocketParts = rocketParts.filter(p => !partsToDrop.includes(p));
                let otherSide = rocketParts.find(p => p.type === 'decoupler' && Math.abs(p.x + dropX) < 5);
                if (otherSide) {
                    let dropX2 = otherSide.x;
                    let partsToDrop2 = rocketParts.filter(p => Math.abs(p.x - dropX2) < 5);
                    rocketParts = rocketParts.filter(p => !partsToDrop2.includes(p));
                }
            } else {
                let centerDec = rocketParts.filter(p => p.type === 'decoupler');
                if (centerDec.length === 0) return;
                centerDec.sort((a, b) => a.y - b.y);
                let lowest = centerDec[0];
                rocketParts = rocketParts.filter(p => p.y >= lowest.y);
            }
            
            let m = 0, f = 0;
            rocketParts.forEach(p => { m += P[p.type].m; f += P[p.type].f; });
            state.dryMass = m;
            state.maxFuel = f;
            if (state.currentFuel > state.maxFuel) state.currentFuel = state.maxFuel;
            
            updateStats();
        };

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
            planetsMap.forEach(p => {
                if (Math.abs(x - p.x) < 0.05) {
                    state.y = 1000; 
                    state.vy = 0; state.vx = 0;
                    state.throttle = 0;
                    mapOverlay.style.display = 'none';
                }
            });
        });

        document.getElementById('btn-launch').onclick = function(e) {
            e.stopPropagation();
            if (gameState === "vab") {
                let minX = 9999, maxX = -9999, minY = 9999;
                rocketParts.forEach(p => {
                    let pw = (p.angle % 180 === 0) ? P[p.type].w : P[p.type].h;
                    let ph = (p.angle % 180 === 0) ? P[p.type].h : P[p.type].w;
                    if (p.x - pw/2 < minX) minX = p.x - pw/2;
                    if (p.x + pw/2 > maxX) maxX = p.x + pw/2;
                    if (p.y - ph/2 < minY) minY = p.y - ph/2;
                });
                let offsetX = (minX + maxX) / 2;
                rocketParts.forEach(p => { p.x -= offsetX; p.y -= minY; });

                gameState = "flight";
                state.y = 50; 
                state.vy = 0; state.vx = 0;
                state.angle = 0; state.angularVelocity = 0;
                state.throttle = 0;
                state.legsDeployed = false;
                state.cameraY = state.y; 

                document.getElementById('vab-menu').style.display = 'none';
                document.getElementById('vab-stats').style.display = 'none';
                document.getElementById('btn-rotate').style.display = 'none';
                document.getElementById('trash-can').style.display = 'none';
                document.getElementById('top-bar').style.display = 'none';
                
                document.getElementById('hud').style.display = 'block';
                document.getElementById('throttle-zone').style.display = 'block';
                document.getElementById('arrow-zone').style.display = 'flex';
                document.getElementById('btn-stage').style.display = 'block';
                document.getElementById('btn-legs').style.display = 'block';
                document.getElementById('btn-map').style.display = 'block';
                document.getElementById('throttle-fill').style.height = '0%';

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
            
            let drag = 0;
            if (state.y < 10000) {
                drag = (Math.abs(state.vx) + Math.abs(state.vy)) * 0.005;
            }

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

                // FIXED: Fire particles now rotate with the rocket
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

            state.vx -= Math.sign(state.vx) * drag * dt;
            state.vy -= Math.sign(state.vy) * drag * dt;

            state.vx += ax * dt;
            state.vy += ay * dt;
            state.x += state.vx * dt;
            state.y += state.vy * dt;

            if (state.y < 0) {
                state.y = 0;
                if (Math.hypot(state.vx, state.vy) > 5 || !state.legsDeployed) {
                    gameState = "crashed";
                    for(let i=0; i<100; i++) {
                        state.particles.push({
                            x: state.x + (Math.random()-0.5)*30, 
                            y: state.y + (Math.random()-0.5)*30,
                            vx: (Math.random()-0.5)*200,
                            vy: (Math.random()-0.5)*200,
                            life: 1.5, size: Math.random()*20+10, color: "255,50,0"
                        });
                    }
                    document.getElementById('hud').innerText = "CRASHED";
                } else {
                    state.vy = 0; state.vx = 0; state.throttle = 0;
                    document.getElementById('hud').innerText = "LANDED SAFELY";
                }
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

            for(let i = state.particles.length - 1; i >= 0; i--) {
                let p = state.particles[i];
                p.x += p.vx * dt;
                p.y += p.vy * dt;
                p.life -= dt * 1.5;
                if(p.life <= 0) state.particles.splice(i, 1);
            }
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
            const angle = (p.angle || 0) * Math.PI / 180;
            
            ctx.save();
            ctx.translate(p.x, py);
            ctx.rotate(angle);
            
            if (p.type === "pod") {
                ctx.fillStyle = "#888"; 
                ctx.beginPath(); ctx.moveTo(-w/2, h/2); ctx.lineTo(w/2, h/2); ctx.lineTo(w/3, -h/2); ctx.lineTo(-w/3, -h/2); ctx.fill();
                ctx.fillStyle = "#222"; ctx.beginPath(); ctx.arc(0, 0, w/4, 0, Math.PI*2); ctx.fill();
            } else if (p.type === "nose") {
                ctx.fillStyle = "#fff"; ctx.beginPath(); ctx.moveTo(-w/2, h/2); ctx.lineTo(w/2, h/2); ctx.lineTo(0, -h/2); ctx.fill();
            } else if (p.type.includes("tank")) {
                let grad = ctx.createLinearGradient(-w/2, 0, w/2, 0); grad.addColorStop(0,"#aaa"); grad.addColorStop(0.5,"#fff"); grad.addColorStop(1,"#888");
                ctx.fillStyle = grad; ctx.fillRect(-w/2, -h/2, w, h);
            } else if (p.type.includes("engine")) {
                ctx.fillStyle = "#222"; ctx.beginPath(); ctx.moveTo(-w/3, -h/2); ctx.lineTo(w/3, -h/2); ctx.lineTo(w/2, h/2); ctx.lineTo(-w/2, h/2); ctx.fill();
            } else if (p.type === "booster") {
                ctx.fillStyle = "#ddd"; ctx.fillRect(-w/2, -h/2, w, h);
            } else if (p.type === "decoupler") {
                ctx.fillStyle = "#5c3a21"; ctx.fillRect(-w/2, -h/2, w, h);
            } else if (p.type === "legs") {
                ctx.fillStyle = "#555"; ctx.beginPath(); ctx.moveTo(-w/2, -h/2); ctx.lineTo(w/2, -h/2); ctx.lineTo(w/3, h/2); ctx.lineTo(-w/3, h/2); ctx.fill();
            }
            ctx.restore();
        }

        function draw() {
            if (gameState === "menu") return; 

            // Faster sky transition
            if (gameState === "vab") {
                ctx.fillStyle = "#2b3a4a";
            } else {
                if (state.y < 1000) ctx.fillStyle = "#87CEEB"; // Blue sky
                else if (state.y < 3000) ctx.fillStyle = "#1a3b5c"; // Dark blue
                else ctx.fillStyle = "#000000"; // Space
            }
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            ctx.save();
            ctx.translate(canvas.width/2, canvas.height*0.8);
            
            let zoom = gameState === "vab" ? 1.2 : Math.max(0.4, 1.2 - (state.y/10000));
            ctx.scale(zoom, zoom);

            if (gameState === "vab") {
                ctx.strokeStyle = "rgba(255,255,255,0.1)";
                for(let i=-1000;i<1000;i+=GRID){ctx.beginPath();ctx.moveTo(i,-1000);ctx.lineTo(i,1000);ctx.stroke();ctx.beginPath();ctx.moveTo(-1000,i);ctx.lineTo(1000,i);ctx.stroke();}
                rocketParts.forEach(p => drawPart(p, -p.y));
            } else {
                ctx.translate(-state.x, state.cameraY);

                ctx.fillStyle = "#4a3b2c"; ctx.fillRect(-10000, 0, 20000, 10000);
                
                state.particles.forEach(p => {
                    ctx.fillStyle = `rgba(${p.color}, ${p.life})`;
                    ctx.beginPath();
                    ctx.arc(p.x, -p.y, p.size * p.life, 0, Math.PI*2);
                    ctx.fill();
                });

                ctx.translate(0, -state.y); 
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
