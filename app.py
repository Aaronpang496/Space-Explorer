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
        
        #hud {{ position: absolute; top: 10px; left: 10px; color: #38bdf8; text-shadow: 0 0 5px #38bdf8; font-size: 14px; background: rgba(0,0,0,0.7); padding: 12px; border-radius: 5px; border: 1px solid #38bdf8;}}
        #mission {{ position: absolute; top: 10px; left: 50%; transform: translateX(-50%); color: #fbbf24; text-align: center; font-size: 14px; font-weight: bold; text-shadow: 0 0 5px black; width: 60%;}}
        
        /* Position Controls higher up */
        #joystick-zone {{ position: absolute; bottom: 180px; left: 20px; width: 110px; height: 110px; background: rgba(255,255,255,0.15); border: 2px solid #38bdf8; border-radius: 50%; pointer-events: auto; touch-action: none; display: none;}}
        #joystick-knob {{ position: absolute; top: 30px; left: 30px; width: 46px; height: 46px; background: #38bdf8; border-radius: 50%; box-shadow: 0 0 10px #fff; }}
        
        #throttle-zone {{ position: absolute; bottom: 180px; right: 20px; width: 45px; height: 160px; background: rgba(255,255,255,0.15); border: 2px solid #ef4444; border-radius: 20px; pointer-events: auto; touch-action: none; display: none;}}
        #throttle-fill {{ position: absolute; bottom: 0; left: 0; width: 100%; height: 0%; background: #ef4444; border-radius: 18px;}}
        
        #minimap-container {{ position: absolute; top: 10px; right: 10px; width: 100px; height: 100px; border: 2px solid #38bdf8; border-radius: 50%; background: rgba(0,0,0,0.8); overflow: hidden; display: none;}}
        
        .action-btn {{ position: absolute; pointer-events: auto; background: rgba(0,0,0,0.8); color: white; border: 2px solid #38bdf8; padding: 10px; border-radius: 8px; font-family: inherit; font-weight: bold; font-size: 12px; display: none; z-index: 10000; }}
        #btn-gear {{ bottom: 180px; right: 80px; color: #22c55e; border-color: #22c55e; }}
        #btn-retro {{ bottom: 230px; right: 80px; color: #f59e0b; border-color: #f59e0b; }}
        #btn-reset {{ bottom: 180px; left: 140px; color: #ef4444; border-color: #ef4444; }}
        
        #loading {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: #000; color: #38bdf8; display: flex; justify-content: center; align-items: center; font-size: 24px; z-index: 100; transition: opacity 1s; }}
        #start-overlay {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(2, 6, 23, 0.85); z-index: 99999; display: flex; flex-direction: column; justify-content: center; align-items: center; pointer-events: auto; cursor: pointer; }}
        .start-text {{ color: #38bdf8; font-size: 24px; font-weight: bold; text-transform: uppercase; letter-spacing: 3px; text-align: center; text-shadow: 0 0 20px #38bdf8; animation: pulse 2s infinite; }}
        @keyframes pulse {{ 0% {{ opacity: 0.5; }} 50% {{ opacity: 1; }} 100% {{ opacity: 0.5; }} }}
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
        <div id="minimap-container"><canvas id="minimap" width="100" height="100"></canvas></div>
        
        <button class="action-btn" id="btn-gear">GEAR: UP</button>
        <button class="action-btn" id="btn-retro">RETRO</button>
        <button class="action-btn" id="btn-reset">RESET</button>
    </div>

    <script>
        let state = {{
            // SPAWN FIXED: X is offset so it doesn't divide by zero
            x: 500, y: 6371, vx: 0, vy: 0, 
            fuel: 100, throttle: 0, angle: 0, 
            gear: false, exploded: false, started: false,
            liftOffTime: 0 // Tracks when we actually leave the ground
        }};

        const G = 6.674e-11;
        const rocketMass = 100000; 
        const maxThrust = 1500000; // Tuned down for controllable speed

        const planets = {{
            Earth:   {{ m: 5.97e22, r: 6371, x: 0, y: 0, color: 0x1e3a8a, soi: 50000 }},
            Moon:    {{ m: 7.34e20, r: 1737, x: 100000, y: 0, color: 0x9ca3af, soi: 20000 }},
            Mars:    {{ m: 6.41e21, r: 3389, x: 200000, y: 0, color: 0xea580c, soi: 30000 }}
        }};

        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 100000000);
        const renderer = new THREE.WebGLRenderer({{ antialias: true }});
        renderer.setSize(window.innerWidth, window.innerHeight);
        document.body.appendChild(renderer.domElement);

        // Add Stars to the background
        const starsGeo = new THREE.BufferGeometry();
        const starsCount = 2000;
        const starsPos = new Float32Array(starsCount * 3);
        for(let i=0; i<starsCount*3; i++) starsPos[i] = (Math.random() - 0.5) * 1000000;
        starsGeo.setAttribute('position', new THREE.BufferAttribute(starsPos, 3));
        const starsMat = new THREE.PointsMaterial({{color: 0xffffff, size: 1000}});
        scene.add(new THREE.Points(starsGeo, starsMat));

        const sunLight = new THREE.DirectionalLight(0xffffff, 2);
        sunLight.position.set(500000, 500000, 500000);
        scene.add(sunLight);
        scene.add(new THREE.AmbientLight(0x404040));

        for (let p in planets) {{
            // Main Planet
            let geo = new THREE.SphereGeometry(planets[p].r, 32, 32);
            let mat = new THREE.MeshPhongMaterial({{color: planets[p].color, shininess: 10}});
            let mesh = new THREE.Mesh(geo, mat);
            mesh.position.set(planets[p].x, planets[p].y, 0);
            scene.add(mesh);

            // Atmosphere Glow
            let atmoGeo = new THREE.SphereGeometry(planets[p].r * 1.05, 32, 32);
            let atmoMat = new THREE.MeshBasicMaterial({{ color: 0x38bdf8, transparent: true, opacity: 0.15, side: THREE.BackSide }});
            let atmo = new THREE.Mesh(atmoGeo, atmoMat);
            atmo.position.set(planets[p].x, planets[p].y, 0);
            scene.add(atmo);

            // Gravity Ring
            let ringGeo = new THREE.RingGeometry(planets[p].soi - 500, planets[p].soi, 64);
            let ringMat = new THREE.MeshBasicMaterial({{ color: planets[p].color, side: THREE.DoubleSide, transparent: true, opacity: 0.2 }});
            let ring = new THREE.Mesh(ringGeo, ringMat);
            ring.position.set(planets[p].x, planets[p].y, 0);
            scene.add(ring);
        }}

        const rocketGroup = new THREE.Group();
        scene.add(rocketGroup);

        const fireGeo = new THREE.ConeGeometry(150, 400, 16);
        const fireMat = new THREE.MeshBasicMaterial({{color: 0xffaa00, transparent: true, opacity: 0.8, blending: THREE.AdditiveBlending}});
        const engineFire = new THREE.Mesh(fireGeo, fireMat);
        engineFire.rotation.x = Math.PI;
        engineFire.position.y = -200;
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
                const scaleFactor = 1000 / size.y;
                model.scale.set(scaleFactor, scaleFactor, scaleFactor);
                const center = box.getCenter(new THREE.Vector3());
                model.position.x = -center.x * scaleFactor;
                model.position.z = -center.z * scaleFactor;
                model.position.y = (-box.min.y * scaleFactor);
                rocketGroup.add(model);
                document.getElementById('loading').style.opacity = 0;
            }});
        }}

        const canvas = document.getElementById('minimap');
        const ctx = canvas.getContext('2d');
        function drawMinimap() {{
            ctx.clearRect(0, 0, 100, 100);
            let scale = 100 / 300000; 
            for (let p in planets) {{
                ctx.beginPath();
                ctx.arc(50 + planets[p].x * scale, 50 - planets[p].y * scale, Math.max(1, planets[p].r * scale * 2), 0, Math.PI*2);
                ctx.fillStyle = '#' + planets[p].color.toString(16).padStart(6, '0');
                ctx.fill();
            }}
            ctx.beginPath();
            ctx.arc(50 + state.x * scale, 50 - state.y * scale, 3, 0, Math.PI*2);
            ctx.fillStyle = '#ff0000';
            ctx.fill();
        }}

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
            document.getElementById('btn-gear').style.display = 'block';
            document.getElementById('btn-retro').style.display = 'block';
            document.getElementById('btn-reset').style.display = 'block';
            document.getElementById('mission').innerText = "Slide RED BAR up to launch.";
        }});

        joyZone.addEventListener('pointerdown', (e) => {{ isDraggingJoy = true; joyZone.setPointerCapture(e.pointerId); }});
        joyZone.addEventListener('pointerup', (e) => {{ isDraggingJoy = false; joyKnob.style.top = '30px'; joyKnob.style.left = '30px'; }});
        joyZone.addEventListener('pointermove', (e) => {{
            if (!isDraggingJoy) return;
            const rect = joyZone.getBoundingClientRect();
            let x = e.clientX - rect.left - 55; let y = e.clientY - rect.top - 55;
            const dist = Math.sqrt(x*x + y*y);
            if (dist > 35) {{ x = (x/35)*35; y = (y/35)*35; }}
            joyKnob.style.left = (30 + x) + 'px'; joyKnob.style.top = (30 + y) + 'px';
            state.angle = Math.atan2(x, -y); 
        }});

        throttleZone.addEventListener('pointerdown', (e) => {{ isDraggingThrottle = true; throttleZone.setPointerCapture(e.pointerId); }});
        throttleZone.addEventListener('pointerup', () => {{ isDraggingThrottle = false; }});
        throttleZone.addEventListener('pointermove', (e) => {{
            if (!isDraggingThrottle) return;
            const rect = throttleZone.getBoundingClientRect();
            let y = e.clientY - rect.top;
            if (y < 0) y = 0; if (y > 160) y = 160;
            let percent = 100 - (y / 160) * 100;
            state.throttle = percent;
            throttleFill.style.height = percent + '%';
        }});

        document.getElementById('btn-gear').onclick = function() {{
            state.gear = !state.gear;
            this.innerText = "GEAR: " + (state.gear ? "DOWN" : "UP");
        }};
        document.getElementById('btn-retro').onclick = function() {{
            state.vx *= 0.8; state.vy *= 0.8;
        }};
        document.getElementById('btn-reset').onclick = function() {{
            state.x = 500; state.y = 6371; state.vx = 0; state.vy = 0; state.fuel = 100; state.throttle = 0; state.exploded = false; state.liftOffTime = 0;
            rocketGroup.visible = true;
            throttleFill.style.height = '0%';
            document.getElementById('mission').innerText = "Reset. Slide RED BAR up to launch.";
        }};

        function updatePhysics() {{
            if (!state.started || state.exploded) return;

            let ax = 0, ay = 0;
            let currentZone = "Deep Space";

            for (let p in planets) {{
                let dx = planets[p].x - state.x;
                let dy = planets[p].y - state.y;
                let distSq = dx*dx + dy*dy;
                let dist = Math.sqrt(distSq);
                if (dist < 100) dist = 100; 

                if (dist < planets[p].soi) currentZone = p;

                let accel = (G * planets[p].m) / distSq;
                ax += accel * (dx / dist);
                ay += accel * (dy / dist);

                // COLLISION FIX: Only explode if you have actually lifted off
                if (dist < planets[p].r && state.throttle > 5 && !state.exploded) {{
                    triggerExplosion("CRASHED INTO " + p);
                }}
            }}

            if (state.throttle > 0) {{
                engineFire.visible = true;
                engineFire.scale.set(1 + Math.random()*0.2, 1 + Math.random()*0.5, 1 + Math.random()*0.2);
                let thrustAccel = (maxThrust * (state.throttle/100)) / rocketMass;
                ax += thrustAccel * Math.sin(state.angle);
                ay += thrustAccel * Math.cos(state.angle);
                state.fuel -= 0.02 * (state.throttle/100);
                if (state.fuel <= 0) {{ state.fuel = 0; state.throttle = 0; }}
            }} else {{
                engineFire.visible = false;
            }}

            state.vx += ax * 0.1;
            state.vy += ay * 0.1;
            state.x += state.vx * 0.1;
            state.y += state.vy * 0.1;

            let speed = Math.sqrt(state.vx*state.vx + state.vy*state.vy);
            
            if (!isNaN(state.x) && !isNaN(speed)) {{
                let alt = Math.sqrt(state.x*state.x + state.y*state.y) - 6371;
                document.getElementById('val-alt').innerText = Math.max(0, (alt/1000)).toFixed(1);
                document.getElementById('val-vel').innerText = (speed * 3.6).toFixed(0); 
                document.getElementById('val-fuel').innerText = state.fuel.toFixed(1);
                document.getElementById('val-zone').innerText = currentZone;
            }}
        }}

        function triggerExplosion(reason) {{
            state.exploded = true;
            document.getElementById('mission').innerText = "💥 FAILED: " + reason;
            rocketGroup.visible = false;
        }}

        function animate() {{
            requestAnimationFrame(animate);
            updatePhysics();
            drawMinimap();

            if (!isNaN(state.x) && !isNaN(state.y)) {{
                if (!state.exploded) {{
                    rocketGroup.position.set(state.x, state.y, 0);
                    rocketGroup.rotation.z = -state.angle; 
                }}

                // Slightly dynamic camera that keeps Earth in view but follows rocket
                let zoom = 20000; 
                camera.position.set(state.x, state.y, zoom);
                camera.lookAt(state.x, state.y, 0);
            }}
            
            renderer.render(scene, camera);
        }}
        
        animate();
    </script>
</body>
</html>
"""

components.html(game_html, height=900, scrolling=False)
