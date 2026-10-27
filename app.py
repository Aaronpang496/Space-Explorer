import streamlit as st
import streamlit.components.v1 as components
import base64
import os

st.set_page_config(page_title="Artemis II | Orbital Simulator", layout="wide", initial_sidebar_state="collapsed")

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
        canvas { display: block; }
        #ui-layer { position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 9999; }
        
        #hud { position: absolute; top: 10px; left: 10px; color: #38bdf8; text-shadow: 0 0 5px #38bdf8; font-size: 14px; background: rgba(0,0,0,0.7); padding: 12px; border-radius: 5px; border: 1px solid #38bdf8;}
        #mission { position: absolute; top: 10px; left: 50%; transform: translateX(-50%); color: #fbbf24; text-align: center; font-size: 16px; font-weight: bold; text-shadow: 0 0 8px black; width: 60%;}
        
        /* Controls */
        #joystick-zone { position: absolute; top: 40%; left: 20px; width: 110px; height: 110px; background: rgba(255,255,255,0.15); border: 2px solid #38bdf8; border-radius: 50%; pointer-events: auto; touch-action: none; display: none;}
        #joystick-knob { position: absolute; top: 30px; left: 30px; width: 46px; height: 46px; background: #38bdf8; border-radius: 50%; box-shadow: 0 0 10px #fff; }
        
        #throttle-zone { position: absolute; top: 40%; right: 20px; width: 45px; height: 160px; background: rgba(255,255,255,0.15); border: 2px solid #ef4444; border-radius: 20px; pointer-events: auto; touch-action: none; display: none;}
        #throttle-fill { position: absolute; bottom: 0; left: 0; width: 100%; height: 0%; background: #ef4444; border-radius: 18px;}
        
        .action-btn { position: absolute; pointer-events: auto; background: rgba(0,0,0,0.8); color: white; border: 2px solid #38bdf8; padding: 10px; border-radius: 8px; font-family: inherit; font-weight: bold; font-size: 12px; display: none; z-index: 10000; }
        #btn-gear { top: 40%; right: 80px; color: #22c55e; border-color: #22c55e; }
        #btn-retro { top: 48%; right: 80px; color: #f59e0b; border-color: #f59e0b; }
        #btn-reset { top: 40%; left: 140px; color: #ef4444; border-color: #ef4444; }
        #btn-camera { top: 56%; right: 80px; color: #38bdf8; border-color: #38bdf8; width: 85px; }
        
        #loading { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: #000; color: #38bdf8; display: flex; justify-content: center; align-items: center; font-size: 24px; z-index: 100; transition: opacity 1s; }
        #start-overlay { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(2, 6, 23, 0.85); z-index: 99999; display: flex; flex-direction: column; justify-content: center; align-items: center; pointer-events: auto; cursor: pointer; }
        .start-text { color: #38bdf8; font-size: 24px; font-weight: bold; text-transform: uppercase; letter-spacing: 3px; text-align: center; text-shadow: 0 0 20px #38bdf8; animation: pulse 2s infinite; }
        @keyframes pulse { 0% { opacity: 0.5; } 50% { opacity: 1; } 100% { opacity: 0.5; } }
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js"></script>
    <!-- ADDED ORBIT CONTROLS -->
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>
    <div id="loading">INITIALIZING SOLAR SYSTEM...</div>
    
    <div id="start-overlay">
        <div class="start-text">TAP ANYWHERE<br>TO<br>ENTER COCKPIT</div>
    </div>

    <div id="ui-layer">
        <div id="hud">
            ALT: <span id="val-alt">0</span> km<br>
            SPEED: <span id="val-vel">0</span> km/h<br>
            FUEL: <span id="val-fuel">100</span>%<br>
            <span style="color:white">ZONE: <span id="val-zone">Earth</span></span>
        </div>
        <div id="mission">Awaiting Launch...</div>
        
        <div id="joystick-zone"><div id="joystick-knob"></div></div>
        <div id="throttle-zone"><div id="throttle-fill"></div></div>
        
        <button class="action-btn" id="btn-gear">GEAR: UP</button>
        <button class="action-btn" id="btn-retro">RETRO</button>
        <button class="action-btn" id="btn-camera">CAM: DYNAMIC</button>
        <button class="action-btn" id="btn-reset">RESET</button>
    </div>

    <script>
        let state = {
            x: 0, y: 205, vx: 0, vy: 0, 
            rotation: 0, angularVelocity: 0,
            fuel: 100, throttle: 0, 
            gear: false, exploded: false, started: false, phase: 1,
            cameraMode: "dynamic" 
        };

        const G = 1; 
        const ROCKET_MASS = 1;
        const MAX_THRUST = 6; 
        
        const planets = [
            { name: "Earth", x: 0, y: 0, r: 200, m: 50000, color: 0x1e3a8a, atmo: 0x38bdf8 },
            { name: "Moon", x: 1000, y: 400, r: 50, m: 500, color: 0x9ca3af, atmo: 0x000000 },
            { name: "Mars", x: -2000, y: -800, r: 100, m: 5000, color: 0xea580c, atmo: 0xffaa00 },
            { name: "Jupiter", x: 3000, y: 1500, r: 400, m: 200000, color: 0xd4a373, atmo: 0xffd700 }
        ];

        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 100000);
        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        document.body.appendChild(renderer.domElement);

        // Setup OrbitControls (Disabled by default until ORBIT mode is selected)
        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;
        controls.enabled = false;

        const sunLight = new THREE.PointLight(0xffffff, 2, 0, 1);
        sunLight.position.set(0, -2000, 0); 
        scene.add(sunLight);
        scene.add(new THREE.AmbientLight(0x404040));

        const starsGeo = new THREE.BufferGeometry();
        const starsPos = new Float32Array(5000 * 3);
        for(let i=0; i<5000*3; i++) starsPos[i] = (Math.random() - 0.5) * 20000;
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

        const padGeo = new THREE.BoxGeometry(40, 4, 40);
        const padMat = new THREE.MeshStandardMaterial({color: 0x555555});
        const pad = new THREE.Mesh(padGeo, padMat);
        pad.position.set(0, 202, 0);
        scene.add(pad);

        const rocketGroup = new THREE.Group();
        rocketGroup.position.set(0, 205, 0);
        scene.add(rocketGroup);

        const particleCount = 200;
        const fireGeo = new THREE.BufferGeometry();
        const firePositions = new Float32Array(particleCount * 3);
        const fireVelocities = [];
        
        for (let i = 0; i < particleCount; i++) {
            firePositions[i*3] = 0; firePositions[i*3+1] = 0; firePositions[i*3+2] = 0;
            fireVelocities.push({ x: (Math.random() - 0.5) * 2, y: -Math.random() * 10 - 5, z: (Math.random() - 0.5) * 2 });
        }
        fireGeo.setAttribute('position', new THREE.BufferAttribute(firePositions, 3));
        
        const canvas = document.createElement('canvas');
        canvas.width = 16; canvas.height = 16;
        const ctx = canvas.getContext('2d');
        const gradient = ctx.createRadialGradient(8, 8, 0, 8, 8, 8);
        gradient.addColorStop(0, 'rgba(255, 255, 255, 1)');
        gradient.addColorStop(0.2, 'rgba(255, 200, 0, 1)');
        gradient.addColorStop(1, 'rgba(255, 0, 0, 0)');
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, 16, 16);
        
        const fireTexture = new THREE.CanvasTexture(canvas);
        const fireMaterial = new THREE.PointsMaterial({ size: 15, map: fireTexture, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false });

        const fireParticles = new THREE.Points(fireGeo, fireMaterial);
        fireParticles.position.y = -10; 
        fireParticles.visible = false;
        rocketGroup.add(fireParticles);

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
                const scaleFactor = 30 / size.y; 
                model.scale.set(scaleFactor, scaleFactor, scaleFactor);
                const center = box.getCenter(new THREE.Vector3());
                model.position.x = -center.x * scaleFactor;
                model.position.z = -center.z * scaleFactor;
                model.position.y = (-box.min.y * scaleFactor); 
                rocketGroup.add(model);
                document.getElementById('loading').style.opacity = 0;
            });
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
            document.getElementById('mission').innerText = "Task: Slide throttle to 100% for liftoff.";
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
        
        // --- CAMERA TOGGLE BUTTON ---
        document.getElementById('btn-camera').onclick = function() {
            if (state.cameraMode === "dynamic") {
                state.cameraMode = "orbit";
                this.innerText = "CAM: ORBIT";
                controls.enabled = true;
                
                // Snap camera to a close, dramatic angle when entering orbit mode
                camera.position.set(state.x + 80, state.y + 40, 80);
                controls.target.set(state.x, state.y, 0);
                
            } else {
                state.cameraMode = "dynamic";
                this.innerText = "CAM: DYNAMIC";
                controls.enabled = false;
            }
        };

        document.getElementById('btn-reset').onclick = function() {
            state.x = 0; state.y = 205; state.vx = 0; state.vy = 0; 
            state.rotation = 0; state.angularVelocity = 0; state.phase = 1;
            state.fuel = 100; state.throttle = 0; state.exploded = false;
            rocketGroup.visible = true;
            rocketGroup.position.set(0, 205, 0);
            throttleFill.style.height = '0%';
            document.getElementById('mission').innerText = "Reset. Slide throttle up to launch.";
        };

        function updatePhysics() {
            if (!state.started || state.exploded) return;
            if (state.throttle === 0 && state.vy === 0 && state.vx === 0) return;

            let ax = 0, ay = 0;
            let currentZone = "Deep Space";

            planets.forEach(p => {
                let dx = p.x - state.x;
                let dy = p.y - state.y;
                let distSq = dx*dx + dy*dy;
                let dist = Math.sqrt(distSq);
                if (dist < 10) dist = 10;

                if (dist < p.r * 3) currentZone = p.name + " Orbit";

                let accel = (G * p.m) / distSq;
                ax += accel * (dx / dist);
                ay += accel * (dy / dist);

                if (dist < p.r && (Math.abs(state.vx) > 0.5 || Math.abs(state.vy) > 0.5)) {
                    if (dist < p.r - 5) { 
                        triggerExplosion("CRASHED INTO " + p.name.toUpperCase());
                    }
                }
            });

            if (state.throttle > 0) {
                fireParticles.visible = true;
                const positions = fireParticles.geometry.attributes.position.array;
                for (let i = 0; i < particleCount; i++) {
                    if (positions[i*3+1] < -40) {
                        positions[i*3] = 0; positions[i*3+1] = 0; positions[i*3+2] = 0;
                    }
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

            let targetAngVel = (joyX / 35) * 0.05; 
            state.angularVelocity += (targetAngVel - state.angularVelocity) * 0.1; 
            state.rotation += state.angularVelocity;

            state.vx += ax * 0.1;
            state.vy += ay * 0.1;
            state.x += state.vx * 0.1;
            state.y += state.vy * 0.1;

            let distToEarth = Math.sqrt(state.x*state.x + state.y*state.y);
            if (distToEarth < 205) {
                let angle = Math.atan2(state.y, state.x);
                state.x = Math.cos(angle) * 205;
                state.y = Math.sin(angle) * 205;
                state.vx = 0; state.vy = 0; 
                state.throttle = 0; 
                throttleFill.style.height = '0%';
                fireParticles.visible = false;
            }

            if (state.phase === 1 && distToEarth > 400) {
                document.getElementById('mission').innerText = "Task: Fly to the Moon (Grey planet to the Right).";
                state.phase = 2;
            }

            let speed = Math.sqrt(state.vx*state.vx + state.vy*state.vy);
            document.getElementById('val-alt').innerText = Math.max(0, (distToEarth - 200)).toFixed(1);
            document.getElementById('val-vel').innerText = (speed * 10).toFixed(0); 
            document.getElementById('val-fuel').innerText = state.fuel.toFixed(1);
            document.getElementById('val-zone').innerText = currentZone;
        }

        function triggerExplosion(reason) {
            state.exploded = true;
            document.getElementById('mission').innerText = "💥 FAILED: " + reason;
            rocketGroup.visible = false;
        }

        function animate() {
            requestAnimationFrame(animate);
            updatePhysics();

            if (!state.exploded) {
                rocketGroup.position.set(state.x, state.y, 0);
                rocketGroup.rotation.z = -state.rotation; 
            }

            let speed = Math.sqrt(state.vx*state.vx + state.vy*state.vy);
            let distToEarth = Math.sqrt(state.x*state.x + state.y*state.y);

            // --- CAMERA LOGIC ---
            if (state.cameraMode === "dynamic") {
                // DYNAMIC MOMENTUM CAMERA (Cinematic)
                let camTargetX = state.x - (state.vx * 0.8); 
                let camTargetY = state.y - (state.vy * 0.8);
                let lookTargetX = state.x + (state.vx * 1.5);
                let lookTargetY = state.y + (state.vy * 1.5);

                camera.position.x += (camTargetX - camera.position.x) * 0.05; 
                camera.position.y += (camTargetY - camera.position.y) * 0.05;

                let targetZoom = 300 + (distToEarth * 0.5) + (speed * 3);
                camera.position.z += (targetZoom - camera.position.z) * 0.05;
                
                camera.lookAt(lookTargetX, lookTargetY, 0);

            } else {
                // 360 ORBIT CAMERA (Locked to Rocket)
                // Keep the orbit controls target exactly on the rocket
                controls.target.set(state.x, state.y, 0);
                controls.update(); // Updates the drag/zoom
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
