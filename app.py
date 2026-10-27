import streamlit as st
import streamlit.components.v1 as components
import base64
import os

st.set_page_config(page_title="Artemis II | Solar System", layout="wide", initial_sidebar_state="collapsed")

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

game_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body {{ margin: 0; overflow: hidden; background-color: #000; font-family: 'Courier New', monospace; touch-action: none; user-select: none; }}
        canvas {{ display: block; }}
        #ui-layer {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 9999; }}
        
        #hud {{ position: absolute; top: 10px; left: 10px; color: #38bdf8; text-shadow: 0 0 5px #38bdf8; font-size: 14px; background: rgba(0,0,0,0.5); padding: 10px; border-radius: 5px; border: 1px solid #38bdf8;}}
        #mission {{ position: absolute; top: 10px; left: 50%; transform: translateX(-50%); color: #fbbf24; text-align: center; font-size: 14px; font-weight: bold; text-shadow: 0 0 5px black; width: 60%;}}
        
        /* Mobile Joystick */
        #joystick-zone {{ position: absolute; bottom: 40px; left: 40px; width: 140px; height: 140px; background: rgba(255,255,255,0.1); border: 2px solid rgba(56,189,248,0.5); border-radius: 50%; pointer-events: auto; touch-action: none; display: none;}}
        #joystick-knob {{ position: absolute; top: 45px; left: 45px; width: 50px; height: 50px; background: #38bdf8; border-radius: 50%; box-shadow: 0 0 10px #fff; }}
        
        /* Mobile Throttle */
        #throttle-zone {{ position: absolute; bottom: 40px; right: 40px; width: 50px; height: 250px; background: rgba(255,255,255,0.1); border: 2px solid rgba(239,68,68,0.5); border-radius: 25px; pointer-events: auto; touch-action: none; display: none;}}
        #throttle-fill {{ position: absolute; bottom: 0; left: 0; width: 100%; height: 0%; background: #ef4444; border-radius: 20px;}}
        
        #minimap-container {{ position: absolute; top: 10px; right: 10px; width: 180px; height: 180px; border: 2px solid #38bdf8; border-radius: 50%; background: rgba(0,0,0,0.8); overflow: hidden; display: none;}}
        #minimap {{ width: 100%; height: 100%; }}
        
        .btn {{ position: absolute; pointer-events: auto; background: rgba(0,0,0,0.8); color: white; border: 2px solid #38bdf8; padding: 15px; border-radius: 8px; font-family: inherit; font-weight: bold; font-size: 14px; display: none; z-index: 10000;}}
        
        #loading {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: #000; color: #38bdf8; display: flex; justify-content: center; align-items: center; font-size: 24px; z-index: 100; transition: opacity 1s; }}
        #start-overlay {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(2, 6, 23, 0.85); z-index: 99999; display: flex; flex-direction: column; justify-content: center; align-items: center; pointer-events: auto; cursor: pointer; }}
        .start-text {{ color: #38bdf8; font-size: 28px; font-weight: bold; text-transform: uppercase; letter-spacing: 3px; text-align: center; text-shadow: 0 0 20px #38bdf8; animation: pulse 2s infinite; }}
        @keyframes pulse {{ 0% {{ opacity: 0.5; }} 50% {{ opacity: 1; }} 100% {{ opacity: 0.5; }} }}
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js"></script>
</head>
<body>
    <div id="loading">INITIALIZING SOLAR SYSTEM...</div>
    
    <div id="start-overlay">
        <div class="start-text">TAP ANYWHERE<br>TO<br>ENTER COCKPIT</div>
    </div>

    <div id="ui-layer">
        <div id="hud">
            POS: X:<span id="val-x">0</span> Y:<span id="val-y">0</span><br>
            VEL: <span id="val-vel">0</span> m/s<br>
            FUEL: <span id="val-fuel">100</span>%<br>
            <span style="color:white">ZONE: <span id="val-zone">Earth</span></span>
        </div>
        <div id="mission">Awaiting Launch...</div>
        
        <div id="joystick-zone"><div id="joystick-knob"></div></div>
        <div id="throttle-zone"><div id="throttle-fill"></div></div>
        <div id="minimap-container"><div id="minimap"></div></div>
    </div>

    <script>
        // --- 1. GAME STATE & PHYSICS ---
        let state = {{
            x: 0, y: 6371, // Start on Earth surface
            vx: 0, vy: 0,  // Velocity vector
            fuel: 100, throttle: 0, 
            angle: 0, // Rocket rotation (radians)
            exploded: false, won: false,
            started: false
        }};

        const G = 6.674e-11;
        const rocketMass = 100000; 
        const maxThrust = 20000000; // Newtons

        // Planets: Mass, Radius, Position, Gravity Ring (Sphere of Influence)
        const planets = {{
            Earth:   {{ m: 5.97e24, r: 6371, x: 0, y: 0, color: 0x2233ff, soi: 924000 }},
            Moon:    {{ m: 7.34e22, r: 1737, x: 384400, y: 0, color: 0xaaaaaa, soi: 66100 }},
            Mars:    {{ m: 6.41e23, r: 3389, x: 225000000, y: 0, color: 0xff4400, soi: 577000 }},
            Jupiter: {{ m: 1.89e27, r: 69911, x: 778000000, y: 0, color: 0xd4a373, soi: 48200000 }}
        }};

        // --- 2. THREE.JS SETUP ---
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000000000);
        const renderer = new THREE.WebGLRenderer({{ antialias: true }});
        renderer.setSize(window.innerWidth, window.innerHeight);
        document.body.appendChild(renderer.domElement);

        const sunLight = new THREE.DirectionalLight(0xffffff, 2);
        sunLight.position.set(100000, 100000, 100000);
        scene.add(sunLight);
        scene.add(new THREE.AmbientLight(0x404040));

        // Draw Planets & Gravity Rings
        for (let p in planets) {{
            let geo = new THREE.SphereGeometry(planets[p].r, 64, 64);
            let mat = new THREE.MeshPhongMaterial({{color: planets[p].color}});
            let mesh = new THREE.Mesh(geo, mat);
            mesh.position.set(planets[p].x, planets[p].y, 0);
            scene.add(mesh);

            // Draw Gravity Ring (Sphere of Influence)
            let ringGeo = new THREE.RingGeometry(planets[p].soi - (planets[p].soi*0.01), planets[p].soi, 64);
            let ringMat = new THREE.MeshBasicMaterial({{ color: planets[p].color, side: THREE.DoubleSide, transparent: true, opacity: 0.1 }});
            let ring = new THREE.Mesh(ringGeo, ringMat);
            ring.position.set(planets[p].x, planets[p].y, 0);
            scene.add(ring);
        }}

        // Load Rocket
        const rocketGroup = new THREE.Group();
        scene.add(rocketGroup);

        const fireGeo = new THREE.ConeGeometry(10, 40, 16);
        const fireMat = new THREE.MeshBasicMaterial({{color: 0xffaa00, transparent: true, opacity: 0.8, blending: THREE.AdditiveBlending}});
        const engineFire = new THREE.Mesh(fireGeo, fireMat);
        engineFire.rotation.x = Math.PI;
        engineFire.position.y = -20;
        engineFire.visible = false;
        rocketGroup.add(engineFire);

        const base64String = "{glb_base64}";
        if (base64String.length > 100) {{
            const binaryString = atob(base64String);
            const bytes = new Uint8Array(binaryString.length);
            for (let i = 0; i < binaryString.length; i++) {{ bytes[i] = binaryString.charCodeAt(i); }}
            
            const loader = new THREE.GLTFLoader();
            loader.parse(bytes.buffer, '', function (gltf) {{
                const model = gltf.scene;
                const box = new THREE.Box3().setFromObject(model);
                const size = box.getSize(new THREE.Vector3());
                const scaleFactor = 100 / size.y;
                model.scale.set(scaleFactor, scaleFactor, scaleFactor);
                const center = box.getCenter(new THREE.Vector3());
                model.position.x = -center.x * scaleFactor;
                model.position.z = -center.z * scaleFactor;
                model.position.y = (-box.min.y * scaleFactor);
                rocketGroup.add(model);
                document.getElementById('loading').style.opacity = 0;
            }});
        }}

        // Minimap Setup
        const miniScene = new THREE.Scene();
        const miniCamera = new THREE.OrthographicCamera(-1e9, 1e9, 1e9, -1e9, 0.1, 2e9);
        miniCamera.position.set(0, 0, 1e8);
        const miniRenderer = new THREE.WebGLRenderer({{ alpha: true }});
        miniRenderer.setSize(180, 180);
        document.getElementById('minimap').appendChild(miniRenderer.domElement);

        // Draw minimap planets
        let miniPlanets = {{}};
        for (let p in planets) {{
            let mGeo = new THREE.CircleGeometry(planets[p].soi * 0.8, 16); // Scale for visibility
            let mMat = new THREE.MeshBasicMaterial({{color: planets[p].color, transparent: true, opacity: 0.5}});
            let mesh = new THREE.Mesh(mGeo, mMat);
            mesh.position.set(planets[p].x * 0.0000001, planets[p].y * 0.0000001, 0);
            miniScene.add(mesh);
        }}
        const miniRocket = new THREE.Mesh(new THREE.CircleGeometry(5000, 8), new THREE.MeshBasicMaterial({{color: 0xff0000}}));
        miniScene.add(miniRocket);

        // --- 3. CONTROLS ---
        let isDraggingJoy = false;
        let isDraggingThrottle = false;
        const joyZone = document.getElementById('joystick-zone');
        const joyKnob = document.getElementById('joystick-knob');
        const throttleZone = document.getElementById('throttle-zone');
        const throttleFill = document.getElementById('throttle-fill');

        document.getElementById('start-overlay').addEventListener('pointerdown', function(e) {{
            e.preventDefault(); 
            state.started = true;
            this.style.display = 'none';
            document.getElementById('joystick-zone').style.display = 'block';
            document.getElementById('throttle-zone').style.display = 'block';
            document.getElementById('minimap-container').style.display = 'block';
            state.task = "Slide RED BAR up to launch.";
        }});

        joyZone.addEventListener('pointerdown', (e) => {{ isDraggingJoy = true; joyZone.setPointerCapture(e.pointerId); }});
        joyZone.addEventListener('pointerup', (e) => {{ isDraggingJoy = false; joyKnob.style.top = '45px'; joyKnob.style.left = '45px'; }});
        joyZone.addEventListener('pointermove', (e) => {{
            if (!isDraggingJoy) return;
            const rect = joyZone.getBoundingClientRect();
            let x = e.clientX - rect.left - 70; let y = e.clientY - rect.top - 70;
            const dist = Math.sqrt(x*x + y*y);
            if (dist > 45) {{ x = (x/45)*45; y = (y/45)*45; }}
            joyKnob.style.left = (45 + x) + 'px'; joyKnob.style.top = (45 + y) + 'px';
            
            // Angle 0 is UP. Math.atan2(y, x) gives angle from positive X axis. 
            // We want 0 to be up, so we use atan2(x, -y) 
            state.angle = Math.atan2(x, -y); 
        }});

        throttleZone.addEventListener('pointerdown', (e) => {{ isDraggingThrottle = true; throttleZone.setPointerCapture(e.pointerId); }});
        throttleZone.addEventListener('pointerup', () => {{ isDraggingThrottle = false; }});
        throttleZone.addEventListener('pointermove', (e) => {{
            if (!isDraggingThrottle) return;
            const rect = throttleZone.getBoundingClientRect();
            let y = e.clientY - rect.top;
            if (y < 0) y = 0; if (y > 250) y = 250;
            let percent = 100 - (y / 250) * 100;
            state.throttle = percent;
            throttleFill.style.height = percent + '%';
        }});

        // --- 4. PHYSICS ENGINE ---
        function updatePhysics() {{
            if (!state.started || state.exploded) return;

            // Calculate Gravity from all planets
            let ax = 0, ay = 0;
            let currentZone = "Deep Space";

            for (let p in planets) {{
                let dx = planets[p].x - state.x;
                let dy = planets[p].y - state.y;
                let distSq = dx*dx + dy*dy;
                let dist = Math.sqrt(distSq);

                // Check if we are inside this planet's gravity ring
                if (dist < planets[p].soi) currentZone = p;

                // Newton's Law of Universal Gravitation: F = G * m1 * m2 / r^2
                // Acceleration (a = F/m): a = G * m / r^2
                let accel = (G * planets[p].m) / distSq;
                
                // Break acceleration into X and Y components
                ax += accel * (dx / dist);
                ay += accel * (dy / dist);

                // Collision Check (Crash into planet)
                if (dist < planets[p].r && !state.exploded) {{
                    triggerExplosion("CRASHED INTO " + p);
                }}
            }}

            // Apply Thrust
            if (state.throttle > 0) {{
                engineFire.visible = true;
                engineFire.scale.set(1 + Math.random()*0.2, 1 + Math.random()*0.5, 1 + Math.random()*0.2);
                
                let thrustAccel = (maxThrust * (state.throttle/100)) / rocketMass;
                // Thrust angle: 0 is UP (positive Y)
                ax += thrustAccel * Math.sin(state.angle);
                ay += thrustAccel * Math.cos(state.angle);
                
                // Burn fuel
                state.fuel -= 0.1 * (state.throttle/100);
                if (state.fuel <= 0) {{ state.fuel = 0; state.throttle = 0; }}
            }} else {{
                engineFire.visible = false;
            }}

            // Update Velocity & Position (Euler Integration)
            state.vx += ax * 0.1; // Time step
            state.vy += ay * 0.1;
            state.x += state.vx * 0.1;
            state.y += state.vy * 0.1;

            // Update HUD
            let speed = Math.sqrt(state.vx*state.vx + state.vy*state.vy);
            document.getElementById('val-x').innerText = (state.x/1000).toFixed(0);
            document.getElementById('val-y').innerText = (state.y/1000).toFixed(0);
            document.getElementById('val-vel').innerText = speed.toFixed(0);
            document.getElementById('val-fuel').innerText = state.fuel.toFixed(1);
            document.getElementById('val-zone').innerText = currentZone;
        }}

        function triggerExplosion(reason) {{
            state.exploded = true;
            document.getElementById('mission').innerText = "💥 FAILED: " + reason;
            rocketGroup.visible = false;
            
            // Particle Explosion
            const particleCount = 500;
            const geometry = new THREE.BufferGeometry();
            const positions = new Float32Array(particleCount * 3);
            const velocities = [];
            for (let i = 0; i < particleCount; i++) {{
                positions[i*3] = state.x; positions[i*3+1] = state.y; positions[i*3+2] = 0;
                velocities.push({{ x: (Math.random()-0.5)*20000, y: (Math.random()-0.5)*20000 }});
            }}
            geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
            const material = new THREE.PointsMaterial({{ size: 1000, color: 0xff3300, transparent: true }});
            const particles = new THREE.Points(geometry, material);
            particles.userData.vel = velocities;
            scene.add(particles);
        }}

        // --- 5. RENDER LOOP ---
        function animate() {{
            requestAnimationFrame(animate);
            updatePhysics();

            // Update Rocket Visuals
            if (!state.exploded) {{
                rocketGroup.position.set(state.x, state.y, 0);
                rocketGroup.rotation.z = -state.angle; // Rotate rocket to match thrust angle
            }}

            // Dynamic Camera (Zooms out as you leave Earth)
            let distToEarth = Math.sqrt(state.x*state.x + state.y*state.y);
            let zoom = Math.max(500, distToEarth * 1.5); 
            camera.position.set(state.x, state.y, zoom);
            camera.lookAt(state.x, state.y, 0);

            // Minimap Update
            miniRocket.position.set(state.x * 0.0000001, state.y * 0.0000001, 1);
            miniRenderer.render(miniScene, miniCamera);

            renderer.render(scene, camera);
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
