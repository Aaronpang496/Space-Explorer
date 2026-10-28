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
        body { margin: 0; overflow: hidden; background-color: #000; font-family: 'Arial', sans-serif; touch-action: none; user-select: none; height: 100dvh; width: 100vw; }
        canvas { display: block; }
        #ui-layer { position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 99999; }
        
        /* START SCREEN */
        #start-screen { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.85); display: flex; flex-direction: column; justify-content: center; align-items: center; pointer-events: auto; z-index: 1000000; }
        #btn-start { background: #00ffcc; color: #000; border: none; padding: 20px 50px; font-size: 28px; font-weight: bold; border-radius: 10px; cursor: pointer; box-shadow: 0 0 20px #00ffcc; }
        .title { color: white; font-size: 48px; font-weight: bold; margin-bottom: 50px; text-shadow: 0 0 20px #4a90e2; }

        /* VAB MENU */
        #vab-menu { position: absolute; top: 10px; left: 10px; width: 100px; background: rgba(0,0,0,0.85); border: 2px solid #555; border-radius: 10px; display: none; flex-direction: column; align-items: center; padding: 10px 0; pointer-events: auto; max-height: 80vh; overflow-y: auto; z-index: 100000;}
        .part-btn { width: 80px; height: 45px; margin: 3px 0; background: #1a1a1a; border: 2px solid #444; border-radius: 5px; cursor: grab; display: flex; flex-direction: column; justify-content: center; align-items: center; position: relative; touch-action: none;}
        .part-btn.active { border-color: #00ffcc; background: #114444; }
        .part-btn span { font-size: 8px; color: #aaa; position: absolute; bottom: 2px;}

        /* CSS Lego Shapes */
        .m-pod { width: 16px; height: 20px; background: #888; clip-path: polygon(50% 0%, 100% 100%, 0% 100%);}
        .m-chute { width: 20px; height: 12px; background: #f44; border-radius: 10px 10px 0 0;}
        .m-nose { width: 16px; height: 15px; background: #fff; clip-path: polygon(50% 0%, 100% 100%, 0% 100%);}
        .m-tank-s { width: 16px; height: 20px; background: #eee; border-left: 2px solid #ccc; border-right: 2px solid #ccc;}
        .m-tank-m { width: 20px; height: 30px; background: #eee; border-left: 2px solid #ccc; border-right: 2px solid #ccc;}
        .m-tank-l { width: 26px; height: 40px; background: #eee; border-left: 2px solid #ccc; border-right: 2px solid #ccc;}
        .m-engine-s { width: 16px; height: 12px; background: #222; clip-path: polygon(20% 0%, 80% 0%, 100% 100%, 0% 100%);}
        .m-engine-m { width: 20px; height: 15px; background: #222; clip-path: polygon(20% 0%, 80% 0%, 100% 100%, 0% 100%);}
        .m-engine-l { width: 26px; height: 18px; background: #222; clip-path: polygon(20% 0%, 80% 0%, 100% 100%, 0% 100%);}
        .m-decoupler { width: 20px; height: 5px; background: #5c3a21;}
        .m-booster { width: 12px; height: 25px; background: #ddd; border-radius: 5px 5px 0 0;}
        .m-legs { width: 16px; height: 10px; background: #555; clip-path: polygon(0 0, 100% 0, 80% 100%, 20% 100%);}

        /* VAB STATS */
        #vab-stats { position: absolute; top: 10px; right: 10px; width: 140px; background: rgba(0,0,0,0.85); border: 2px solid #555; border-radius: 10px; padding: 10px; color: white; display: none; flex-direction: column; z-index: 100000; pointer-events: none;}
        .stat-row { display: flex; justify-content: space-between; margin-bottom: 5px; font-size: 12px;}
        .stat-val { color: #00ffcc; font-weight: bold;}

        /* TOP BAR */
        #top-bar { position: absolute; top: 10px; left: 50%; transform: translateX(-50%); display: none; gap: 10px; pointer-events: auto; z-index: 100000;}
        .top-btn { background: #1e3a8a; color: white; border: 2px solid #60a5fa; padding: 10px 20px; font-size: 14px; font-weight: bold; border-radius: 5px; cursor: pointer;}
        
        /* FLIGHT HUD */
        #hud { position: absolute; top: 10px; right: 10px; color: #fff; font-size: 12px; background: rgba(0,0,0,0.6); padding: 10px; border-radius: 5px; text-align: right; border-left: 3px solid #00ffcc; display: none; z-index: 100000;}
        
        /* FLIGHT CONTROLS - PERCENTAGE BASED FOR MOBILE */
        #throttle-zone { position: absolute; right: 15px; bottom: 25%; width: 45px; height: 160px; background: rgba(255,255,255,0.15); border: 2px solid #fff; border-radius: 25px; pointer-events: auto; display: none; z-index: 100000; backdrop-filter: blur(5px);}
        #throttle-fill { position: absolute; bottom: 0; width: 100%; height: 0%; background: #ffaa00; border-radius: 22px;}
        
        #arrow-zone { position: absolute; left: 15px; bottom: 25%; display: none; gap: 15px; pointer-events: auto; z-index: 100000;}
        .arrow-btn { width: 60px; height: 80px; background: rgba(255,255,255,0.15); border: 2px solid #fff; border-radius: 10px; color: white; font-size: 30px; display: flex; justify-content: center; align-items: center; cursor: pointer; backdrop-filter: blur(5px);}
        
        #btn-stage { position: absolute; bottom: 25%; right: 75px; width: 70px; height: 50px; background: rgba(200, 50, 0, 0.8); border: 2px solid #ffaa00; color: white; border-radius: 8px; font-size: 12px; font-weight: bold; pointer-events: auto; display: none; z-index: 100000; backdrop-filter: blur(5px);}
        #btn-legs { position: absolute; bottom: 35%; right: 75px; width: 70px; height: 45px; background: rgba(255,255,255,0.15); border: 2px solid #fff; color: white; border-radius: 8px; font-size: 11px; font-weight: bold; pointer-events: auto; display: none; z-index: 100000; backdrop-filter: blur(5px);}
        #btn-legs.deployed { border-color: #00ffcc; color: #00ffcc; }
        #btn-map { position: absolute; top: 10px; left: 15px; width: 60px; height: 40px; background: rgba(255,255,255,0.15); border: 2px solid #fff; color: white; border-radius: 5px; font-size: 12px; font-weight: bold; pointer-events: auto; display: none; z-index: 100000; backdrop-filter: blur(5px);}

        /* MINIMAP */
        #minimap-container { position: absolute; top: 100px; right: 15px; width: 80px; height: 80px; border: 2px solid #555; border-radius: 50%; background: rgba(0,0,0,0.8); overflow: hidden; display: none; z-index: 100000;}
        
        /* TRANSPORT MAP */
        #map-overlay { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 5, 15, 0.95); display: none; pointer-events: auto; z-index: 200000;}
        #map-canvas { position: absolute; top: 0; left: 0; width: 100%; height: 100%; }
        #map-title { position: absolute; top: 20px; left: 20px; color: white; font-size: 24px; font-weight: bold;}

        /* STATUS MSG */
        #status-msg { position: absolute; top: 40%; left: 50%; transform: translate(-50%, -50%); font-size: 36px; font-weight: bold; text-align: center; display: none; text-shadow: 2px 2px 5px #000; pointer-events: none; z-index: 1000000;}
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
            <div class="part-btn" data-type="chute"><div class="m-chute"></div><span>Chute</span></div>
            <div class="part-btn" data-type="nose"><div class="m-nose"></div><span>Nose</span></div>
            <div class="part-btn" data-type="tank_small"><div class="m-tank-s"></div><span>Tank S</span></div>
            <div class="part-btn" data-type="tank_med"><div class="m-tank-m"></div><span>Tank M</span></div>
            <div class="part-btn" data-type="tank_large"><div class="m-tank-l"></div><span>Tank L</span></div>
            <div class="part-btn" data-type="engine_small"><div class="m-engine-s"></div><span>Engine S</span></div>
            <div class="part-btn" data-type="engine_med"><div class="m-engine-m"></div><span>Engine M</span></div>
            <div class="part-btn" data-type="engine_large"><div class="m-engine-l"></div><span>Engine L</span></div>
            <div class="part-btn" data-type="decoupler"><div class="m-decoupler"></div><span>Decoupler</span></div>
            <div class="part-btn" data-type="booster"><div class="m-booster"></div><span>Booster</span></div>
            <div class="part-btn" data-type="legs"><div class="m-legs"></div><span>Legs</span></div>
        </div>

        <div id="vab-stats">
            <div class="stat-row"><span>Mass:</span> <span class="stat-val" id="stat-mass">0 kg</span></div>
            <div class="stat-row"><span>Fuel:</span> <span class="stat-val" id="stat-fuel">0 kg</span></div>
            <div class="stat-row"><span>Thrust:</span> <span class="stat-val" id="stat-thrust">0 kN</span></div>
        </div>

        <div id="top-bar">
            <button class="top-btn" id="btn-launch">LAUNCH 🚀</button>
            <button class="top-btn" id="btn-reset">RESET 🔄</button>
        </div>

        <button id="btn-map">MAP</button>
        <div id="minimap-container"><canvas id="minimap" width="80" height="80"></canvas></div>

        <div id="hud">
            ALT: <span id="val-alt">0</span> m<br>
            VEL: <span id="val-vel">0</span> m/s<br>
            FUEL: <span id="val-fuel" style="color:#00ffcc">100</span>%
        </div>
        
        <div id="throttle-zone"><div id="throttle-fill"></div></div>
        <div id="arrow-zone">
            <div class="arrow-btn" id="joy-left">◀</div>
            <div class="arrow-btn" id="joy-right">▶</div>
        </div>
        <button id="btn-stage">STAGE</button>
        <button id="btn-legs">LEGS: UP</button>

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
        
        const planetsDB = {
            "Earth": { ground: "#2e4a2e", g: 9.81, color: "#4a90e2" },
            "Moon": { ground: "#555555", g: 1.62, color: "#9ca3af" },
            "Mars": { ground: "#8a2be2", g: 3.71, color: "#ea580c" },
            "Jupiter": { ground: "#8b4513", g: 24.79, color: "#d4a373" }
        };

        let state = {
            x: 0, y: 0, vx: 0, vy: 0, 
            angle: 0, angularVelocity: 0, 
            throttle: 0, 
            currentFuel: 0, maxFuel: 0, dryMass: 0, totalMass: 0,
            hasLiftedOff: false,
            legsDeployed: false, legsProgress: 0,
            chuteDeployed: false,
            currentPlanet: "Earth",
            cameraY: 0, lastTime: performance.now(),
            particles: [],
            stars: [],
            shake: 0
        };

        const GRID = 10;
        let rocketParts = []; 
        let currentSelectedPart = "pod";
        
        const P = {
            pod:         { w: 20, h: 24, m: 1500, f: 0,    t: 0 },
            chute:       { w: 20, h: 12, m: 100,  f: 0,    t: 0 },
            nose:        { w: 20, h: 16, m: 200,  f: 0,    t: 0 },
            tank_small:  { w: 20, h: 30, m: 500,  f: 1000, t: 0 },
            tank_med:    { w: 20, h: 60, m: 1000, f: 3000, t: 0 },
            tank_large:  { w: 20, h: 90, m: 2500, f: 9000, t: 0 }, 
            engine_small:{ w: 20, h: 16, m: 300,  f: 0,    t: 300 },
            engine_med:  { w: 20, h: 24, m: 800,  f: 0,    t: 1000 },
            engine_large:{ w: 20, h: 32, m: 2000, f: 0,    t: 3000 },
            decoupler:   { w: 20, h: 6,  m: 100,  f: 0,    t: 0 },
            booster:     { w: 14, h: 50, m: 600,  f: 1800, t: 600 },
            legs:        { w: 24, h: 20, m: 100,  f: 0,    t: 0 }
        };

        // Generate Static Stars
        for(let i=0; i<300; i++) {
            state.stars.push({
                x: Math.random() * 2000 - 1000,
                y: Math.random() * 30000 - 15000,
                size: Math.random() * 2 + 1
            });
        }

        document.getElementById('btn-start').onclick = function() {
            gameState = "vab";
            document.getElementById('start-screen').style.display = 'none';
            document.getElementById('vab-menu').style.display = 'flex';
            document.getElementById('top-bar').style.display = 'flex';
            document.getElementById('vab-stats').style.display = 'flex';
            
            rocketParts = [];
            addPart("engine_med", 0, 12);
            addPart("tank_med", 0, 54);
            addPart("pod", 0, 96);
            addPart("chute", 0, 114);
            updateStats();
        };

        function updateStats() {
            let mass = 0, fuel = 0, thrust = 0;
            rocketParts.forEach(p => {
                mass += P[p.type].m; fuel += P[p.type].f; thrust += P[p.type].t;
            });
            document.getElementById('stat-mass').innerText = (mass + fuel).toLocaleString() + " kg";
            document.getElementById('stat-fuel').innerText = fuel.toLocaleString() + " kg";
            document.getElementById('stat-thrust').innerText = thrust.toLocaleString() + " kN";
        }

        // DRAG AND DROP
        let isDraggingPart = false;
        let draggedType = null;
        let dragGhost = null;

        document.querySelectorAll('.part-btn').forEach(item => {
            item.addEventListener('pointerdown', (e) => {
                if (gameState !== "vab") return;
                e.preventDefault(); 
                
                document.querySelectorAll('.part-btn').forEach(b => b.classList.remove('active'));
                item.classList.add('active');
                currentSelectedPart = item.dataset.type;
                
                isDraggingPart = true;
                draggedType = item.dataset.type;
                dragGhost = document.createElement('div');
                dragGhost.style.position = 'absolute';
                dragGhost.style.width = P[draggedType].w + 'px';
                dragGhost.style.height = P[draggedType].h + 'px';
                
                if (draggedType === 'chute') dragGhost.style.backgroundColor = '#f44';
                else if (draggedType.includes('tank')) dragGhost.style.backgroundColor = '#fff';
                else if (draggedType.includes('engine')) dragGhost.style.backgroundColor = '#222';
                else dragGhost.style.backgroundColor = '#888';
                
                dragGhost.style.border = '2px dashed #00ffcc';
                dragGhost.style.pointerEvents = 'none';
                dragGhost.style.zIndex = 999999;
                dragGhost.style.left = (e.clientX - P[draggedType].w/2) + 'px';
                dragGhost.style.top = (e.clientY - P[draggedType].h/2) + 'px';
                document.body.appendChild(dragGhost);
            });
        });

        window.addEventListener('pointermove', (e) => {
            if (isDraggingPart && dragGhost) {
                dragGhost.style.left = (e.clientX - P[draggedType].w/2) + 'px';
                dragGhost.style.top = (e.clientY - P[draggedType].h/2) + 'px';
            }
        });

        window.addEventListener('pointerup', (e) => {
            if (!isDraggingPart) return;
            if (dragGhost) document.body.removeChild(dragGhost);
            dragGhost = null;
            isDraggingPart = false;

            const rect = canvas.getBoundingClientRect();
            if (e.clientX >= rect.left && e.clientX <= rect.right && e.clientY >= rect.top && e.clientY <= rect.bottom && gameState === "vab") {
                let mouseX = e.clientX - rect.left;
                let mouseY = e.clientY - rect.top;
                let worldX = (mouseX - canvas.width/2) / 1.2;
                
                let maxY = 0;
                if (rocketParts.length > 0) {
                    rocketParts.forEach(p => { if (p.y > maxY) maxY = p.y; });
                }
                let worldY = (canvas.height * 0.8 - maxY * 0.5 - mouseY) / 1.2;

                let snapX = Math.round(worldX / GRID) * GRID;
                let snapY = Math.round(worldY / GRID) * GRID;
                let minDist = 70; 

                let nw = P[draggedType].w;
                let nh = P[draggedType].h;

                if (rocketParts.length > 0) {
                    rocketParts.forEach(p => {
                        let pw = P[p.type].w;
                        let ph = P[p.type].h;

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
                addPart(draggedType, snapX, snapY);
                updateStats();
            }
        });

        function addPart(type, x, y) {
            rocketParts.push({ type, x, y });
        }

        // FLIGHT CONTROLS
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
            if (y < 0) y = 0; if (y > 160) y = 160;
            let percent = 100 - (y / 160) * 100;
            state.throttle = percent / 100;
            throttleFill.style.height = percent + '%';
        });

        document.getElementById('joy-left').addEventListener('pointerdown', () => { leftPressed = true; });
        document.getElementById('joy-left').addEventListener('pointerup', () => { leftPressed = false; });
        document.getElementById('joy-left').addEventListener('pointerleave', () => { leftPressed = false; });

        document.getElementById('joy-right').addEventListener('pointerdown', () => { rightPressed = true; });
        document.getElementById('joy-right').addEventListener('pointerup', () => { rightPressed = false; });
        document.getElementById('joy-right').addEventListener('pointerleave', () => { rightPressed = false; });

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
            { name: "Jupiter", color: "#d4a373", x: 0.6 }
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
                if (Math.abs(x - p.x) < 0.05 && Math.abs(y - 0.5) < 0.1) {
                    state.currentPlanet = p.name;
                    state.y = 5000; 
                    state.vy = 0; state.vx = 0;
                    state.throttle = 0;
                    state.cameraY = state.y; 
                    mapOverlay.style.display = 'none';
                }
            });
        });

        document.getElementById('btn-launch').onclick = function(e) {
            e.stopPropagation();
            if (gameState === "vab") {
                let minY = 9999;
                rocketParts.forEach(p => {
                    if (p.y - P[p.type].h/2 < minY) minY = p.y - P[p.type].h/2;
                });
                rocketParts.forEach(p => { p.y -= minY; });

                gameState = "flight";
                state.y = 0; 
                state.vy = 0; state.vx = 0;
                state.angle = 0; state.angularVelocity = 0;
                state.throttle = 0;
                state.legsDeployed = false; 
                state.chuteDeployed = false;
                state.hasLiftedOff = false;
                state.cameraY = 0; 
                state.shake = 0;
                state.currentPlanet = "Earth";

                document.getElementById('vab-menu').style.display = 'none';
                document.getElementById('vab-stats').style.display = 'none';
                document.getElementById('top-bar').style.display = 'none';
                
                document.getElementById('hud').style.display = 'block';
                document.getElementById('minimap-container').style.display = 'block';
                document.getElementById('throttle-zone').style.display = 'block';
                document.getElementById('arrow-zone').style.display = 'flex';
                document.getElementById('btn-legs').style.display = 'block';
                document.getElementById('btn-stage').style.display = 'block';
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

            let currentGravity = planetsDB[state.currentPlanet].g;

            let ay = -currentGravity;
            let ax = 0;

            if (state.throttle > 0 && state.currentFuel > 0 && thrust > 0) {
                state.hasLiftedOff = true; 
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

                // --- SEPARATE FIRE FOR EACH ENGINE ---
                let radF = state.angle * (Math.PI / 180);
                let cosA = Math.cos(radF);
                let sinA = Math.sin(radF);
                
                rocketParts.forEach(eng => {
                    if (eng.type.includes("engine")) {
                        // Nozzle position relative to rocket center
                        let lx = eng.x;
                        let ly = eng.y - (P[eng.type].h / 2);
                        
                        // Rotate by angle
                        let rx = lx * cosA + ly * sinA;
                        let ry = -lx * sinA + ly * cosA;
                        
                        // World position
                        let wx = state.x + rx;
                        let wy = state.y + ry;
                        
                        for(let i=0; i<3; i++) {
                            state.particles.push({
                                x: wx + (Math.random()-0.5)*P[eng.type].w, 
                                y: wy, 
                                vx: -sinA * 120 + (Math.random()-0.5)*40,
                                vy: -cosA * 120 + (Math.random()-0.5)*40,
                                life: 1.0, size: Math.random()*12+5, color: "255,150,0"
                            });
                        }
                    }
                });
            }

            if (state.hasLiftedOff && state.y < 3000 && state.vy < -10 && !state.chuteDeployed) {
                if (rocketParts.some(p => p.type === 'chute')) {
                    state.chuteDeployed = true;
                }
            }

            if (state.chuteDeployed) {
                ay += 15; 
                state.vx *= 0.98; 
                state.vy *= 0.95;
            }

            state.vx += ax * dt;
            state.vy += ay * dt;
            state.x += state.vx * dt;
            state.y += state.vy * dt;

            if (state.y <= 0) {
                state.y = 0;
                if (state.hasLiftedOff && (state.vy < -5 || !state.legsDeployed) && !state.chuteDeployed) {
                    gameState = "crashed";
                    state.shake = 30; 
                    
                    for(let i=0; i<100; i++) {
                        let col = "255,100,0"; 
                        if (Math.random() > 0.8) col = "255,255,0"; 
                        else if (Math.random() > 0.5) col = "255,50,0"; 

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
                    if (state.hasLiftedOff) {
                        document.getElementById('status-msg').innerText = "🏆 LANDED SAFELY";
                        document.getElementById('status-msg').style.color = "#00ffcc";
                        document.getElementById('status-msg').style.display = 'block';
                    }
                }
            }

            state.cameraY += (state.y - state.cameraY) * 5 * dt;
            
            if (state.legsDeployed && state.legsProgress < 1) state.legsProgress += 2 * dt;
            if (!state.legsDeployed && state.legsProgress > 0) state.legsProgress -= 2 * dt;
            
            document.getElementById('val-alt').innerText = state.y.toFixed(1);
            document.getElementById('val-vel').innerText = Math.sqrt(state.vx*state.vx + state.vy*state.vy).toFixed(1);
            
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
                if(gameState === "crashed") p.vy += 100 * dt; 
                p.life -= dt * 1.5;
                if(p.life <= 0) state.particles.splice(i, 1);
            }
            
            state.shake = Math.max(0, state.shake - 50 * dt);
        }

        function drawPart(p, py) {
            const w = P[p.type].w, h = P[p.type].h;
            ctx.save();
            ctx.translate(p.x, py);
            
            if (p.type === "pod") {
                ctx.fillStyle = "#888"; 
                ctx.beginPath(); ctx.moveTo(-w/2, h/2); ctx.lineTo(w/2, h/2); ctx.lineTo(w/3, -h/2); ctx.lineTo(-w/3, -h/2); ctx.fill();
                ctx.fillStyle = "#222"; ctx.beginPath(); ctx.arc(0, 0, w/4, 0, Math.PI*2); ctx.fill();
            } else if (p.type === "chute") {
                if (!state.chuteDeployed) {
                    ctx.fillStyle = "#555"; ctx.fillRect(-w/3, -h/2, w/1.5, h);
                }
            } else if (p.type === "nose") {
                ctx.fillStyle = "#fff"; ctx.beginPath(); ctx.moveTo(-w/2, h/2); ctx.lineTo(w/2, h/2); ctx.lineTo(0, -h/2); ctx.fill();
            } else if (p.type.includes("tank")) {
                let grad = ctx.createLinearGradient(-w/2, 0, w/2, 0); grad.addColorStop(0,"#aaa"); grad.addColorStop(0.5,"#fff"); grad.addColorStop(1,"#888");
                ctx.fillStyle = grad; ctx.fillRect(-w/2, -h/2, w, h);
            } else if (p.type.includes("engine")) {
                ctx.fillStyle = "#222"; ctx.beginPath(); ctx.moveTo(-w/3, -h/2); ctx.lineTo(w/3, -h/2); ctx.lineTo(w/2, h/2); ctx.lineTo(-w/2, h/2); ctx.fill();
            } else if (p.type === "decoupler") {
                ctx.fillStyle = "#5c3a21"; ctx.fillRect(-w/2, -h/2, w, h);
            } else if (p.type === "booster") {
                ctx.fillStyle = "#ddd"; ctx.fillRect(-w/2, -h/2, w, h);
            }
            ctx.restore();
        }

        function draw() {
            if (gameState === "menu") return; 

            ctx.save();
            
            if (state.shake > 0) {
                ctx.translate((Math.random()-0.5)*state.shake, (Math.random()-0.5)*state.shake);
            }

            if (gameState === "vab") {
                ctx.fillStyle = "#2b3a4a";
            } else {
                if (state.currentPlanet === "Earth") {
                    let alt = state.y;
                    if (alt < 1500) {
                        ctx.fillStyle = "#87CEEB";
                    } else if (alt < 8000) {
                        let ratio = (alt - 1500) / (8000 - 1500);
                        let r = 135 - (135 - 26) * ratio;
                        let g = 206 - (206 - 59) * ratio;
                        let b = 235 - (235 - 92) * ratio;
                        ctx.fillStyle = `rgb(${r}, ${g}, ${b})`;
                    } else if (alt < 20000) {
                        let ratio = (alt - 8000) / (20000 - 8000);
                        let r = 26 - (26) * ratio;
                        let g = 59 - (59) * ratio;
                        let b = 92 - (92) * ratio;
                        ctx.fillStyle = `rgb(${r}, ${g}, ${b})`;
                    } else {
                        ctx.fillStyle = "#000000";
                    }
                } else {
                    ctx.fillStyle = "#000000"; 
                }
            }
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            if (gameState !== "vab" && (state.currentPlanet !== "Earth" || state.y > 8000)) {
                ctx.fillStyle = "#fff";
                state.stars.forEach(star => {
                    ctx.beginPath();
                    ctx.arc(canvas.width/2 + star.x, canvas.height/2 - (star.y - state.cameraY), star.size, 0, Math.PI*2);
                    ctx.fill();
                });
            }

            // --- CAMERA LOGIC ---
            if (gameState === "vab") {
                let maxY = 0;
                if (rocketParts.length > 0) {
                    rocketParts.forEach(p => { if (p.y > maxY) maxY = p.y; });
                }
                ctx.translate(canvas.width/2, canvas.height * 0.8 - maxY * 0.5);
                ctx.scale(1.2, 1.2);

                ctx.fillStyle = "#444";
                ctx.fillRect(-500, 0, 1000, 10);

                ctx.strokeStyle = "rgba(255,255,255,0.1)";
                for(let i=-1000;i<1000;i+=GRID){ctx.beginPath();ctx.moveTo(i,-1000);ctx.lineTo(i,1000);ctx.stroke();ctx.beginPath();ctx.moveTo(-1000,i);ctx.lineTo(1000,i);ctx.stroke();}
                rocketParts.forEach(p => drawPart(p, -p.y));
                
            } else {
                ctx.translate(canvas.width/2, canvas.height * 0.7);
                
                let zoom = Math.max(0.65, 1.2 - (state.y / 30000));
                ctx.scale(zoom, zoom);
                
                ctx.translate(-state.x, state.cameraY);

                ctx.fillStyle = planetsDB[state.currentPlanet].ground; 
                ctx.fillRect(-10000, 0, 20000, 10000);
                
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

                    if (state.legsProgress > 0) {
                        let legLen = 20 * state.legsProgress;
                        ctx.strokeStyle = "#888"; ctx.lineWidth = 4;
                        ctx.beginPath();
                        ctx.moveTo(-6, 10); ctx.lineTo(-6 - legLen, 10 + legLen);
                        ctx.moveTo(6, 10); ctx.lineTo(6 + legLen, 10 + legLen);
                        ctx.stroke();
                    }

                    if (state.chuteDeployed) {
                        ctx.strokeStyle = "#fff"; ctx.lineWidth = 1;
                        ctx.beginPath(); ctx.moveTo(-15, -110); ctx.lineTo(-5, -50); ctx.stroke();
                        ctx.beginPath(); ctx.moveTo(15, -110); ctx.lineTo(5, -50); ctx.stroke();
                        ctx.fillStyle = "#f44";
                        ctx.beginPath(); ctx.arc(0, -110, 30, Math.PI, 0); ctx.fill();
                        ctx.fillStyle = "#fff";
                        ctx.beginPath(); ctx.arc(0, -110, 30, Math.PI, Math.PI * 1.3); ctx.fill();
                        ctx.beginPath(); ctx.arc(0, -110, 30, Math.PI * 1.6, Math.PI * 2); ctx.fill();
                    }
                }
            }
            ctx.restore();
            
            if (gameState !== "vab") {
                minimapCtx.fillStyle = "#000";
                minimapCtx.fillRect(0, 0, 80, 80);
                minimapCtx.fillStyle = planetsDB[state.currentPlanet].color;
                minimapCtx.beginPath();
                minimapCtx.arc(40, 40 + (state.y / 100), 5, 0, Math.PI * 2); 
                minimapCtx.fill();
                minimapCtx.fillStyle = "#00ffcc";
                minimapCtx.beginPath();
                minimapCtx.arc(40, 65, 2, 0, Math.PI * 2);
                minimapCtx.fill();
            }
        }

        function loop(time) {
            let dt = (time - state.lastTime) / 1000;
            state.lastTime = time;
            if (dt > 0.1) dt = 0.1;

            if (gameState !== "menu") {
                updatePhysics(dt);
            }
            draw();
            requestAnimationFrame(loop);
        }
        requestAnimationFrame(loop);
    </script>
</body>
</html>
"""

components.html(game_html, height=900, scrolling=False)
