import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Artemis II | Universe View", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    .block-container { padding: 0rem !important; margin: 0rem !important; max-width: 100% !important; }
    header {visibility: hidden;}
    iframe { border: none; }
</style>
""", unsafe_allow_html=True)

model_filename = "artemis_ii.glb"

game_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body {{ margin: 0; overflow: hidden; background-color: #000; font-family: 'Courier New', monospace; touch-action: none; }}
        canvas {{ display: block; }}
        #ui-layer {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; }}
        #hud {{ position: absolute; top: 10px; left: 10px; color: #38bdf8; text-shadow: 0 0 5px #38bdf8; font-size: 14px; background: rgba(0,0,0,0.5); padding: 10px; border-radius: 5px; border: 1px solid #38bdf8;}}
        #mission {{ position: absolute; top: 10px; left: 50%; transform: translateX(-50%); color: #fbbf24; text-align: center; font-size: 16px; font-weight: bold; text-shadow: 0 0 5px black; width: 60%;}}
        #joystick-zone {{ position: absolute; bottom: 30px; left: 30px; width: 120px; height: 120px; background: rgba(255,255,255,0.1); border: 2px solid rgba(56,189,248,0.5); border-radius: 50%; pointer-events: auto; touch-action: none;}}
        #joystick-knob {{ position: absolute; top: 35px; left: 35px; width: 50px; height: 50px; background: rgba(56,189,248,0.8); border-radius: 50%; box-shadow: 0 0 10px #38bdf8; }}
        #throttle-zone {{ position: absolute; bottom: 30px; right: 30px; width: 40px; height: 200px; background: rgba(255,255,255,0.1); border: 2px solid rgba(239,68,68,0.5); border-radius: 20px; pointer-events: auto; touch-action: none;}}
        #throttle-fill {{ position: absolute; bottom: 0; left: 0; width: 100%; height: 0%; background: rgba(239,68,68,0.8); border-radius: 18px;}}
        #minimap-container {{ position: absolute; top: 10px; right: 10px; width: 150px; height: 150px; border: 2px solid #38bdf8; border-radius: 50%; background: rgba(0,0,0,0.6); overflow: hidden; }}
        #minimap {{ width: 100%; height: 100%; }}
        .btn {{ position: absolute; pointer-events: auto; background: rgba(0,0,0,0.6); color: white; border: 1px solid #38bdf8; padding: 10px; border-radius: 5px; font-family: inherit; font-weight: bold; }}
        #btn-gear {{ bottom: 30px; left: 160px; color: #22c55e; border-color: #22c55e; }}
        #btn-shield {{ bottom: 80px; left: 160px; color: #f59e0b; border-color: #f59e0b; }}
        #btn-reset {{ top: 10px; right: 170px; color: #ef4444; border-color: #ef4444; }}
        #loading {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: #000; color: #38bdf8; display: flex; justify-content: center; align-items: center; font-size: 24px; z-index: 100; transition: opacity 1s; }}
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js"></script>
</head>
<body>
    <div id="loading">INITIALIZING UNIVERSE...</div>
    
    <div id="ui-layer" style="opacity: 0; transition: opacity 1s;">
        <div id="hud">
            ALT: <span id="val-alt">0</span> km<br>
            VEL: <span id="val-vel">0</span> m/s<br>
            FUEL: <span id="val-fuel">100</span>%<br>
            <span style="color:white">TARGET: <span id="val-target">Earth</span></span>
        </div>
        <div id="mission">MISSION: Awaiting Launch Sequence...</div>
        <div id="joystick-zone"><div id="joystick-knob"></div></div>
        <div id="throttle-zone"><div id="throttle-fill"></div></div>
        <div id="minimap-container"><div id="minimap"></div></div>
        <button class="btn" id="btn-gear">GEAR: RETRACTED</button>
        <button class="btn" id="btn-shield">HEAT SHIELD: ON</button>
        <button class="btn" id="btn-reset">RESET</button>
    </div>

    <script>
        let state = {{
            alt: 0, vel: 0, fuel: 100, throttle: 0, 
            pitch: 0, roll: 0,
            gear: false, shield: true,
            exploded: false, won: false,
            target: "Earth", 
            task: "Awaiting Launch Sequence...",
            missionPhase: 1,
            cameraMode: "birdseye"
        }};

        const planets = {{
            "Earth": {{ gravity: 9.81, atmo: 100, color: 0x2233ff, radius: 6371 }},
            "Moon": {{ gravity: 1.62, atmo: 0, color: 0xaaaaaa, radius: 1737 }},
            "Mars": {{ gravity: 3.71, atmo: 50, color: 0xff4400, radius: 3389 }},
            "Jupiter": {{ gravity: 24.79, atmo: 500, color: 0xd4a373, radius: 69911 }}
        }};

        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 100000000);
        const renderer = new THREE.WebGLRenderer({{ antialias: true }});
        renderer.setSize(window.innerWidth, window.innerHeight);
        document.body.appendChild(renderer.domElement);

        const sunLight = new THREE.DirectionalLight(0xffffff, 2);
        sunLight.position.set(100000, 100000, 100000);
        scene.add(sunLight);
        scene.add(new THREE.AmbientLight(0x404040));

        let planetMeshes = {{}};
        let planetPositions = {{
            "Earth": [0, -6371, 0],
            "Moon": [50000, 20000, -50000],
            "Mars": [150000, -10000, 100000],
            "Jupiter": [-300000, 50000, -200000]
        }};

        for (let p in planets) {{
            let geo = new THREE.SphereGeometry(planets[p].radius, 64, 64);
            let mat = new THREE.MeshPhongMaterial({{color: planets[p].color}});
            let mesh = new THREE.Mesh(geo, mat);
            mesh.position.set(...planetPositions[p]);
            scene.add(mesh);
            planetMeshes[p] = mesh;
        }}

        const rocketGroup = new THREE.Group();
        scene.add(rocketGroup);

        // --- ENGINE FIRE EFFECT ---
        const fireGeo = new THREE.ConeGeometry(10, 40, 16);
        // Material with emissive glow and transparency
        const fireMat = new THREE.MeshBasicMaterial({{color: 0xffaa00, transparent: true, opacity: 0.8, blending: THREE.AdditiveBlending}});
        const engineFire = new THREE.Mesh(fireGeo, fireMat);
        engineFire.rotation.x = Math.PI; // Point down
        engineFire.position.y = -20; // Position under rocket
        engineFire.visible = false; // Hidden by default
        rocketGroup.add(engineFire);

        const loader = new THREE.GLTFLoader();
        loader.load('app/static/{model_filename}', function (gltf) {{
            const model = gltf.scene;
            const box = new THREE.Box3().setFromObject(model);
            const size = box.getSize(new THREE.Vector3());
            const targetHeight = 100;
            const scaleFactor = targetHeight / size.y;
            model.scale.set(scaleFactor, scaleFactor, scaleFactor);
            const center = box.getCenter(new THREE.Vector3());
            model.position.x = -center.x * scaleFactor;
            model.position.z = -center.z * scaleFactor;
            model.position.y = (-box.min.y * scaleFactor);
            
            rocketGroup.add(model);
            
            const padGeo = new THREE.BoxGeometry(200, 20, 200);
            const padMat = new THREE.MeshLambertMaterial({{color: 0x555555}});
            const pad = new THREE.Mesh(padGeo, padMat);
            pad.position.set(0, -10, 0);
            rocketGroup.add(pad);
            
            document.getElementById('loading').style.opacity = 0;
            document.getElementById('ui-layer').style.opacity = 1;
        }}, undefined, function (error) {{
            console.error('Error loading model:', error);
            const rocketGeo = new THREE.CylinderGeometry(15, 15, 100, 16);
            const rocketMat = new THREE.MeshPhongMaterial({{color: 0xdddddd}});
            const rocket = new THREE.Mesh(rocketGeo, rocketMat);
            rocket.position.y = 50;
            rocketGroup.add(rocket);
            document.getElementById('loading').style.opacity = 0;
            document.getElementById('ui-layer').style.opacity = 1;
        }});

        const miniScene = new THREE.Scene();
        const miniCamera = new THREE.PerspectiveCamera(50, 1, 0.1, 100000);
        miniCamera.position.set(0, 50, 100);
        miniCamera.lookAt(0, 0, 0);
        const miniRenderer = new THREE.WebGLRenderer({{ alpha: true }});
        miniRenderer.setSize(150, 150);
        document.getElementById('minimap').appendChild(miniRenderer.domElement);

        const miniEarth = new THREE.Mesh(new THREE.SphereGeometry(10, 16, 16), new THREE.MeshBasicMaterial({{color: 0x2233ff}}));
        miniScene.add(miniEarth);
        const miniRocket = new THREE.Mesh(new THREE.ConeGeometry(2, 5, 8), new THREE.MeshBasicMaterial({{color: 0xff0000}}));
        miniScene.add(miniRocket);

        let isDraggingJoy = false;
        let isDraggingThrottle = false;
        
        const joyZone = document.getElementById('joystick-zone');
        const joyKnob = document.getElementById('joystick-knob');
        const throttleZone = document.getElementById('throttle-zone');
        const throttleFill = document.getElementById('throttle-fill');

        joyZone.addEventListener('pointerdown', (e) => {{ 
            isDraggingJoy = true; joyZone.setPointerCapture(e.pointerId); 
            if (state.cameraMode === "birdseye") {{ state.cameraMode = "launch"; }}
        }});
        joyZone.addEventListener('pointerup', (e) => {{ 
            isDraggingJoy = false; joyKnob.style.top = '35px'; joyKnob.style.left = '35px'; 
            state.pitch = 0; state.roll = 0; 
        }});
        joyZone.addEventListener('pointermove', (e) => {{
            if (!isDraggingJoy) return;
            const rect = joyZone.getBoundingClientRect();
            let x = e.clientX - rect.left - 60; let y = e.clientY - rect.top - 60;
            const dist = Math.sqrt(x*x + y*y);
            if (dist > 35) {{ x = (x/dist)*35; y = (y/dist)*35; }}
            joyKnob.style.left = (35 + x) + 'px'; joyKnob.style.top = (35 + y) + 'px';
            state.roll = (x / 35) * 45; state.pitch = -(y / 35) * 45;
        }});

        throttleZone.addEventListener('pointerdown', (e) => {{ 
            isDraggingThrottle = true; throttleZone.setPointerCapture(e.pointerId);
            if (state.cameraMode === "birdseye") {{ state.cameraMode = "launch"; }}
        }});
        throttleZone.addEventListener('pointerup', () => {{ isDraggingThrottle = false; }});
        throttleZone.addEventListener('pointermove', (e) => {{
            if (!isDraggingThrottle) return;
            const rect = throttleZone.getBoundingClientRect();
            let y = e.clientY - rect.top;
            if (y < 0) y = 0; if (y > 200) y = 200;
            let percent = 100 - (y / 200) * 100;
            state.throttle = percent;
            throttleFill.style.height = percent + '%';
        }});

        document.getElementById('btn-gear').onclick = function() {{
            state.gear = !state.gear;
            this.innerText = "GEAR: " + (state.gear ? "DEPLOYED" : "RETRACTED");
        }};
        document.getElementById('btn-shield').onclick = function() {{
            state.shield = !state.shield;
            this.innerText = "HEAT SHIELD: " + (state.shield ? "ON" : "OFF");
        }};
        document.getElementById('btn-reset').onclick = function() {{
            state.alt = 0; state.vel = 0; state.fuel = 100; state.throttle = 0;
            state.exploded = false; state.won = false; state.missionPhase = 1;
            state.cameraMode = "birdseye"; 
            state.task = "Awaiting Launch Sequence...";
            throttleFill.style.height = '0%';
            rocketGroup.visible = true;
            rocketGroup.rotation.set(0,0,0);
            // Remove old explosions
            scene.children = scene.children.filter(child => child.type !== 'Points' && child.type !== 'Mesh' || child.geometry.type !== 'SphereGeometry');
        }};

        function updatePhysics() {{
            if (state.exploded || state.won) return;
            if (state.throttle === 0 && state.vel === 0) return;

            let p = planets[state.target];
            let altKm = state.alt / 1000;
            let throttleRatio = state.throttle / 100;

            // --- ENGINE FIRE VISUALS ---
            if (throttleRatio > 0.05 && !state.exploded) {{
                engineFire.visible = true;
                // Flicker effect
                engineFire.scale.set(1 + Math.random()*0.2, 1 + Math.random()*0.5, 1 + Math.random()*0.2);
                engineFire.material.opacity = 0.5 + Math.random() * 0.4;
            }} else {{
                engineFire.visible = false;
            }}

            if (state.missionPhase === 1 && altKm > 0.1) {{ state.task = "Task: Reach 100km altitude to enter Deep Space."; state.missionPhase = 1.5; }}
            if (state.missionPhase === 1.5 && altKm > 100) {{ state.task = "Task Complete! Cut throttle, fall back, and land."; state.missionPhase = 2; }}
            if (state.missionPhase === 2 && state.vel < -100) {{ state.task = "Re-entry! Deploy gear and slow down below 10m/s."; state.missionPhase = 3; }}

            if (altKm < 15 && state.vel > 450 && throttleRatio > 0.85) {{ triggerExplosion("MAX-Q STRUCTURAL FAILURE"); }}
            if (state.vel < -2000 && altKm < p.atmo && !state.shield) {{ triggerExplosion("ATMOSPHERIC BURN-UP"); }}

            let thrustForce = 3500000 * throttleRatio;
            let fuelBurn = 600 * throttleRatio * 0.1;
            state.fuel -= (fuelBurn / 100000) * 100;
            if (state.fuel < 0) state.fuel = 0;

            let mass = 50000 + (state.fuel/100)*100000;
            let accel = (thrustForce / mass) - p.gravity;
            
            if (altKm < p.atmo) {{ accel -= (0.05 * (state.vel * state.vel)) / mass; }}

            state.vel += accel * 0.1;
            state.alt += state.vel * 0.1;

            if (state.alt <= 0) {{
                if (state.vel < -10) {{ triggerExplosion("LITHOBRAKING"); }}
                else if (!state.gear) {{ triggerExplosion("CRUSHED (NO GEAR)"); }}
                else {{ 
                    state.alt = 0; state.vel = 0; state.won = true;
                    state.task = "🏆 MISSION ACCOMPLISHED!";
                }}
            }}
        }}

        // --- PARTICLES EXPLOSION EFFECT ---
        function triggerExplosion(reason) {{
            state.exploded = true;
            state.task = "💥 FAILED: " + reason;
            rocketGroup.visible = false; // Hide rocket
            
            // Create a particle system for the explosion
            const particleCount = 500;
            const geometry = new THREE.BufferGeometry();
            const positions = new Float32Array(particleCount * 3);
            const colors = new Float32Array(particleCount * 3);
            const velocities = [];

            for (let i = 0; i < particleCount; i++) {{
                // Start all particles at the center of the rocket
                positions[i*3] = 0;
                positions[i*3+1] = Math.max(100, state.alt * 0.1);
                positions[i*3+2] = 0;

                // Random velocity vectors outward
                velocities.push({{
                    x: (Math.random() - 0.5) * 20,
                    y: (Math.random() - 0.5) * 20,
                    z: (Math.random() - 0.5) * 20
                }});

                // Random fire colors (Red, Orange, Yellow)
                colors[i*3] = 1.0; // R
                colors[i*3+1] = Math.random() * 0.8; // G
                colors[i*3+2] = 0.0; // B
            }}

            geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
            geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

            const material = new THREE.PointsMaterial({{ size: 15, vertexColors: true, transparent: true, blending: THREE.AdditiveBlending }});
            const explosionParticles = new THREE.Points(geometry, material);
            explosionParticles.userData.velocities = velocities; // Store velocities for animation
            scene.add(explosionParticles);
        }}

        function animate() {{
            requestAnimationFrame(animate);
            updatePhysics();

            document.getElementById('val-alt').innerText = (state.alt/1000).toFixed(1);
            document.getElementById('val-vel').innerText = state.vel.toFixed(1);
            document.getElementById('val-fuel').innerText = state.fuel.toFixed(1);
            document.getElementById('mission').innerText = state.task;

            let visualAlt = state.alt * 0.1;
            if (!state.exploded) {{
                rocketGroup.position.y = visualAlt;
                rocketGroup.rotation.x = state.pitch * (Math.PI / 180);
                rocketGroup.rotation.z = state.roll * (Math.PI / 180);
            }}

            // Animate Explosion Particles
            scene.children.forEach(child => {{
                if (child.type === 'Points' && child.userData.velocities) {{
                    const positions = child.geometry.attributes.position.array;
                    for (let i = 0; i < positions.length / 3; i++) {{
                        positions[i*3] += child.userData.velocities[i].x * 0.1;
                        positions[i*3+1] += child.userData.velocities[i].y * 0.1;
                        positions[i*3+2] += child.userData.velocities[i].z * 0.1;
                    }}
                    child.geometry.attributes.position.needsUpdate = true;
                }}
            }});

            if (state.cameraMode === "birdseye") {{
                const time = Date.now() * 0.0001;
                camera.position.x = Math.sin(time) * 400000;
                camera.position.z = Math.cos(time) * 400000;
                camera.position.y = 150000 + Math.sin(time * 2) * 50000;
                camera.lookAt(0, 0, 0);
            }} else {{
                camera.position.set(150, visualAlt + 100, 300);
                camera.lookAt(rocketGroup.position);
            }}

            let mapScale = 0.05;
            miniRocket.position.set(0, (state.alt/1000) * mapScale, 0);
            miniEarth.position.y = -10 - (state.alt/1000) * mapScale;

            renderer.render(scene, camera);
            miniRenderer.render(miniScene, miniCamera);
        }}
        
        animate();

        window.addEventListener('resize', () => {{
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }});
    </script>
</body>
</html>
"""

components.html(game_html, height=900, scrolling=False)
