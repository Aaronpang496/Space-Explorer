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
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body { margin: 0; overflow: hidden; background-color: #000; font-family: 'Arial', sans-serif; touch-action: none; user-select: none; height: 100dvh; width: 100vw; }
        canvas { display: block; }
        #ui-layer { position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 99999; }

        #start-screen { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.85); display: flex; flex-direction: column; justify-content: center; align-items: center; pointer-events: auto; z-index: 1000000; }
        #btn-start { background: #00ffcc; color: #000; border: none; padding: 20px 50px; font-size: 28px; font-weight: bold; border-radius: 10px; cursor: pointer; box-shadow: 0 0 20px #00ffcc; }
        .title { color: white; font-size: 48px; font-weight: bold; margin-bottom: 50px; text-shadow: 0 0 20px #4a90e2; }

        #vab-menu { position: absolute; top: 10px; left: 10px; width: 100px; background: rgba(0,0,0,0.85); border: 2px solid #555; border-radius: 10px; display: none; flex-direction: column; align-items: center; padding: 10px 0; pointer-events: auto; max-height: 80vh; overflow-y: auto; z-index: 100000;}
        .part-btn { width: 80px; height: 45px; margin: 3px 0; background: #1a1a1a; border: 2px solid #444; border-radius: 5px; cursor: grab; display: flex; flex-direction: column; justify-content: center; align-items: center; position: relative; touch-action: none;}
        .part-btn.active { border-color: #00ffcc; background: #114444; }
        .part-btn span { font-size: 8px; color: #aaa; position: absolute; bottom: 2px;}

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

        #vab-stats { position: absolute; top: 10px; right: 10px; width: 140px; background: rgba(0,0,0,0.85); border: 2px solid #555; border-radius: 10px; padding: 10px; color: white; display: none; flex-direction: column; z-index: 100000; pointer-events: none;}
        .stat-row { display: flex; justify-content: space-between; margin-bottom: 5px; font-size: 12px;}
        .stat-val { color: #00ffcc; font-weight: bold;}

        #trash-can { position: absolute; bottom: 20px; right: 20px; width: 60px; height: 60px; background: rgba(255,0,0,0.3); border: 2px dashed #ff4444; border-radius: 50%; display: none; justify-content: center; align-items: center; font-size: 30px; pointer-events: auto; z-index: 100000; transition: all 0.2s; }
        #trash-can.hover { background: rgba(255,0,0,0.8); border-style: solid; transform: scale(1.1); }

        #top-bar { position: absolute; top: 10px; left: 50%; transform: translateX(-50%); display: none; gap: 10px; pointer-events: auto; z-index: 100000;}
        .top-btn { background: #1e3a8a; color: white; border: 2px solid #60a5fa; padding: 10px 20px; font-size: 14px; font-weight: bold; border-radius: 5px; cursor: pointer;}

        #hud { position: absolute; top: 10px; right: 10px; color: #fff; font-size: 12px; background: rgba(0,0,0,0.6); padding: 10px; border-radius: 5px; text-align: right; border-left: 3px solid #00ffcc; display: none; z-index: 100000;}
        #hud-planet { color: #ffcc44; font-weight: bold; }
        #hud-space { color: #00ffcc; font-weight: bold; display: none; }

        #throttle-zone { position: absolute; right: 15px; top: 60%; width: 45px; height: 160px; background: rgba(255,255,255,0.15); border: 2px solid #fff; border-radius: 25px; pointer-events: auto; display: none; z-index: 100000; backdrop-filter: blur(5px);}
        #throttle-fill { position: absolute; bottom: 0; width: 100%; height: 0%; background: #ffaa00; border-radius: 22px;}

        #arrow-zone { position: absolute; left: 15px; top: 65%; display: none; gap: 15px; pointer-events: auto; z-index: 100000;}
        .arrow-btn { width: 60px; height: 80px; background: rgba(255,255,255,0.15); border: 2px solid #fff; border-radius: 10px; color: white; font-size: 30px; display: flex; justify-content: center; align-items: center; cursor: pointer; backdrop-filter: blur(5px);}

        #btn-stage { position: absolute; top: 65%; right: 75px; width: 70px; height: 50px; background: rgba(200, 50, 0, 0.8); border: 2px solid #ffaa00; color: white; border-radius: 8px; font-size: 12px; font-weight: bold; pointer-events: auto; display: none; z-index: 100000; backdrop-filter: blur(5px);}
        #btn-legs { position: absolute; top: 55%; right: 75px; width: 70px; height: 45px; background: rgba(255,255,255,0.15); border: 2px solid #fff; color: white; border-radius: 8px; font-size: 11px; font-weight: bold; pointer-events: auto; display: none; z-index: 100000; backdrop-filter: blur(5px);}
        #btn-legs.deployed { border-color: #00ffcc; color: #00ffcc; }
        #btn-map { position: absolute; top: 10px; left: 15px; width: 60px; height: 40px; background: rgba(255,255,255,0.15); border: 2px solid #fff; color: white; border-radius: 5px; font-size: 12px; font-weight: bold; pointer-events: auto; display: none; z-index: 100000; backdrop-filter: blur(5px);}

        #minimap-container { position: absolute; top: 100px; right: 15px; width: 80px; height: 80px; border: 2px solid #555; border-radius: 50%; background: rgba(0,0,0,0.8); overflow: hidden; display: none; z-index: 100000;}

        #map-overlay { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 5, 15, 0.95); display: none; pointer-events: auto; z-index: 200000;}
        #map-canvas { position: absolute; top: 0; left: 0; width: 100%; height: 100%; }
        #map-title { position: absolute; top: 20px; left: 20px; color: white; font-size: 24px; font-weight: bold;}
        #map-hint { position: absolute; bottom: 24px; left: 0; width: 100%; text-align: center; color: #9ab; font-size: 13px; }

        #status-msg { position: absolute; top: 40%; left: 50%; transform: translate(-50%, -50%); font-size: 36px; font-weight: bold; text-align: center; display: none; text-shadow: 2px 2px 5px #000; pointer-events: none; z-index: 1000000;}

        #btn-rebuild { position: absolute; bottom: 30px; left: 50%; transform: translateX(-50%); display: none; padding: 15px 30px; background: #1e3a8a; color: #fff; border: 2px solid #60a5fa; border-radius: 8px; font-size: 16px; font-weight: bold; pointer-events: auto; z-index: 100000; cursor: pointer;}

        #warp-flash { position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: radial-gradient(circle, #ffffff 0%, #aaddff 40%, rgba(0,0,20,0) 100%);
            opacity: 0; pointer-events: none; z-index: 500000; transition: opacity 0.3s ease-out; }
        #warp-flash.active { opacity: 1; }
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

        <div id="trash-can">🗑️</div>

        <div id="top-bar">
            <button class="top-btn" id="btn-launch">LAUNCH 🚀</button>
            <button class="top-btn" id="btn-reset">RESET 🔄</button>
        </div>

        <button id="btn-map">MAP</button>
        <div id="minimap-container"><canvas id="minimap" width="80" height="80"></canvas></div>

        <div id="hud">
            <span id="hud-planet">Earth</span><br>
            ALT: <span id="val-alt">0</span> m<br>
            VEL: <span id="val-vel">0</span> m/s<br>
            FUEL: <span id="val-fuel" style="color:#00ffcc">100</span>%<br>
            <span id="hud-space">★ IN SPACE ★</span>
        </div>

        <div id="throttle-zone"><div id="throttle-fill"></div></div>
        <div id="arrow-zone">
            <div class="arrow-btn" id="joy-left">◀</div>
            <div class="arrow-btn" id="joy-right">▶</div>
        </div>
        <button id="btn-stage">STAGE</button>
        <button id="btn-legs">LEGS: UP</button>

        <div id="status-msg"></div>
        <button id="btn-rebuild">REBUILD 🔄</button>
    </div>

    <div id="map-overlay">
        <canvas id="map-canvas"></canvas>
        <div id="map-title">SOLAR SYSTEM MAP</div>
        <div id="map-hint">Tap a planet to warp there</div>
    </div>

    <div id="warp-flash"></div>

    <script>
    const canvas = document.getElementById('gameCanvas');
    const ctx = canvas.getContext('2d');
    const mapCanvas = document.getElementById('map-canvas');
    const mapCtx = mapCanvas.getContext('2d');
    const minimapCanvas = document.getElementById('minimap');
    const minimapCtx = minimapCanvas.getContext('2d');

    let W = window.innerWidth;
    let H = window.innerHeight;

    let stars = [];
    function buildStars() {
        stars = [];
        const count = Math.min(320, Math.max(140, Math.round((W * H) / 9000)));
        for (let i = 0; i < count; i++) {
            stars.push({
                x: Math.random() * W,
                y: Math.random() * H,
                size: Math.random() * 1.7 + 0.4,
                a: 0.35 + Math.random() * 0.65
            });
        }
    }

    function resize() {
        W = window.innerWidth;
        H = window.innerHeight;
        canvas.width = W;
        canvas.height = H;
        mapCanvas.width = W;
        mapCanvas.height = H;
        buildStars();
    }
    window.addEventListener('resize', resize);
    resize();

    let gameState = "menu";

    const GRID = 10;
    let rocketParts = [];
    let currentSelectedPart = "pod";

    const P = {
        pod:          { w: 20, h: 24, m: 1500, f: 0,    t: 0 },
        chute:        { w: 20, h: 12, m: 100,  f: 0,    t: 0 },
        nose:         { w: 20, h: 16, m: 200,  f: 0,    t: 0 },
        tank_small:   { w: 20, h: 30, m: 500,  f: 1000, t: 0 },
        tank_med:     { w: 20, h: 60, m: 1000, f: 3000, t: 0 },
        tank_large:   { w: 20, h: 90, m: 2500, f: 9000, t: 0 },
        engine_small: { w: 20, h: 16, m: 300,  f: 0,    t: 300 },
        engine_med:   { w: 20, h: 24, m: 800,  f: 0,    t: 1000 },
        engine_large: { w: 20, h: 32, m: 2000, f: 0,    t: 3000 },
        decoupler:    { w: 20, h: 6,  m: 100,  f: 0,    t: 0 },
        booster:      { w: 14, h: 50, m: 600,  f: 1800, t: 600 },
        legs:         { w: 24, h: 20, m: 100,  f: 0,    t: 0 }
    };

    const planetsDB = {
        "Earth":   { ground: "#2e4a2e", g: 9.81,  color: "#4a90e2", sky: [135, 206, 235], atmo: 9000 },
        "Moon":    { ground: "#555555", g: 1.62,  color: "#9ca3af", sky: [0, 0, 0],       atmo: 0    },
        "Mars":    { ground: "#8a2be2", g: 3.71,  color: "#ea580c", sky: [224, 150, 110], atmo: 6000 },
        "Jupiter": { ground: "#8b4513", g: 24.79, color: "#d4a373", sky: [216, 170, 130], atmo: 15000 }
    };

    function makeSurface(seed) {
        const arr = [];
        let s = seed >>> 0;
        function rnd() { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }
        for (let i = 0; i < 46; i++) {
            arr.push({
                x: (rnd() - 0.5) * 6000,
                w: 20 + rnd() * 80,
                h: 4 + rnd() * 10,
                a: 0.06 + rnd() * 0.10,
                light: rnd() > 0.5
            });
        }
        return arr;
    }
    Object.keys(planetsDB).forEach(function (k, i) {
        planetsDB[k].surface = makeSurface(1234 + i * 97);
    });

    let state = {
        x: 0, y: 0, vx: 0, vy: 0,
        angle: 0, angularVelocity: 0,
        throttle: 0,
        currentFuel: 0, maxFuel: 0, dryMass: 0, totalMass: 0,
        rocketCenterY: 0,
        hasLiftedOff: false,
        onGround: true,
        legsDeployed: false, legsProgress: 0,
        chuteDeployed: false,
        currentPlanet: "Earth",
        cameraX: 0, cameraY: 0,
        lastTime: performance.now(),
        particles: [],
        shake: 0
    };

    const throttleFill = document.getElementById('throttle-fill');
    const statusEl = document.getElementById('status-msg');
    const rebuildBtn = document.getElementById('btn-rebuild');
    const mapOverlay = document.getElementById('map-overlay');
    let statusTimer = null;

    function showStatus(text, color, seconds) {
        statusEl.innerText = text;
        statusEl.style.color = color;
        statusEl.style.display = 'block';
        if (statusTimer) { clearTimeout(statusTimer); statusTimer = null; }
        if (seconds) {
            statusTimer = setTimeout(function () { statusEl.style.display = 'none'; }, seconds * 1000);
        }
    }

    function rocketMaxY() {
        let m = 0;
        rocketParts.forEach(function (p) { if (p.y > m) m = p.y; });
        return m;
    }

    function vabView() {
        const maxY = rocketMaxY();
        const rh = Math.max(maxY, 60);
        const sc = Math.max(0.35, Math.min(2.2, (H * 0.55) / rh));
        const oy = H * 0.5 + (rh * sc) / 2;
        return { ox: W / 2, oy: oy, sc: sc };
    }

    function screenToBuild(clientX, clientY) {
        const rect = canvas.getBoundingClientRect();
        const mx = clientX - rect.left;
        const my = clientY - rect.top;
        const v = vabView();
        return { x: (mx - v.ox) / v.sc, y: (v.oy - my) / v.sc };
    }

    /* Compute rocket center of mass in "part-y" space */
    function computeRocketCenter() {
        let totalMass = 0, weightedY = 0;
        rocketParts.forEach(function (p) {
            const m = P[p.type].m + P[p.type].f;
            totalMass += m;
            weightedY += p.y * m;
        });
        state.rocketCenterY = totalMass > 0 ? weightedY / totalMass : 0;
    }

    document.getElementById('btn-start').onclick = function () {
        gameState = "vab";
        document.getElementById('start-screen').style.display = 'none';
        document.getElementById('vab-menu').style.display = 'flex';
        document.getElementById('top-bar').style.display = 'flex';
        document.getElementById('vab-stats').style.display = 'flex';
        document.getElementById('trash-can').style.display = 'flex';

        rocketParts = [];
        addPart("engine_med", 0, 12);
        addPart("tank_med", 0, 54);
        addPart("pod", 0, 96);
        addPart("chute", 0, 114);
        updateStats();
    };

    function updateStats() {
        let mass = 0, fuel = 0, thrust = 0;
        rocketParts.forEach(function (p) {
            mass += P[p.type].m;
            fuel += P[p.type].f;
            thrust += P[p.type].t;
        });
        document.getElementById('stat-mass').innerText = (mass + fuel).toLocaleString() + " kg";
        document.getElementById('stat-fuel').innerText = fuel.toLocaleString() + " kg";
        document.getElementById('stat-thrust').innerText = thrust.toLocaleString() + " kN";
    }

    let isDraggingPart = false;
    let draggedType = null;
    let dragGhost = null;

    document.querySelectorAll('.part-btn').forEach(function (item) {
        item.addEventListener('pointerdown', function (e) {
            if (gameState !== "vab") return;
            e.preventDefault();
            document.querySelectorAll('.part-btn').forEach(function (b) { b.classList.remove('active'); });
            item.classList.add('active');
            currentSelectedPart = item.dataset.type;
            startDrag(currentSelectedPart, e.clientX, e.clientY);
        });
    });

    canvas.addEventListener('pointerdown', function (e) {
        if (gameState !== "vab" || isDraggingPart) return;
        const b = screenToBuild(e.clientX, e.clientY);

        for (let i = rocketParts.length - 1; i >= 0; i--) {
            const p = rocketParts[i];
            const pw = P[p.type].w, ph = P[p.type].h;
            if (Math.abs(b.x - p.x) < pw / 2 + 3 && Math.abs(b.y - p.y) < ph / 2 + 3) {
                rocketParts.splice(i, 1);
                updateStats();
                startDrag(p.type, e.clientX, e.clientY);
                break;
            }
        }
    });

    function startDrag(type, cx, cy) {
        isDraggingPart = true;
        draggedType = type;
        const v = vabView();
        const gw = P[type].w * v.sc;
        const gh = P[type].h * v.sc;

        dragGhost = document.createElement('div');
        dragGhost.style.position = 'absolute';
        dragGhost.style.width = gw + 'px';
        dragGhost.style.height = gh + 'px';
        dragGhost.style.opacity = '0.8';

        if (type === 'chute') dragGhost.style.backgroundColor = '#f44';
        else if (type.indexOf('tank') !== -1) dragGhost.style.backgroundColor = '#fff';
        else if (type.indexOf('engine') !== -1) dragGhost.style.backgroundColor = '#222';
        else dragGhost.style.backgroundColor = '#888';

        dragGhost.style.border = '2px dashed #00ffcc';
        dragGhost.style.pointerEvents = 'none';
        dragGhost.style.zIndex = 999999;
        dragGhost.style.left = (cx - gw / 2) + 'px';
        dragGhost.style.top = (cy - gh / 2) + 'px';
        document.body.appendChild(dragGhost);
    }

    window.addEventListener('pointermove', function (e) {
        if (isDraggingPart && dragGhost) {
            const v = vabView();
            const gw = P[draggedType].w * v.sc;
            const gh = P[draggedType].h * v.sc;
            dragGhost.style.left = (e.clientX - gw / 2) + 'px';
            dragGhost.style.top = (e.clientY - gh / 2) + 'px';
        }
    });

    const trashCan = document.getElementById('trash-can');
    trashCan.addEventListener('pointerenter', function () { trashCan.classList.add('hover'); });
    trashCan.addEventListener('pointerleave', function () { trashCan.classList.remove('hover'); });

    window.addEventListener('pointerup', function (e) {
        if (!isDraggingPart) return;

        if (dragGhost) { dragGhost.remove(); dragGhost = null; }
        isDraggingPart = false;
        const type = draggedType;
        draggedType = null;

        const tr = trashCan.getBoundingClientRect();
        if (e.clientX >= tr.left && e.clientX <= tr.right && e.clientY >= tr.top && e.clientY <= tr.bottom) {
            updateStats();
            return;
        }

        if (gameState !== "vab" || !type) return;

        const rect = canvas.getBoundingClientRect();
        if (e.clientX < rect.left || e.clientX > rect.right || e.clientY < rect.top || e.clientY > rect.bottom) {
            updateStats();
            return;
        }

        const b = screenToBuild(e.clientX, e.clientY);

        let snapX = Math.round(b.x / GRID) * GRID;
        let snapY = Math.round(b.y / GRID) * GRID;
        let best = 70;

        const nw = P[type].w;
        const nh = P[type].h;

        rocketParts.forEach(function (p) {
            const pw = P[p.type].w;
            const ph = P[p.type].h;
            const cand = [
                { d: Math.hypot(b.x - p.x, b.y - (p.y + ph / 2)), x: p.x, y: p.y + ph / 2 + nh / 2 },
                { d: Math.hypot(b.x - p.x, b.y - (p.y - ph / 2)), x: p.x, y: p.y - ph / 2 - nh / 2 },
                { d: Math.hypot(b.x - (p.x + pw / 2), b.y - p.y), x: p.x + pw / 2 + nw / 2, y: p.y },
                { d: Math.hypot(b.x - (p.x - pw / 2), b.y - p.y), x: p.x - pw / 2 - nw / 2, y: p.y }
            ];
            cand.forEach(function (c) {
                if (c.d < best) { best = c.d; snapX = c.x; snapY = c.y; }
            });
        });

        addPart(type, snapX, snapY);
        updateStats();
    });

    function addPart(type, x, y) {
        rocketParts.push({ type: type, x: x, y: y });
    }

    let isDraggingThrottle = false;
    let leftPressed = false;
    let rightPressed = false;

    const throttleZone = document.getElementById('throttle-zone');

    throttleZone.addEventListener('pointerdown', function (e) {
        isDraggingThrottle = true;
        try { throttleZone.setPointerCapture(e.pointerId); } catch (err) {}
        setThrottleFromEvent(e);
    });
    throttleZone.addEventListener('pointermove', function (e) {
        if (!isDraggingThrottle) return;
        setThrottleFromEvent(e);
    });
    throttleZone.addEventListener('pointerup', function () { isDraggingThrottle = false; });
    throttleZone.addEventListener('pointercancel', function () { isDraggingThrottle = false; });

    function setThrottleFromEvent(e) {
        const rect = throttleZone.getBoundingClientRect();
        let y = e.clientY - rect.top;
        if (y < 0) y = 0;
        if (y > 160) y = 160;
        const percent = 100 - (y / 160) * 100;
        state.throttle = percent / 100;
        throttleFill.style.height = percent + '%';
    }

    document.getElementById('joy-left').addEventListener('pointerdown', function () { leftPressed = true; });
    document.getElementById('joy-left').addEventListener('pointerup', function () { leftPressed = false; });
    document.getElementById('joy-left').addEventListener('pointerleave', function () { leftPressed = false; });
    document.getElementById('joy-right').addEventListener('pointerdown', function () { rightPressed = true; });
    document.getElementById('joy-right').addEventListener('pointerup', function () { rightPressed = false; });
    document.getElementById('joy-right').addEventListener('pointerleave', function () { rightPressed = false; });

    document.getElementById('btn-legs').onclick = function () {
        state.legsDeployed = !state.legsDeployed;
        this.innerText = state.legsDeployed ? "LEGS: DOWN" : "LEGS: UP";
        if (state.legsDeployed) this.classList.add('deployed');
        else this.classList.remove('deployed');
    };

    document.getElementById('btn-stage').onclick = function () {
        if (gameState !== "flight") return;

        const sideDecouplers = rocketParts.filter(function (p) { return p.type === 'decoupler' && Math.abs(p.x) > 10; });
        if (sideDecouplers.length > 0) {
            const dropX = sideDecouplers[0].x;
            rocketParts = rocketParts.filter(function (p) { return Math.abs(p.x - dropX) >= 5; });
        } else {
            const centerDec = rocketParts.filter(function (p) { return p.type === 'decoupler'; });
            if (centerDec.length === 0) return;
            centerDec.sort(function (a, b) { return a.y - b.y; });
            const lowest = centerDec[0];
            rocketParts = rocketParts.filter(function (p) { return p.y >= lowest.y; });
        }

        let m = 0, f = 0;
        rocketParts.forEach(function (p) { m += P[p.type].m; f += P[p.type].f; });
        state.dryMass = m;
        state.maxFuel = f;
        if (state.currentFuel > state.maxFuel) state.currentFuel = state.maxFuel;
        computeRocketCenter();
        updateStats();
    };

    const planetsMap = [
        { name: "Earth",   color: "#4a90e2", x: 0.20 },
        { name: "Moon",    color: "#9ca3af", x: 0.40 },
        { name: "Mars",    color: "#ea580c", x: 0.60 },
        { name: "Jupiter", color: "#d4a373", x: 0.80 }
    ];

    function drawMap() {
        mapCtx.setTransform(1, 0, 0, 1, 0, 0);
        mapCtx.fillStyle = "#000511";
        mapCtx.fillRect(0, 0, mapCanvas.width, mapCanvas.height);

        mapCtx.fillStyle = "#ffffff";
        for (let i = 0; i < 140; i++) {
            const sx = (i * 137.508) % mapCanvas.width;
            const sy = (i * 91.7) % mapCanvas.height;
            mapCtx.globalAlpha = 0.15 + ((i * 37) % 100) / 180;
            mapCtx.fillRect(sx, sy, 1.5, 1.5);
        }
        mapCtx.globalAlpha = 1;

        mapCtx.strokeStyle = "rgba(255,255,255,0.15)";
        mapCtx.lineWidth = 1;
        mapCtx.beginPath();
        mapCtx.moveTo(0, mapCanvas.height / 2);
        mapCtx.lineTo(mapCanvas.width, mapCanvas.height / 2);
        mapCtx.stroke();

        mapCtx.textAlign = "center";
        planetsMap.forEach(function (p) {
            const cx = p.x * mapCanvas.width;
            const cy = mapCanvas.height / 2;

            const g = mapCtx.createRadialGradient(cx - 9, cy - 9, 3, cx, cy, 26);
            g.addColorStop(0, "#ffffff");
            g.addColorStop(0.25, p.color);
            g.addColorStop(1, p.color);

            mapCtx.fillStyle = g;
            mapCtx.beginPath();
            mapCtx.arc(cx, cy, 24, 0, Math.PI * 2);
            mapCtx.fill();

            if (p.name === state.currentPlanet) {
                mapCtx.strokeStyle = "#00ffcc";
                mapCtx.lineWidth = 3;
                mapCtx.beginPath();
                mapCtx.arc(cx, cy, 33, 0, Math.PI * 2);
                mapCtx.stroke();
            }

            mapCtx.fillStyle = "#ffffff";
            mapCtx.font = "16px Arial";
            mapCtx.fillText(p.name, cx, cy + 52);
        });
    }

    document.getElementById('btn-map').onclick = function () {
        if (gameState !== "flight" && gameState !== "crashed") return;
        if (mapOverlay.style.display === 'block') {
            mapOverlay.style.display = 'none';
        } else {
            mapOverlay.style.display = 'block';
            drawMap();
        }
    };

    mapCanvas.addEventListener('pointerdown', function (e) {
        const rect = mapCanvas.getBoundingClientRect();
        const mx = e.clientX - rect.left;
        const my = e.clientY - rect.top;

        planetsMap.forEach(function (p) {
            const cx = p.x * mapCanvas.width;
            const cy = mapCanvas.height / 2;
            if (Math.hypot(mx - cx, my - cy) < 48) {
                warpTravel(p.name);
            }
        });
    });

    /* Warp with a flash effect */
    function warpTravel(name) {
        if (name === state.currentPlanet && state.y < 10) {
            mapOverlay.style.display = 'none';
            showStatus("ALREADY HERE", "#ffaa00", 1.5);
            return;
        }
        const flash = document.getElementById('warp-flash');
        flash.classList.add('active');
        mapOverlay.style.display = 'none';
        setTimeout(function () {
            travelTo(name);
            setTimeout(function () {
                flash.classList.remove('active');
            }, 120);
        }, 380);
    }

    function travelTo(name) {
        state.currentPlanet = name;
        state.x = 0;
        state.y = 0;
        state.vx = 0;
        state.vy = 0;
        state.angle = 0;
        state.angularVelocity = 0;
        state.throttle = 0;
        state.chuteDeployed = false;
        state.hasLiftedOff = false;
        state.onGround = true;
        state.legsDeployed = false;
        state.legsProgress = 0;
        state.cameraX = 0;
        state.cameraY = 0;
        state.particles = [];
        state.shake = 0;

        state.currentFuel = state.maxFuel;
        throttleFill.style.height = '0%';

        computeRocketCenter();

        const legsBtn = document.getElementById('btn-legs');
        legsBtn.innerText = "LEGS: UP";
        legsBtn.classList.remove('deployed');

        if (gameState === "crashed") {
            gameState = "flight";
            rebuildBtn.style.display = 'none';
            document.getElementById('status-msg').style.display = 'none';
        }

        document.getElementById('hud-planet').innerText = name;
        showStatus("WARPED TO " + name.toUpperCase(), "#00ffcc", 2.5);
    }

    document.getElementById('btn-launch').onclick = function (e) {
        e.stopPropagation();
        if (gameState !== "vab") return;

        if (rocketParts.length === 0) {
            showStatus("BUILD A ROCKET FIRST", "#ff4444", 2);
            return;
        }

        let minY = Infinity;
        rocketParts.forEach(function (p) { minY = Math.min(minY, p.y - P[p.type].h / 2); });
        rocketParts.forEach(function (p) { p.y -= minY; });

        computeRocketCenter();

        gameState = "flight";

        state.currentPlanet = "Earth";
        state.x = 0; state.y = 0;
        state.vx = 0; state.vy = 0;
        state.angle = 0; state.angularVelocity = 0;
        state.throttle = 0;
        state.legsDeployed = false; state.legsProgress = 0;
        state.chuteDeployed = false;
        state.hasLiftedOff = false;
        state.onGround = true;
        state.cameraX = 0; state.cameraY = 0;
        state.shake = 0;
        state.particles = [];

        let m = 0, f = 0;
        rocketParts.forEach(function (p) { m += P[p.type].m; f += P[p.type].f; });
        state.dryMass = m;
        state.maxFuel = f;
        state.currentFuel = f;
        state.totalMass = m + f;

        document.getElementById('vab-menu').style.display = 'none';
        document.getElementById('vab-stats').style.display = 'none';
        document.getElementById('top-bar').style.display = 'none';
        document.getElementById('trash-can').style.display = 'none';

        document.getElementById('hud').style.display = 'block';
        document.getElementById('hud-planet').innerText = "Earth";
        document.getElementById('minimap-container').style.display = 'block';
        document.getElementById('throttle-zone').style.display = 'block';
        document.getElementById('arrow-zone').style.display = 'flex';
        document.getElementById('btn-legs').style.display = 'block';
        document.getElementById('btn-stage').style.display = 'block';
        document.getElementById('btn-map').style.display = 'block';

        throttleFill.style.height = '0%';
        statusEl.style.display = 'none';
        rebuildBtn.style.display = 'none';
        mapOverlay.style.display = 'none';

        document.getElementById('btn-legs').innerText = "LEGS: UP";
        document.getElementById('btn-legs').classList.remove('deployed');

        updateHUD();
    };

    document.getElementById('btn-reset').onclick = function () { window.location.reload(); };
    rebuildBtn.onclick = function () { window.location.reload(); };

    function updateParticles(dt) {
        for (let i = state.particles.length - 1; i >= 0; i--) {
            const p = state.particles[i];
            p.x += p.vx * dt;
            p.y += p.vy * dt;
            p.vy -= 200 * dt;
            p.vx *= Math.pow(0.35, dt);
            p.vy *= Math.pow(0.6, dt);
            p.life -= dt * 1.1;
            if (p.life <= 0) state.particles.splice(i, 1);
        }
    }

    function crash() {
        gameState = "crashed";
        state.shake = 30;

        for (let i = 0; i < 90; i++) {
            let col = "255,100,0";
            const r = Math.random();
            if (r > 0.85) col = "255,255,0";
            else if (r > 0.55) col = "255,50,0";

            state.particles.push({
                x: state.x + (Math.random() - 0.5) * 30,
                y: state.y + (Math.random() - 0.5) * 30,
                vx: (Math.random() - 0.5) * 400,
                vy: (Math.random() - 0.5) * 400,
                life: 1.0 + Math.random(),
                size: Math.random() * 15 + 5,
                color: col
            });
        }
        for (let i = 0; i < 45; i++) {
            state.particles.push({
                x: state.x + (Math.random() - 0.5) * 40,
                y: state.y + (Math.random() - 0.5) * 40,
                vx: (Math.random() - 0.5) * 100,
                vy: (Math.random() - 0.5) * 100 - 50,
                life: 2.0 + Math.random() * 2,
                size: Math.random() * 30 + 15,
                color: "100,100,100"
            });
        }

        showStatus("💥 CRASHED", "#ff4444", 0);
        rebuildBtn.style.display = 'block';
    }

    function updatePhysics(dt) {
        if (gameState === "crashed") {
            updateParticles(dt);
            state.shake = Math.max(0, state.shake - 50 * dt);
            state.cameraX += (state.x - state.cameraX) * Math.min(1, 8 * dt);
            state.cameraY += (state.y - state.cameraY) * Math.min(1, 8 * dt);
            return;
        }
        if (gameState !== "flight") return;

        if (leftPressed) state.angularVelocity -= 120 * dt;
        if (rightPressed) state.angularVelocity += 120 * dt;
        if (!leftPressed && !rightPressed) {
            state.angularVelocity *= Math.pow(0.02, dt);
        }
        state.angularVelocity = Math.max(-90, Math.min(90, state.angularVelocity));
        state.angle += state.angularVelocity * dt;

        let thrust = 0;
        rocketParts.forEach(function (p) { thrust += P[p.type].t; });

        state.totalMass = state.dryMass + state.currentFuel;
        const g = planetsDB[state.currentPlanet].g;

        let ay = -g;
        let ax = 0;

        if (state.throttle > 0 && state.currentFuel > 0 && thrust > 0) {
            state.hasLiftedOff = true;

            const a = (thrust * 1000 * state.throttle) / Math.max(1, state.totalMass);
            const rad = state.angle * Math.PI / 180;
            ax += a * Math.sin(rad);
            ay += a * Math.cos(rad);

            state.currentFuel -= 50 * state.throttle * dt;
            if (state.currentFuel <= 0) {
                state.currentFuel = 0;
                state.throttle = 0;
                throttleFill.style.height = '0%';
                showStatus("OUT OF FUEL", "#ffaa00", 2);
            }

            const cosA = Math.cos(rad);
            const sinA = Math.sin(rad);

            /* Particle spawn using centre-of-mass pivot */
            rocketParts.forEach(function (eng) {
                if (eng.type.indexOf("engine") === -1) return;

                const hw = P[eng.type].w;
                const exBottom = eng.y - P[eng.type].h / 2;
                const dxScreen = eng.x;
                const dyScreen = state.rocketCenterY - exBottom;
                const dxRot = dxScreen * cosA - dyScreen * sinA;
                const dyRot = dxScreen * sinA + dyScreen * cosA;
                const wx = state.x + dxRot;
                const wy = state.y + state.rocketCenterY - dyRot;

                for (let i = 0; i < 3; i++) {
                    state.particles.push({
                        x: wx + (Math.random() - 0.5) * hw,
                        y: wy + (Math.random() - 0.5) * 4,
                        vx: -sinA * 140 + (Math.random() - 0.5) * 50,
                        vy: -cosA * 140 + (Math.random() - 0.5) * 50,
                        life: 1.0,
                        size: Math.random() * 12 + 5,
                        color: "255,150,0"
                    });
                }
            });
        }

        if (state.hasLiftedOff && state.y < 3000 && state.vy < -10 && !state.chuteDeployed) {
            if (rocketParts.some(function (p) { return p.type === 'chute'; })) {
                state.chuteDeployed = true;
            }
        }

        state.vx += ax * dt;
        state.vy += ay * dt;

        if (state.chuteDeployed) {
            if (state.vy < -8) state.vy = Math.min(-8, state.vy + 60 * dt);
            state.vx *= Math.pow(0.25, dt);
        }

        state.x += state.vx * dt;
        state.y += state.vy * dt;

        if (state.y <= 0) {
            state.y = 0;

            if (!state.onGround) {
                state.onGround = true;

                const impact = Math.abs(state.vy);
                const safeSpeed = state.chuteDeployed ? 999 : (state.legsDeployed ? 15 : 8);

                if (state.hasLiftedOff && impact > safeSpeed) {
                    state.vy = 0;
                    state.vx = 0;
                    crash();
                } else {
                    state.vy = 0;
                    state.vx = 0;
                    state.throttle = 0;
                    throttleFill.style.height = '0%';
                    if (state.hasLiftedOff) {
                        showStatus("🏆 LANDED SAFELY", "#00ffcc", 3);
                        rebuildBtn.style.display = 'block';
                    }
                }
            }

            if (state.vy < 0) state.vy = 0;
            state.vx *= Math.pow(0.01, dt);
        } else {
            state.onGround = false;
        }

        state.cameraX += (state.x - state.cameraX) * Math.min(1, 8 * dt);
        state.cameraY += (state.y - state.cameraY) * Math.min(1, 8 * dt);

        if (state.legsDeployed && state.legsProgress < 1) state.legsProgress = Math.min(1, state.legsProgress + 2 * dt);
        if (!state.legsDeployed && state.legsProgress > 0) state.legsProgress = Math.max(0, state.legsProgress - 2 * dt);

        updateParticles(dt);
        state.shake = Math.max(0, state.shake - 50 * dt);
    }

    function updateHUD() {
        document.getElementById('val-alt').innerText = state.y.toFixed(1);
        document.getElementById('val-vel').innerText = Math.hypot(state.vx, state.vy).toFixed(1);

        const fp = state.maxFuel > 0 ? (state.currentFuel / state.maxFuel) * 100 : 0;
        const fuelEl = document.getElementById('val-fuel');
        fuelEl.innerText = fp.toFixed(1);
        fuelEl.style.color = fp < 20 ? "#ff4444" : "#00ffcc";

        const planet = planetsDB[state.currentPlanet];
        const spaceEl = document.getElementById('hud-space');
        if (planet.atmo > 0 && state.y > planet.atmo) {
            spaceEl.style.display = 'block';
        } else if (planet.atmo === 0) {
            spaceEl.style.display = 'block';
        } else {
            spaceEl.style.display = 'none';
        }
    }

    function drawPart(p, py) {
        const w = P[p.type].w, h = P[p.type].h;
        ctx.save();
        ctx.translate(p.x, py);

        if (p.type === "pod") {
            ctx.fillStyle = "#888";
            ctx.beginPath();
            ctx.moveTo(-w / 2, h / 2);
            ctx.lineTo(w / 2, h / 2);
            ctx.lineTo(w / 3, -h / 2);
            ctx.lineTo(-w / 3, -h / 2);
            ctx.fill();
            ctx.fillStyle = "#222";
            ctx.beginPath();
            ctx.arc(0, 0, w / 4, 0, Math.PI * 2);
            ctx.fill();

        } else if (p.type === "chute") {
            if (!state.chuteDeployed) {
                ctx.fillStyle = "#555";
                ctx.fillRect(-w / 3, -h / 2, w / 1.5, h);
            }

        } else if (p.type === "nose") {
            ctx.fillStyle = "#fff";
            ctx.beginPath();
            ctx.moveTo(-w / 2, h / 2);
            ctx.lineTo(w / 2, h / 2);
            ctx.lineTo(0, -h / 2);
            ctx.fill();

        } else if (p.type.indexOf("tank") !== -1) {
            const grad = ctx.createLinearGradient(-w / 2, 0, w / 2, 0);
            grad.addColorStop(0, "#aaa");
            grad.addColorStop(0.5, "#fff");
            grad.addColorStop(1, "#888");
            ctx.fillStyle = grad;
            ctx.fillRect(-w / 2, -h / 2, w, h);

        } else if (p.type.indexOf("engine") !== -1) {
            ctx.fillStyle = "#222";
            ctx.beginPath();
            ctx.moveTo(-w / 3, -h / 2);
            ctx.lineTo(w / 3, -h / 2);
            ctx.lineTo(w / 2, h / 2);
            ctx.lineTo(-w / 2, h / 2);
            ctx.fill();

            if (state.throttle > 0 && state.currentFuel > 0 && gameState === "flight") {
                const flameLen = 40 + Math.random() * 55 * state.throttle;

                /* Outer flame (orange) */
                const fg = ctx.createLinearGradient(0, h / 2, 0, h / 2 + flameLen);
                fg.addColorStop(0, "rgba(255,255,255,1)");
                fg.addColorStop(0.3, "rgba(255,220,0,0.95)");
                fg.addColorStop(0.65, "rgba(255,110,0,0.65)");
                fg.addColorStop(1, "rgba(255,0,0,0)");
                ctx.fillStyle = fg;
                ctx.beginPath();
                ctx.moveTo(-w / 2.4, h / 2);
                ctx.lineTo(w / 2.4, h / 2);
                ctx.lineTo(0, h / 2 + flameLen);
                ctx.fill();

                /* Inner flame (white core) */
                const coreLen = flameLen * 0.6;
                const cg = ctx.createLinearGradient(0, h / 2, 0, h / 2 + coreLen);
                cg.addColorStop(0, "rgba(255,255,255,1)");
                cg.addColorStop(0.5, "rgba(255,255,190,0.9)");
                cg.addColorStop(1, "rgba(255,210,0,0)");
                ctx.fillStyle = cg;
                ctx.beginPath();
                ctx.moveTo(-w / 4.5, h / 2);
                ctx.lineTo(w / 4.5, h / 2);
                ctx.lineTo(0, h / 2 + coreLen);
                ctx.fill();
            }

        } else if (p.type === "decoupler") {
            ctx.fillStyle = "#5c3a21";
            ctx.fillRect(-w / 2, -h / 2, w, h);

        } else if (p.type === "booster") {
            ctx.fillStyle = "#ddd";
            ctx.fillRect(-w / 2, -h / 2, w, h);

        } else if (p.type === "legs") {
            ctx.fillStyle = "#555";
            ctx.fillRect(-w / 2, -h / 2, w, h);
        }

        ctx.restore();
    }

    function drawVAB() {
        ctx.setTransform(1, 0, 0, 1, 0, 0);

        ctx.fillStyle = "#2b3a4a";
        ctx.fillRect(0, 0, W, H);

        const v = vabView();
        ctx.save();
        ctx.translate(v.ox, v.oy);
        ctx.scale(v.sc, v.sc);

        ctx.strokeStyle = "rgba(255,255,255,0.07)";
        ctx.lineWidth = 1;
        ctx.beginPath();
        for (let i = -60; i <= 60; i++) {
            ctx.moveTo(i * GRID, -3000);
            ctx.lineTo(i * GRID, 100);
            ctx.moveTo(-600, i * GRID);
            ctx.lineTo(600, i * GRID);
        }
        ctx.stroke();

        ctx.fillStyle = "#444";
        ctx.fillRect(-220, 0, 440, 10);

        rocketParts.forEach(function (p) { drawPart(p, -p.y); });
        ctx.restore();
    }

    function drawFlight() {
        ctx.setTransform(1, 0, 0, 1, 0, 0);

        const planet = planetsDB[state.currentPlanet];

        const alt = Math.max(0, state.y);
        let t = planet.atmo > 0 ? Math.min(1, alt / planet.atmo) : 1;
        t = Math.pow(t, 0.6);

        const r0 = Math.round(planet.sky[0] * (1 - Math.min(1, t * 1.15)));
        const g0 = Math.round(planet.sky[1] * (1 - Math.min(1, t * 1.15)));
        const b0 = Math.round(planet.sky[2] * (1 - Math.min(1, t * 1.15)));

        const r1 = Math.round(planet.sky[0] * (1 - t));
        const g1 = Math.round(planet.sky[1] * (1 - t));
        const b1 = Math.round(planet.sky[2] * (1 - t));

        const skyGrad = ctx.createLinearGradient(0, 0, 0, H);
        skyGrad.addColorStop(0, "rgb(" + r0 + "," + g0 + "," + b0 + ")");
        skyGrad.addColorStop(1, "rgb(" + r1 + "," + g1 + "," + b1 + ")");
        ctx.fillStyle = skyGrad;
        ctx.fillRect(0, 0, W, H);

        if (t > 0.04) {
            const px = state.cameraX * 0.04;
            const py = state.cameraY * 0.04;
            ctx.fillStyle = "#ffffff";
            for (let i = 0; i < stars.length; i++) {
                const s = stars[i];
                const sx = ((s.x - px) % W + W) % W;
                const sy = ((s.y + py) % H + H) % H;
                ctx.globalAlpha = t * s.a;
                ctx.beginPath();
                ctx.arc(sx, sy, s.size, 0, Math.PI * 2);
                ctx.fill();
            }
            ctx.globalAlpha = 1;
        }

        const zoom = Math.max(0.55, 1.1 - state.y / 25000);

        ctx.save();
        ctx.translate(W / 2, H * 0.68);
        ctx.scale(zoom, zoom);
        ctx.translate(-state.cameraX, state.cameraY);

        const R = 50000;
        ctx.fillStyle = planet.ground;
        ctx.beginPath();
        ctx.arc(0, R, R, 0, Math.PI * 2);
        ctx.fill();

        if (planet.surface) {
            for (let i = 0; i < planet.surface.length; i++) {
                const f = planet.surface[i];
                const sy = R - Math.sqrt(Math.max(0, R * R - f.x * f.x));
                ctx.fillStyle = f.light
                    ? "rgba(255,255,255," + f.a + ")"
                    : "rgba(0,0,0," + f.a + ")";
                ctx.beginPath();
                ctx.ellipse(f.x, sy + f.h * 0.5, f.w * 0.5, f.h * 0.5, 0, 0, Math.PI * 2);
                ctx.fill();
            }
        }

        ctx.strokeStyle = "rgba(255,255,255,0.18)";
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(0, R, R, -Math.PI / 2 - 0.35, -Math.PI / 2 + 0.35);
        ctx.stroke();

        for (let i = 0; i < state.particles.length; i++) {
            const p = state.particles[i];
            const life = Math.max(0, p.life);
            ctx.fillStyle = "rgba(" + p.color + "," + life + ")";
            ctx.beginPath();
            ctx.arc(p.x, -p.y, Math.max(0.5, p.size * life), 0, Math.PI * 2);
            ctx.fill();
        }

        if (gameState !== "crashed") {
            /* ---- ROTATE AROUND CENTRE OF MASS ---- */
            ctx.save();
            ctx.translate(state.x, -(state.y + state.rocketCenterY));
            ctx.rotate(state.angle * Math.PI / 180);

            rocketParts.forEach(function (p) {
                drawPart(p, -(p.y - state.rocketCenterY));
            });

            if (state.legsProgress > 0) {
                const legLen = 22 * state.legsProgress;
                const legsBase = -(0 - state.rocketCenterY);
                ctx.strokeStyle = "#888";
                ctx.lineWidth = 4;
                ctx.beginPath();
                ctx.moveTo(-6, legsBase);
                ctx.lineTo(-6 - legLen, legsBase + legLen);
                ctx.moveTo(6, legsBase);
                ctx.lineTo(6 + legLen, legsBase + legLen);
                ctx.stroke();
            }

            if (state.chuteDeployed) {
                const chuteTop = -(120 - state.rocketCenterY);
                ctx.strokeStyle = "#fff";
                ctx.lineWidth = 1;
                ctx.beginPath();
                ctx.moveTo(-15, chuteTop);
                ctx.lineTo(-5, chuteTop + 60);
                ctx.stroke();
                ctx.beginPath();
                ctx.moveTo(15, chuteTop);
                ctx.lineTo(5, chuteTop + 60);
                ctx.stroke();

                ctx.fillStyle = "#f44";
                ctx.beginPath();
                ctx.arc(0, chuteTop, 30, Math.PI, 0);
                ctx.fill();
                ctx.fillStyle = "#fff";
                ctx.beginPath();
                ctx.arc(0, chuteTop, 30, Math.PI, Math.PI * 1.3);
                ctx.fill();
                ctx.beginPath();
                ctx.arc(0, chuteTop, 30, Math.PI * 1.6, Math.PI * 2);
                ctx.fill();
            }

            ctx.restore();
        }

        ctx.restore();

        drawMinimap();
    }

    function drawMinimap() {
        minimapCtx.setTransform(1, 0, 0, 1, 0, 0);
        minimapCtx.fillStyle = "#001018";
        minimapCtx.fillRect(0, 0, 80, 80);

        minimapCtx.fillStyle = planetsDB[state.currentPlanet].ground;
        minimapCtx.fillRect(0, 72, 80, 8);

        const altN = Math.min(1, Math.max(0, state.y) / 5000);
        const ry = 70 - altN * 55;

        minimapCtx.fillStyle = "#00ffcc";
        minimapCtx.beginPath();
        minimapCtx.arc(40, ry, 3, 0, Math.PI * 2);
        minimapCtx.fill();
    }

    function draw() {
        if (gameState === "menu") return;

        if (state.shake > 0) {
            ctx.setTransform(1, 0, 0, 1, 0, 0);
            ctx.clearRect(0, 0, W, H);
            ctx.save();
            ctx.translate((Math.random() - 0.5) * state.shake, (Math.random() - 0.5) * state.shake);
            if (gameState === "vab") drawVAB(); else drawFlight();
            ctx.restore();
            ctx.setTransform(1, 0, 0, 1, 0, 0);
        } else {
            if (gameState === "vab") drawVAB();
            else drawFlight();
        }
    }

    function loop(time) {
        let dt = (time - state.lastTime) / 1000;
        state.lastTime = time;
        if (dt > 0.05) dt = 0.05;

        if (gameState === "flight" || gameState === "crashed") {
            updatePhysics(dt);
            updateHUD();
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
