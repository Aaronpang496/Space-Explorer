import streamlit as st
import streamlit.components.v1 as components
import base64
import os

st.set_page_config(page_title="Artemis II | Real Physics", layout="wide", initial_sidebar_state="collapsed")

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
        #mission { position: absolute; top: 10px; left: 50%; transform: translateX(-50%); color: #fbbf24; text-align: center; font-size: 14px; font-weight: bold; text-shadow: 0 0 5px black; width: 60%;}
        
        /* Controls at top: 40% for mobile visibility */
        #joystick-zone { position: absolute; top: 40%; left: 20px; width: 110px; height: 110px; background: rgba(255,255,255,0.15); border: 2px solid #38bdf8; border-radius: 50%; pointer-events: auto; touch-action: none; display: none;}
        #joystick-knob { position: absolute; top: 30px; left: 30px; width: 46px; height: 46px; background: #38bdf8; border-radius: 50%; box-shadow: 0 0 10px #fff; }
        
        #throttle-zone { position: absolute; top: 40%; right: 20px; width: 45px; height: 160px; background: rgba(255,255,255,0.15); border: 2px solid #ef4444; border-radius: 20px; pointer-events: auto; touch-action: none; display: none;}
        #throttle-fill { position: absolute; bottom: 0; left: 0; width: 100%; height: 0%; background: #ef4444; border-radius: 18px;}
        
        .action-btn { position: absolute; pointer-events: auto; background: rgba(0,0,0,0.8); color: white; border: 2px solid #38bdf8; padding: 10px; border-radius: 8px; font-family: inherit; font-weight: bold; font-size: 12px; display: none; z-index: 10000; }
        #btn-gear { top: 40%; right: 80px; color: #22c55e; border-color: #22c55e; }
        #btn-retro { top: 48%; right: 80px; color: #f59e0b; border-color: #f59e0b; }
        #btn-reset { top: 40%; left: 140px; color: #ef4444; border-color: #ef4444; }
        
        #loading { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: #000; color: #38bdf8; display: flex; justify-content: center; align-items: center; font-size: 24px; z-index: 100; transition: opacity 1s; }
        #start-overlay { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(2, 6, 23, 0.85); z-index: 99999; display: flex; flex-direction: column; justify-content: center; align-items: center; pointer-events: auto; cursor: pointer; }
        .start-text { color: #38bdf8; font-size: 24px; font-weight: bold; text-transform: uppercase; letter-spacing: 3px; text-align: center; text-shadow: 0 0 20px #38bdf8; animation: pulse 2s infinite; }
        @keyframes pulse { 0% { opacity: 0.5; } 50% { opacity: 1; } 100% { opacity: 0.5; } }
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js"></script>
</head>
<body>
    <div id="loading">INITIALIZING...</div>
    
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
        <button class="action-btn" id="btn-reset">RESET</button>
    </div>

    <script>
        let state = {
            x: 0, y: 6371, vx: 0, vy: 0, 
            rotation: 0, angularVelocity: 0,
            fuel: 100, throttle: 0, 
            gear: false, exploded: false, started: false
        };

        const G = 6.674e-11;
        const EARTH_MASS = 5.97e24;
        const ROCKET_MASS = 100000;
        const MAX_THRUST = 2000000; 
        const EARTH_RADIUS = 6371;

        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 10000000);
        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        document.body.appendChild(renderer.domElement);

        scene.add(new THREE.AmbientLight(0x404040));
        const sunLight = new THREE.DirectionalLight(0xffffff, 2);
        sunLight.position.set(5000, 5000, 5000);
        scene.add(sunLight);

        // Stars
        const starsGeo = new THREE.BufferGeometry();
        const starsPos = new Float32Array(4000 * 3);
        for(let i=0; i<4000*3; i++) starsPos[i] = (Math.random() - 0.5) * 50000;
        starsGeo.setAttribute('position', new THREE.BufferAttribute(starsPos, 3));
        scene.add(new THREE.Points(starsGeo, new THREE.PointsMaterial({color: 0xffffff, size: 10})));

        // Spherical Earth
        const earthGeo = new THREE.SphereGeometry(EARTH_RADIUS, 64, 64);
        const earthMat = new THREE.MeshPhongMaterial({color: 0x1e3a8a, shininess: 10});
        const earth = new THREE.Mesh(earthGeo, earthMat);
        scene.add(earth);

        // Atmosphere Glow
        const atmoGeo = new THREE.SphereGeometry(EARTH_RADIUS * 1.02, 64, 64);
        const atmoMat = new THREE.MeshBasicMaterial({color: 0x38bdf8, transparent: true, opacity: 0.2, side: THREE.BackSide});
        scene.add(new THREE.Mesh(atmoGeo, atmoMat));

        // Launch Pad on Earth
        const padGeo = new THREE.BoxGeometry(80, 10, 80);
        const padMat = new THREE.MeshLambertMaterial({color: 0x555555});
        const pad = new THREE.Mesh(padGeo, padMat);
        pad.position.set(0, EARTH_RADIUS + 5, 0);
        scene.add(pad);

        const rocketGroup = new THREE.Group();
        rocketGroup.position.set(0, EARTH_RADIUS + 10, 0); // Start on pad
        scene.add(rocketGroup);

        // Realistic Particle Fire
        const particleCount = 300;
        const fireGeo = new THREE.BufferGeometry();
        const firePositions = new Float32Array(particleCount * 3);
        const fireVelocities = [];
        
        for (let i = 0; i < particleCount; i++) {
            firePositions[i*3] = 0; firePositions[i*3+1] = 0; firePositions[i*3+2] = 0;
            fireVelocities.push({
                x: (Math.random() - 0.5) * 3,
                y: -Math.random() * 30 - 10, 
                z: (Math.random() - 0.5) * 3
            });
        }
        fireGeo.setAttribute('position', new THREE.BufferAttribute(firePositions, 3));
        
        const canvas = document.createElement('canvas');
        canvas.width = 16; canvas.height = 16;
        const ctx = canvas.getContext('2d');
        const gradient = ctx.createRadialGradient(8, 8, 0, 8, 8, 8);
        gradient.addColorStop(0, 'rgba(255, 255, 200, 1)');
        gradient.addColorStop(0.2, 'rgba(255, 150, 0, 1)');
        gradient.addColorStop(1, 'rgba(255, 0, 0, 0)');
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, 16, 16);
        
        const fireTexture = new THREE.CanvasTexture(canvas);
        const fireMaterial = new THREE.PointsMaterial({
            size: 15, map: fireTexture, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false
        });

        const fireParticles = new THREE.Points(fireGeo, fireMaterial);
        fireParticles.position.y = -5; 
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
                const scaleFactor = 60 / size.y; 
                model.scale.set(scaleFactor, scaleFactor, scaleFactor);
                const center = box.getCenter(new THREE.Vector3());
                model.position.x = -center.x * scaleFactor;
                model.position.z = -center.z * scaleFactor;
                model.position.y = (-box.min.y * scaleFactor) + 1; 
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
            document.getElementById('btn-reset').style.display = 'block';
            document.getElementById('mission').innerText = "Slide RED BAR up to launch.";
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
            state.vx *= 0.8; state.vy *= 0.8;
        };
        document.getElementById('btn-reset').onclick = function() {
            state.x = 0; state.y = 6371; state.vx = 0; state.vy = 0; 
            state.rotation = 0; state.angularVelocity = 0;
            state.fuel = 100; state.throttle = 0; state.exploded = false;
            rocketGroup.visible = true;
            rocketGroup.position.set(0, EARTH_RADIUS + 10, 0);
            throttleFill.style.height = '0%';
            document.getElementById('mission').innerText = "Reset. Slide RED BAR up to launch.";
        };

        function updatePhysics() {
            if (!state.started || state.exploded) return;
            if (state.throttle === 0 && state.y <= 6371.1) return;

            let ax = 0, ay = 0;
            let distSq = state.x*state.x + state.y*state.y;
            let dist = Math.sqrt(distSq);
            if(dist < 100) dist = 100;
            
            // Gravity
            let gForce = (G * EARTH_MASS) / distSq;
            ax += gForce * (0 - state.x) / dist;
            ay += gForce * (0 - state.y) / dist;

            // Thrust & Particles
            if (state.throttle > 0) {
                fireParticles.visible = true;
                const positions = fireParticles.geometry.attributes.position.array;
                for (let i = 0; i < particleCount; i++) {
                    if (positions[i*3+1] < -60) {
                        positions[i*3] = 0; positions[i*3+1] = 0; positions[i*3+2] = 0;
                        fireVelocities[i].y = -Math.random() * 40 - 10;
                    }
                    positions[i*3] += fireVelocities[i].x * (state.throttle/100);
                    positions[i*3+1] += fireVelocities[i].y * (state.throttle/100);
                    positions[i*3+2] += fireVelocities[i].z * (state.throttle/100);
                }
                fireParticles.geometry.attributes.position.needsUpdate = true;

                let thrustAccel = (MAX_THRUST * (state.throttle/100)) / ROCKET_MASS;
                ax += thrustAccel * Math.sin(state.rotation);
                ay += thrustAccel * Math.cos(state.rotation);

                state.fuel -= 0.05 * (state.throttle/100);
                if (state.fuel <= 0) { state.fuel = 0; state.throttle = 0; }
            } else {
                fireParticles.visible = false;
            }

            // Angular Momentum
            let targetAngVel = (joyX / 35) * 0.04; 
            state.angularVelocity += (targetAngVel - state.angularVelocity) * 0.1; 
            state.rotation += state.angularVelocity;

            // Integration & Drag
            state.vx += ax * 0.05;
            state.vy += ay * 0.05;
            
            let alt = dist - EARTH_RADIUS;
            if (alt < 150) {
                let drag = 0.0005 * Math.sqrt(state.vx*state.vx + state.vy*state.vy);
                state.vx -= state.vx * drag;
                state.vy -= state.vy * drag;
            }

            state.x += state.vx * 0.05;
            state.y += state.vy * 0.05;

            // Crash Detection
            let currentDist = Math.sqrt(state.x*state.x + state.y*state.y);
            if (currentDist < EARTH_RADIUS) {
                triggerExplosion("LITHOBRAKING (CRASHED)");
            }

            let speed = Math.sqrt(state.vx*state.vx + state.vy*state.vy);
            document.getElementById('val-alt').innerText = Math.max(0, currentDist - EARTH_RADIUS).toFixed(1);
            document.getElementById('val-vel').innerText = (speed * 3.6).toFixed(0);
            document.getElementById('val-fuel').innerText = state.fuel.toFixed(1);
        }

        function triggerExplosion(reason) {
            state.exploded = true;
            document.getElementById('mission').innerText = "💥 FAILED: " + reason;
            rocketGroup.visible = false;
            
            const expGeo = new THREE.BufferGeometry();
            const expPos = new Float32Array(200 * 3);
            const expVel = [];
            for (let i = 0; i < 200; i++) {
                expPos[i*3] = state.x; expPos[i*3+1] = state.y; expPos[i*3+2] = 0;
                expVel.push({x: (Math.random()-0.5)*3000, y: (Math.random()-0.5)*3000});
            }
            expGeo.setAttribute('position', new THREE.BufferAttribute(expPos, 3));
            const exp = new THREE.Points(expGeo, new THREE.PointsMaterial({color: 0xff3300, size: 20}));
            exp.userData = expVel;
            scene.add(exp);
        }

        function animate() {
            requestAnimationFrame(animate);
            updatePhysics();

            if (!state.exploded) {
                rocketGroup.position.set(state.x, state.y, 0);
                rocketGroup.rotation.z = -state.rotation; 
            }

            // --- SMART FIXED CAMERA ---
            // This camera keeps the Earth and the rocket in the exact same frame
            // It anchors itself halfway between the Earth's core and the rocket.
            let midPointX = state.x * 0.5;
            let midPointY = state.y * 0.5;
            
            // Zoom out as rocket goes higher
            let distanceFromEarth = Math.sqrt(state.x*state.x + state.y*state.y);
            let targetZoom = distanceFromEarth * 2.5 + 2000; 
            
            // Smoothly interpolate to target
            camera.position.x += (midPointX - camera.position.x) * 0.1;
            camera.position.y += (midPointY - camera.position.y) * 0.1;
            camera.position.z += (targetZoom - camera.position.z) * 0.1;

            camera.lookAt(0, 0, 0); // Always look at Earth
            // But offset the lookat slightly so the rocket is centered
            let lookAtX = state.x * 0.3;
            let lookAtY = state.y * 0.3;
            camera.lookAt(lookAtX, lookAtY, 0);
            
            renderer.render(scene, camera);
        }
        
        animate();
    </script>
</body>
</html>
"""

final_html = html_template.replace("{{GLB_BASE64_PLACEHOLDER}}", glb_base64)
components.html(final_html, height=900, scrolling=False)
