import streamlit as st
import streamlit.components.v1 as components
import base64
import os

st.set_page_config(page_title="Artemis II | Deep Space", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    .block-container { padding: 0rem !important; margin: 0rem !important; max-width: 100% !important; }
    header {visibility: hidden;}
    iframe { border: none; }
</style>
""", unsafe_allow_html=True)

model_path = "artemis_ii.glb"
glb_base64 = ""
if os.path.exists(model_path):
    with open(model_path, "rb") as f:
        glb_base64 = base64.b64encode(f.read()).decode('utf-8')

html_template = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body { margin: 0; overflow: hidden; background-color: #000; font-family: 'Courier New', monospace; touch-action: none; user-select: none; }
        canvas { display: block; touch-action: none; }
        #ui-layer { position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 9999; }
        
        #hud { position: absolute; top: 10px; left: 10px; color: #38bdf8; text-shadow: 0 0 5px #38bdf8; font-size: 14px; background: rgba(0,0,0,0.7); padding: 12px; border-radius: 5px; border: 1px solid #38bdf8;}
        #mission { position: absolute; top: 10px; left: 50%; transform: translateX(-50%); color: #fbbf24; text-align: center; font-size: 16px; font-weight: bold; text-shadow: 0 0 8px black; width: 60%;}
        
        #heat-warning { position: absolute; top: 110px; left: 10px; color: #ef4444; font-weight: bold; font-size: 16px; display: none; animation: flash 0.5s infinite; }
        
        #warning-overlay { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(255, 0, 0, 0.3); z-index: 9998; display: none; animation: flash 0.5s infinite; pointer-events: none;}
        @keyframes flash { 0% { opacity: 0.1; } 50% { opacity: 0.4; } 100% { opacity: 0.1; } }
        
        #minimap-container { position: absolute; top: 10px; right: 10px; width: 120px; height: 120px; border: 2px solid #38bdf8; border-radius: 50%; background: rgba(0,0,0,0.8); overflow: hidden; box-shadow: 0 0 15px rgba(56,189,248,0.3);}
        #minimap { width: 100%; height: 100%; }

        #joystick-zone { position: absolute; top: 40%; left: 20px; width: 110px; height: 110px; background: rgba(255,255,255,0.15); border: 2px solid #38bdf8; border-radius: 50%; pointer-events: auto; touch-action: none; display: none;}
        #joystick-knob { position: absolute; top: 30px; left: 30px; width: 46px; height: 46px; background: #38bdf8; border-radius: 50%; box-shadow: 0 0 10px #fff; }
        
        #throttle-zone { position: absolute; top: 40%; right: 20px; width: 45px; height: 160px; background: rgba(255,255,255,0.15); border: 2px solid #ef4444; border-radius: 20px; pointer-events: auto; touch-action: none; display: none;}
        #throttle-fill { position: absolute; bottom: 0; left: 0; width: 100%; height: 0%; background: #ef4444; border-radius: 18px;}
        
        .action-btn { position: absolute; pointer-events: auto; background: rgba(0,0,0,0.8); color: white; border: 2px solid #38bdf8; padding: 10px; border-radius: 8px; font-family: inherit; font-weight: bold; font-size: 12px; display: none; z-index: 10000; }
        #btn-gear { top: 40%; right: 80px; color: #22c55e; border-color: #22c55e; }
        #btn-retro { top: 48%; right: 80px; color: #f59e0b; border-color: #f59e0b; }
        #btn-reset { top: 40%; left: 140px; color: #ef4444; border-color: #ef4444; }
        #btn-camera { top: 56%; right: 80px; color: #38bdf8; border-color: #38bdf8; width: 85px; }
        
        #victory-overlay { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.85); z-index: 999999; display: none; flex-direction: column; justify-content: center; align-items: center; pointer-events: auto; }
        .victory-text { color: #22c55e; font-size: 32px; font-weight: bold; text-transform: uppercase; letter-spacing: 3px; text-align: center; text-shadow: 0 0 30px #22c55e; animation: pulse 1.5s infinite; }
        .victory-sub { color: #fff; font-size: 16px; margin-top: 20px; text-align: center;}

        #loading { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: #000; color: #38bdf8; display: flex; justify-content: center; align-items: center; font-size: 24px; z-index: 100; transition: opacity 1s; }
        #start-overlay { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(2, 6, 23, 0.85); z-index: 99999; display: flex; flex-direction: column; justify-content: center; align-items: center; pointer-events: auto; cursor: pointer; }
        .start-text { color: #38bdf8; font-size: 24px; font-weight: bold; text-transform: uppercase; letter-spacing: 3px; text-align: center; text-shadow: 0 0 20px #38bdf8; animation: pulse 2s infinite; }
        @keyframes pulse { 0% { opacity: 0.5; } 50% { opacity: 1; } 100% { opacity: 0.5; } }
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>
    <div id="loading">INITIALIZING DEEP SPACE...</div>
    
    <div id="start-overlay">
        <div class="start-text">TAP ANYWHERE<br>TO<br>ENTER COCKPIT</div>
    </div>
    
    <div id="warning-overlay"></div>

    <div id="victory-overlay">
        <div class="victory-text">🏆 SAFE LANDING</div>
        <div class="victory-sub">You survived the descent.<br>Tap RESET to fly again.</div>
    </div>

    <div id="ui-layer">
        <div id="hud">
            ALT: <span id="val-alt">0</span> km<br>
            SPEED: <span id="val-vel">0</span> km/h<br>
            FUEL: <span id="val-fuel">100</span>%<br>
            HULL: <span id="val-hull" style="color: #22c55e;">100</span>%<br>
            <span style="color:white">ZONE: <span id="val-zone">Earth</span></span>
        </div>
        <div id="mission">Awaiting Launch...</div>
        <div id="heat-warning">⚠️ ENGINE OVERHEATING</div>
        
        <div id="minimap-container"><canvas id="minimap" width="120" height="120"></canvas></div>
        
        <div id="joystick-zone"><div id="joystick-knob"></div></div>
        <div id="throttle-zone"><div id="throttle-fill"></div></div>
        
        <button class="action-btn" id="btn-gear">GEAR: UP</button>
        <button class="action-btn" id="btn-retro">RETRO</button>
        <button class="action-btn" id="btn-camera">CAM: CHASE</button>
        <button class="action-btn" id="btn-reset">RESET</button>
    </div>

    <script>
        let state = {
            x: 0, y: 1005, vx: 0, vy: 0, 
            rotation: 0, angularVelocity: 0, 
            fuel: 100, throttle: 0, hull: 100,
            engineHeat: 0, engineStalled: false,
            gear: false, exploded: false, started: false, phase: 1, won: false,
            cameraMode: "chase" 
        };

        const G = 50; 
        const ROCKET_MASS = 1;
        const MAX_THRUST = 20; 
        
        const planets = [
            { name: "Earth", x: 0, y: 0, r: 1000, m: 50000, color: 0x1e3a8a, atmo: 0x38bdf8, safeSpeed: 5 },
            { name: "Moon", x: 10000, y: 3000, r: 300, m: 500, color: 0x9ca3af, atmo: 0x000000, safeSpeed: 5 },
            { name: "Mars", x: -20000, y: -5000, r: 600, m: 6000, color: 0xea580c, atmo: 0xffaa00, safeSpeed: 5 }
        ];

        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000000);
        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        document.body.appendChild(renderer.domElement);

        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;
        controls.enablePan = false; 
        controls.enabled = true; 

        const sunGeo = new THREE.SphereGeometry(500, 32, 32);
        const sunMat = new THREE.MeshBasicMaterial({color: 0xffdd00});
        const sun = new THREE.Mesh(sunGeo, sunMat);
        sun.position.set(0, -20000, 0);
        scene.add(sun);

        const sunLight = new THREE.PointLight(0xffffff, 2, 0, 1);
        sunLight.position.set(0, -20000, 0); 
        scene.add(sunLight);
        scene.add(new THREE.AmbientLight(0x404040));

        const starsGeo = new THREE.BufferGeometry();
        const starsPos = new Float32Array(10000 * 3);
        for(let i=0; i<10000*3; i++) starsPos[i] = (Math.random() - 0.5) * 100000;
        starsGeo.setAttribute('position', new THREE.BufferAttribute(starsPos, 3));
        scene.add(new THREE.Points(starsGeo, new THREE.PointsMaterial({color: 0xffffff, size: 5})));

        planets.forEach(p => {
            const geo = new THREE.SphereGeometry(p.r, 64, 64);
            const mat = new THREE.MeshStandardMaterial({color: p.color, roughness: 0.8});
            const mesh = new THREE.Mesh(geo, mat);
            mesh.position.set(p.x, p.y, 0);
            scene.add(mesh);

            if (p.atmo !== 0x000000) {
                const atmoGeo = new THREE.SphereGeometry(p.r * 1.05, 64, 64);
                const atmoMat = new THREE.MeshBasicMaterial({color: p.atmo, transparent: true, opacity: 0.2, side: THREE.BackSide});
                const atmo = new THREE.Mesh(atmoGeo, atmoMat);
                atmo.position.set(p.x, p.y, 0);
                scene.add(atmo);
            }
        });

        const asteroids = [];
        for(let i=0; i<40; i++) {
            let ax = 2000 + Math.random() * 6000;
            let ay = Math.random() * 5000;
            let radius = 20 + Math.random() * 50;
            
            const astGeo = new THREE.DodecahedronGeometry(radius, 0);
            const astMat = new THREE.MeshStandardMaterial({color: 0x888888, roughness: 1});
            const astMesh = new THREE.Mesh(astGeo, astMat);
            astMesh.position.set(ax, ay, 0);
            astMesh.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, 0);
            
            scene.add(astMesh);
            asteroids.push({ mesh: astMesh, x: ax, y: ay, r: radius });
        }

        const padGeo = new THREE.BoxGeometry(200, 20, 200);
        const padMat = new THREE.MeshStandardMaterial({color: 0x555555});
        const pad = new THREE.Mesh(padGeo, padMat);
        pad.position.set(0, 1010, 0);
        scene.add(pad);

        const rocketGroup = new THREE.Group();
        rocketGroup.position.set(0, 1020, 0);
        scene.add(rocketGroup);

        const particleCount = 200;
        const fireGeo = new THREE.BufferGeometry();
        const firePositions = new Float32Array(particleCount * 3);
        const fireVelocities = [];
        for (let i = 0; i < particleCount; i++) {
            firePositions[i*3] = 0; firePositions[i*3+1] = 0; firePositions[i*3+2] = 0;
            fireVelocities.push({ x: (Math.random() - 0.5) * 5, y: -Math.random() * 30 - 10, z: (Math.random() - 0.5) * 5 });
        }
        fireGeo.setAttribute('position', new THREE.BufferAttribute(firePositions, 3));
        const canvasFire = document.createElement('canvas');
        canvasFire.width = 16; canvasFire.height = 16;
        const ctx = canvasFire.getContext('2d');
        const gradient = ctx.createRadialGradient(8, 8, 0, 8, 8, 8);
        gradient.addColorStop(0, 'rgba(255, 255, 255, 1)');
        gradient.addColorStop(0.2, 'rgba(255, 200, 0, 1)');
        gradient.addColorStop(1, 'rgba(255, 0, 0, 0)');
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, 16, 16);
        const fireTexture = new THREE.CanvasTexture(canvasFire);
        const fireMaterial = new THREE.PointsMaterial({ size: 40, map: fireTexture, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false });
        const fireParticles = new THREE.Points(fireGeo, fireMaterial);
        fireParticles.position.y = -30; 
        fireParticles.visible = false;
        rocketGroup.add(fireParticles);

        const rcsGeo = new THREE.BufferGeometry();
        const rcsPositions = new Float32Array(50 * 3);
        const rcsVelocities = [];
        for (let i = 0; i < 50; i++) {
            rcsPositions[i*3] = 0; rcsPositions[i*3+1] = 0; rcsPositions[i*3+2] = 0;
            rcsVelocities.push({ x: (Math.random() - 0.5) * 10, y: (Math.random() - 0.5) * 10, z: 0 });
        }
        rcsGeo.setAttribute('position', new THREE.BufferAttribute(rcsPositions, 3));
        const rcsMaterial = new THREE.PointsMaterial({ size: 10, color: 0xffffff, transparent: true, opacity: 0.5 });
        const rcsParticles = new THREE.Points(rcsGeo, rcsMaterial);
        rcsParticles.visible = false;
        rocketGroup.add(rcsParticles);

        const base64String = "{{GLB_BASE64_PLACEHOLDER}}";
        if (base64String.length > 100) {
            const binaryString = atob(base64String);
            const bytes = new Uint8Array(binaryString.length);
            for (let i = 0; i < binaryString.length; i++) { bytes[i] = binaryString.charCodeAt(i); }
            
            const loader = new THREE.GLTFLoader();
            loader.parse(bytes.buffer, '', function (gltf) {
                const model = gltf.scene;
                const box = new THREE.Box3().setFromObject(model);
                const size = box.getSize(new THREE.Vector3());
                
                const scaleFactor = 200 / size.y; 
                model.scale.set(scaleFactor, scaleFactor, scaleFactor);
                
                const center = box.getCenter(new THREE.Vector3());
                model.position.x = -center.x * scaleFactor;
                model.position.z = -center.z * scaleFactor;
                model.position.y = (-box.min.y * scaleFactor); 
                rocketGroup.add(model);
                document.getElementById('loading').style.opacity = 0;
            });
        }

        const mapCanvas = document.getElementById('minimap');
        const mapCtx = mapCanvas.getContext('2d');

        function drawMinimap() {
            mapCtx.clearRect(0, 0, 120, 120);
            let scaleX = 120 / 80000;
            let scaleY = 120 / 40000;
            let centerX = 60; 
            let centerY = 60; 

            mapCtx.beginPath();
            mapCtx.arc(centerX, centerY + (20000 * scaleY), 5, 0, Math.PI * 2);
            mapCtx.fillStyle = '#ffdd00';
            mapCtx.fill();

            planets.forEach(p => {
                mapCtx.beginPath();
                let px = centerX + (p.x * scaleX);
                let py = centerY - (p.y * scaleY);
                mapCtx.arc(px, py, Math.max(2, p.r * scaleX * 2), 0, Math.PI * 2);
                mapCtx.fillStyle = '#' + p.color.toString(16).padStart(6, '0');
                mapCtx.fill();
            });

            // Minimap Arrow
            let rx = centerX + (state.x * scaleX);
            let ry = centerY - (state.y * scaleY);
            
            mapCtx.save();
            mapCtx.translate(rx, ry);
            mapCtx.rotate(-state.rotation); 
            
            mapCtx.beginPath();
            mapCtx.moveTo(0, -8); 
            mapCtx.lineTo(6, 6);  
            mapCtx.lineTo(0, 3);  
            mapCtx.lineTo(-6, 6); 
            mapCtx.closePath();
            mapCtx.fillStyle = '#ff0000';
            mapCtx.fill();
            mapCtx.restore();
        }

        let isDraggingJoy = false;
        let isDraggingThrottle = false;
        let joyX = 0; 

        const joyZone = document.getElementById('joystick-zone');
        const joyKnob = document.getElementById('joystick-knob');
        const throttleZone = document.getElementById('throttle-zone');
        const throttleFill = document.getElementById('throttle-fill');

        document.getElementById('start-overlay').addEventListener('pointerdown', function(e) {
            e.preventDefault(); 
            state.started = true;
            this.style.display = 'none';
            document.getElementById('joystick-zone').style.display = 'block';
            document.getElementById('throttle-zone').style.display = 'block';
            document.getElementById('btn-gear').style.display = 'block';
            document.getElementById('btn-retro').style.display = 'block';
            document.getElementById('btn-camera').style.display = 'block';
            document.getElementById('btn-reset').style.display = 'block';
            document.getElementById('mission').innerText = "Task: Launch and land on the Moon. Beware of asteroids!";
        });

        joyZone.addEventListener('pointerdown', (e) => { isDraggingJoy = true; joyZone.setPointerCapture(e.pointerId); });
        joyZone.addEventListener('pointerup', (e) => { isDraggingJoy = false; joyKnob.style.top = '30px'; joyKnob.style.left = '30px'; joyX = 0; });
        joyZone.addEventListener('pointermove', (e) => {
            if (!isDraggingJoy) return;
            const rect = joyZone.getBoundingClientRect();
            let x = e.clientX - rect.left - 55; let y = e.clientY - rect.top - 55;
            const dist = Math.sqrt(x*x + y*y);
            if (dist > 35) { x = (x/35)*35; y = (y/35)*35; }
            joyKnob.style.left = (30 + x) + 'px'; joyKnob.style.top = (30 + y) + 'px';
            joyX = x; 
        });

        throttleZone.addEventListener('pointerdown', (e) => { isDraggingThrottle = true; throttleZone.setPointerCapture(e.pointerId); });
        throttleZone.addEventListener('pointerup', () => { isDraggingThrottle = false; });
        throttleZone.addEventListener('pointermove', (e) => {
            if (!isDraggingThrottle) return;
            const rect = throttleZone.getBoundingClientRect();
            let y = e.clientY - rect.top;
            if (y < 0) y = 0; if (y > 160) y = 160;
            let percent = 100 - (y / 160) * 100;
            state.throttle = percent;
            throttleFill.style.height = percent + '%';
        });

        document.getElementById('btn-gear').onclick = function() {
            state.gear = !state.gear;
            this.innerText = "GEAR: " + (state.gear ? "DOWN" : "UP");
        };
        document.getElementById('btn-retro').onclick = function() {
            state.vx *= 0.7; state.vy *= 0.7;
        };
        
        document.getElementById('btn-camera').onclick = function() {
            if (state.cameraMode === "chase") {
                state.cameraMode = "orbit";
                this.innerText = "CAM: ORBIT";
            } else {
                state.cameraMode = "chase";
                this.innerText = "CAM: CHASE";
            }
        };

        document.getElementById('btn-reset').onclick = function() {
            state.x = 0; state.y = 1020; state.vx = 0; state.vy = 0; 
            state.rotation = 0; state.angularVelocity = 0; state.phase = 1;
            state.fuel = 100; state.throttle = 0; state.exploded = false; state.won = false; state.hull = 100;
            state.engineHeat = 0; state.engineStalled = false;
            rocketGroup.visible = true;
            rocketGroup.position.set(0, 1020, 0);
            throttleFill.style.height = '0%';
            document.getElementById('victory-overlay').style.display = 'none';
            document.getElementById('warning-overlay').style.display = 'none';
            document.getElementById('heat-warning').style.display = 'none';
            document.getElementById('val-hull').innerText = "100";
            document.getElementById('val-hull').style.color = "#22c55e";
            document.getElementById('mission').innerText = "Reset. Slide throttle up to launch.";
        };

        function updatePhysics() {
            if (!state.started || state.exploded || state.won) return;
            if (state.throttle === 0 && state.vy === 0 && state.vx === 0) return;

            let ax = 0, ay = 0;
            let currentZone = "Deep Space";
            let isInAtmosphere = false;
            let currentSpeed = Math.sqrt(state.vx*state.vx + state.vy*state.vy);

            // Engine Overheat
            if (state.throttle > 80 && !state.engineStalled) {
                state.engineHeat += 0.5;
                if (state.engineHeat > 100) {
                    state.engineStalled = true;
                    state.throttle = 0;
                    throttleFill.style.height = '0%';
                    state.engineHeat = 100;
                    document.getElementById('heat-warning').style.display = 'block';
                }
            } else {
                if (state.engineHeat > 0) state.engineHeat -= 0.2;
                if (state.engineHeat < 0) state.engineHeat = 0;
                if (!state.engineStalled) document.getElementById('heat-warning').style.display = 'none';
            }

            if (state.engineStalled) {
                if (state.engineHeat > 50) {
                    state.engineHeat -= 0.5;
                } else {
                    state.engineStalled = false;
                    document.getElementById('heat-warning').style.display = 'none';
                }
            }

            planets.forEach(p => {
                let dx = p.x - state.x;
                let dy = p.y - state.y;
                let distSq = dx*dx + dy*dy;
                let dist = Math.sqrt(distSq);
                if (dist < 10) dist = 10;

                // Check if in atmosphere (only near the planet)
                if (p.atmo !== 0x000000 && dist < p.r + 500) isInAtmosphere = true;
                if (dist < p.r * 3) currentZone = p.name + " Orbit";

                let accel = (G * p.m) / distSq;
                ax += accel * (dx / dist);
                ay += accel * (dy / dist);

                if (dist < p.r + 400) document.getElementById('warning-overlay').style.display = 'block';
                else document.getElementById('warning-overlay').style.display = 'none';

                if (dist < p.r) {
                    if (currentSpeed > p.safeSpeed) {
                        triggerExplosion("IMPACTED " + p.name.toUpperCase() + " AT HIGH SPEED");
                    } else if (!state.gear) {
                        triggerExplosion("CRUSHED ON " + p.name.toUpperCase() + " (GEAR UP)");
                    } else {
                        state.won = true;
                        document.getElementById('victory-overlay').style.display = 'flex';
                        state.vx = 0; state.vy = 0; state.throttle = 0;
                        document.getElementById('warning-overlay').style.display = 'none';
                    }
                }
            });

            asteroids.forEach(ast => {
                let dx = ast.x - state.x;
                let dy = ast.y - state.y;
                let dist = Math.sqrt(dx*dx + dy*dy);
                
                if (dist < ast.r + 50) { 
                    state.hull -= 2; 
                    document.getElementById('val-hull').innerText = Math.max(0, state.hull).toFixed(0);
                    document.getElementById('val-hull').style.color = "#ef4444";
                    state.vx *= -0.5; state.vy *= -0.5;
                    if (state.hull <= 0) triggerExplosion("DESTROYED BY ASTEROID IMPACT");
                }
            });

            // FIXED: HEAT ONLY APPLIES IF FALLING (vy < 0)
            if (isInAtmosphere && state.vy < 0 && currentSpeed > 8) {
                state.hull -= 0.5; 
                if (state.hull <= 0) triggerExplosion("BURNED UP IN ATMOSPHERE");
                document.getElementById('val-hull').innerText = Math.max(0, state.hull).toFixed(0);
                if (state.hull < 50) document.getElementById('val-hull').style.color = "#ef4444";
            }

            if (state.throttle > 0 && !state.engineStalled) {
                fireParticles.visible = true;
                const positions = fireParticles.geometry.attributes.position.array;
                for (let i = 0; i < particleCount; i++) {
                    if (positions[i*3+1] < -40) { positions[i*3] = 0; positions[i*3+1] = 0; positions[i*3+2] = 0; }
                    positions[i*3] += fireVelocities[i].x * (state.throttle/100);
                    positions[i*3+1] += fireVelocities[i].y * (state.throttle/100);
                    positions[i*3+2] += fireVelocities[i].z * (state.throttle/100);
                }
                fireParticles.geometry.attributes.position.needsUpdate = true;

                let thrustAccel = (MAX_THRUST * (state.throttle/100)) / ROCKET_MASS;
                ax += thrustAccel * Math.sin(state.rotation);
                ay += thrustAccel * Math.cos(state.rotation);

                state.fuel -= 0.1 * (state.throttle/100);
                if (state.fuel <= 0) { state.fuel = 0; state.throttle = 0; }
            } else {
                fireParticles.visible = false;
            }

            let torqueInput = joyX / 35; 
            let torquePower = 0.0015; 
            state.angularVelocity += torqueInput * torquePower;
            
            if (joyX !== 0) {
                rcsParticles.visible = true;
            } else {
                rcsParticles.visible = false;
                state.angularVelocity *= 0.90; 
                if (Math.abs(state.angularVelocity) < 0.0001) state.angularVelocity = 0;
            }
            
            if (state.angularVelocity > 0.03) state.angularVelocity = 0.03;
            if (state.angularVelocity < -0.03) state.angularVelocity = -0.03;
            state.rotation += state.angularVelocity;

            state.vx += ax * 0.1;
            state.vy += ay * 0.1;
            state.x += state.vx * 0.1;
            state.y += state.vy * 0.1;

            let distToEarth = Math.sqrt(state.x*state.x + state.y*state.y);
            if (distToEarth < 1005 && !state.won) {
                let angle = Math.atan2(state.y, state.x);
                state.x = Math.cos(angle) * 1005;
                state.y = Math.sin(angle) * 1005;
                state.vx = 0; state.vy = 0; 
                state.throttle = 0; 
                throttleFill.style.height = '0%';
                fireParticles.visible = false;
            }

            if (state.phase === 1 && distToEarth > 2000) {
                document.getElementById('mission').innerText = "Task: Fly to the Moon. Avoid the grey asteroids!";
                state.phase = 2;
            }

            document.getElementById('val-alt').innerText = Math.max(0, (distToEarth - 1000)).toFixed(1);
            document.getElementById('val-vel').innerText = (currentSpeed * 10).toFixed(0); 
            document.getElementById('val-fuel').innerText = state.fuel.toFixed(1);
            document.getElementById('val-zone').innerText = currentZone;

            if (state.fuel <= 0 && currentSpeed < 0.1 && currentZone === "Deep Space") {
                triggerExplosion("STRANDED IN SPACE (OUT OF FUEL)");
            }
        }

        function triggerExplosion(reason) {
            state.exploded = true;
            document.getElementById('mission').innerText = "💥 FAILED: " + reason;
            rocketGroup.visible = false;
            document.getElementById('warning-overlay').style.display = 'none';
            document.getElementById('heat-warning').style.display = 'none';
        }

        function animate() {
            requestAnimationFrame(animate);
            updatePhysics();
            drawMinimap();

            if (!state.exploded && !state.won) {
                rocketGroup.position.set(state.x, state.y, 0);
                rocketGroup.rotation.z = -state.rotation; 
            }

            let distToEarth = Math.sqrt(state.x*state.x + state.y*state.y);

            if (state.cameraMode === "chase") {
                let distanceInFront = 400; 
                
                let camX = state.x + Math.sin(state.rotation) * distanceInFront;
                let camY = state.y + Math.cos(state.rotation) * distanceInFront;
                
                camera.position.x += (camX - camera.position.x) * 0.1; 
                camera.position.y += (camY - camera.position.y) * 0.1;
                
                let targetZoom = 350 + (distToEarth * 0.05);
                if (targetZoom > 800) targetZoom = 800; 
                camera.position.z += (targetZoom - camera.position.z) * 0.05;
                
                camera.lookAt(state.x, state.y, 0);

            } else {
                controls.target.set(state.x, state.y, 0);
                controls.update(); 
            }
            
            renderer.render(scene, camera);
        }
        
        animate();
    </script>
</body>
</html>
"""

final_html = html_template.replace("{{GLB_BASE64_PLACEHOLDER}}", glb_base64)
components.html(final_html, height=900, scrolling=False)
