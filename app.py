import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="SFS 3D", layout="wide", initial_sidebar_state="collapsed")

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
        body { margin: 0; overflow: hidden; background-color: #000; font-family: 'Arial', sans-serif; touch-action: none; user-select: none; }
        canvas { display: block; }
        
        /* --- UI LAYER --- */
        #ui-layer { position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 99999; }
        
        /* VAB Menu */
        #vab-menu { position: absolute; top: 15px; left: 15px; width: 110px; background: rgba(0,0,0,0.85); border: 2px solid #555; border-radius: 10px; display: flex; flex-direction: column; align-items: center; padding: 10px 0; pointer-events: auto; z-index: 100000;}
        .part-btn { width: 90px; height: 50px; margin: 5px 0; background: #333; border: 2px solid #777; border-radius: 5px; color: white; font-size: 12px; font-weight: bold; display: flex; justify-content: center; align-items: center; cursor: pointer;}
        .part-btn:active { border-color: #00ffcc; background: #114444; }
        
        /* Top Bar */
        #top-bar { position: absolute; top: 15px; left: 50%; transform: translateX(-50%); display: flex; gap: 10px; pointer-events: auto; z-index: 100000;}
        .top-btn { background: #1e3a8a; color: white; border: 2px solid #60a5fa; padding: 10px 20px; font-size: 16px; font-weight: bold; border-radius: 5px; cursor: pointer;}
        
        /* Flight HUD */
        #hud { position: absolute; top: 15px; right: 15px; color: #fff; font-size: 14px; background: rgba(0,0,0,0.6); padding: 10px; border-radius: 5px; text-align: right; border-left: 3px solid #00ffcc; display: none; z-index: 100000;}
        
        /* Flight Controls */
        #throttle-zone { position: absolute; right: 20px; bottom: 80px; width: 45px; height: 200px; background: rgba(0,0,0,0.5); border: 2px solid #fff; border-radius: 22px; pointer-events: auto; display: none; z-index: 100000; }
        #throttle-fill { position: absolute; bottom: 0; width: 100%; height: 0%; background: linear-gradient(to top, #ff0000, #ffff00); border-radius: 20px;}
        
        #arrow-zone { position: absolute; left: 20px; bottom: 20px; display: none; gap: 20px; pointer-events: auto; z-index: 100000;}
        .arrow-btn { width: 70px; height: 70px; background: rgba(0,0,0,0.6); border: 2px solid #fff; border-radius: 10px; color: white; font-size: 35px; display: flex; justify-content: center; align-items: center; cursor: pointer;}
        
        #btn-legs { position: absolute; bottom: 80px; right: 80px; width: 80px; height: 40px; background: rgba(0,0,0,0.6); border: 2px solid #fff; color: white; border-radius: 5px; font-size: 12px; font-weight: bold; pointer-events: auto; display: none; z-index: 100000;}
        #btn-legs.deployed { border-color: #00ffcc; color: #00ffcc; }

        /* Map Overlay */
        #map-overlay { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 5, 15, 0.95); display: none; pointer-events: auto; z-index: 200000;}
        #map-canvas { position: absolute; top: 0; left: 0; width: 100%; height: 100%; }
        #map-title { position: absolute; top: 20px; left: 20px; color: white; font-size: 24px; font-weight: bold;}
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>
    <canvas id="gameCanvas"></canvas>
    
    <div id="ui-layer">
        <!-- Builder Menu -->
        <div id="vab-menu">
            <div class="part-btn" id="btn-add-tank">+ Fuel Tank</div>
            <div class="part-btn" id="btn-add-engine">+ Engine</div>
            <div class="part-btn" id="btn-add-pod">+ Command Pod</div>
        </div>

        <!-- Top Bar -->
        <div id="top-bar">
            <button class="top-btn" id="btn-launch">LAUNCH 🚀</button>
            <button class="top-btn" id="btn-map">MAP 🗺️</button>
            <button class="top-btn" id="btn-reset">RESET 🔄</button>
        </div>

        <!-- Flight HUD -->
        <div id="hud">
            ALT: <span id="val-alt">0</span> m<br>
            VEL: <span id="val-vel">0</span> m/s
        </div>
        
        <!-- Flight Controls -->
        <div id="throttle-zone"><div id="throttle-fill"></div></div>
        
        <div id="arrow-zone">
            <div class="arrow-btn" id="joy-left">◀</div>
            <div class="arrow-btn" id="joy-right">▶</div>
        </div>

        <button id="btn-legs">LEGS: UP</button>
    </div>

    <!-- Map Overlay -->
    <div id="map-overlay">
        <canvas id="map-canvas"></canvas>
        <div id="map-title">SOLAR SYSTEM</div>
    </div>

    <script>
        // --- 3D ENGINE SETUP ---
        const canvas = document.getElementById('gameCanvas');
        const renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;

        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x111827); // VAB Dark Blue
        
        // Perspective Camera (Allows 3D rotation)
        const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 100000);
        camera.position.set(20, 20, 40);

        // Add OrbitControls for drag-to-rotate
        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;
        controls.enablePan = false; // Keep focus on rocket

        // Lighting
        const sunLight = new THREE.DirectionalLight(0xffffff, 1.5);
        sunLight.position.set(50, 100, 50); 
        sunLight.castShadow = true;
        sunLight.shadow.mapSize.width = 2048;
        sunLight.shadow.mapSize.height = 2048;
        scene.add(sunLight);
        
        const ambientLight = new THREE.AmbientLight(0x404040, 1.5);
        scene.add(ambientLight);

        // Ground & Pad
        const groundGeo = new THREE.PlaneGeometry(10000, 10000);
        const groundMat = new THREE.MeshStandardMaterial({color: 0x2e4a2e, roughness: 1});
        const ground = new THREE.Mesh(groundGeo, groundMat);
        ground.rotation.x = -Math.PI / 2;
        ground.position.y = -0.1;
        ground.receiveShadow = true;
        ground.visible = false; 
        scene.add(ground);

        const padGeo = new THREE.CylinderGeometry(10, 10, 1, 32);
        const padMat = new THREE.MeshStandardMaterial({color: 0x444444, roughness: 0.8});
        const pad = new THREE.Mesh(padGeo, padMat);
        pad.position.y = -0.5;
        pad.receiveShadow = true;
        scene.add(pad);

        // Rocket Group
        const rocketGroup = new THREE.Group();
        rocketGroup.position.set(0, 0, 0);
        scene.add(rocketGroup);

        // Materials
        const matTank = new THREE.MeshStandardMaterial({color: 0xf0f0f0, roughness: 0.2, metalness: 0.1});
        const matEngine = new THREE.MeshStandardMaterial({color: 0x222222, metalness: 0.9, roughness: 0.3});
        const matPod = new THREE.MeshStandardMaterial({color: 0x888888, roughness: 0.6, metalness: 0.4});
        const matLeg = new THREE.MeshStandardMaterial({color: 0x666666, metalness: 0.8, roughness: 0.4});

        // --- BUILD LOGIC ---
        let currentHeight = 0;
        let hasEngine = false;
        let hasPod = false;
        let legs = [];
        let legsDeployed = false;

        function addTank() {
            const geo = new THREE.CylinderGeometry(1.5, 1.5, 6, 32);
            const mesh = new THREE.Mesh(geo, matTank);
            mesh.position.y = currentHeight + 3;
            mesh.castShadow = true;
            mesh.receiveShadow = true;
            rocketGroup.add(mesh);
            currentHeight += 6;
        }

        function addEngine() {
            if (hasEngine) return;
            const geo = new THREE.CylinderGeometry(1.5, 2.2, 3, 32);
            const mesh = new THREE.Mesh(geo, matEngine);
            mesh.position.y = currentHeight + 1.5;
            mesh.castShadow = true;
            mesh.receiveShadow = true;
            rocketGroup.add(mesh);
            currentHeight += 3;
            hasEngine = true;

            // Add 3D Landing Legs
            for(let i=0; i<2; i++) {
                const legGroup = new THREE.Group();
                
                // The leg strut
                const legGeo = new THREE.CylinderGeometry(0.15, 0.15, 4, 8);
                const legMesh = new THREE.Mesh(legGeo, matLeg);
                legMesh.position.y = 2;
                legMesh.castShadow = true;
                legGroup.add(legMesh);

                // The footpad
                const footGeo = new THREE.CylinderGeometry(0.5, 0.5, 0.2, 16);
                const footMesh = new THREE.Mesh(footGeo, matLeg);
                footMesh.position.y = 4;
                legGroup.add(footMesh);

                // Position the leg on the engine
                legGroup.position.set(i===0 ? -1.5 : 1.5, 1, 0);
                
                // Folded up by default
                legGroup.rotation.z = i===0 ? Math.PI/2 : -Math.PI/2;
                legGroup.visible = false;
                
                rocketGroup.add(legGroup);
                legs.push({ group: legGroup, side: i===0 ? -1 : 1 });
            }
        }

        function addPod() {
            if (hasPod) return;
            const geo = new THREE.CylinderGeometry(1.2, 1.5, 3, 32);
            const mesh = new THREE.Mesh(geo, matPod);
            mesh.position.y = currentHeight + 1.5;
            mesh.castShadow = true;
            mesh.receiveShadow = true;
            rocketGroup.add(mesh);
            currentHeight += 3;
            hasPod = true;
        }

        // Default Build
        addEngine();
        addTank();
        addTank();
        addPod();

        document.getElementById('btn-add-tank').onclick = () => { if(state.mode==="vab") addTank(); };
        document.getElementById('btn-add-engine').onclick = () => { if(state.mode==="vab") addEngine(); };
        document.getElementById('btn-add-pod').onclick = () => { if(state.mode==="vab") addPod(); };

        // Fire Particles
        const particleCount = 200;
        const fireGeo = new THREE.BufferGeometry();
        const firePositions = new Float32Array(particleCount * 3);
        const fireVelocities = [];
        for (let i = 0; i < particleCount; i++) {
            firePositions[i*3] = (Math.random() - 0.5) * 2;
            firePositions[i*3+1] = 0;
            firePositions[i*3+2] = (Math.random() - 0.5) * 2;
            fireVelocities.push({x: (Math.random()-0.5)*2, y: -Math.random()*20-5, z: (Math.random()-0.5)*2});
        }
        fireGeo.setAttribute('position', new THREE.BufferAttribute(firePositions, 3));
        
        // Fire Texture (Glow)
        const canvasFire = document.createElement('canvas');
        canvasFire.width = 32; canvasFire.height = 32;
        const ctxFire = canvasFire.getContext('2d');
        const gradFire = ctxFire.createRadialGradient(16, 16, 0, 16, 16, 16);
        gradFire.addColorStop(0, 'rgba(255, 255, 255, 1)');
        gradFire.addColorStop(0.3, 'rgba(255, 200, 0, 1)');
        gradFire.addColorStop(1, 'rgba(255, 0, 0, 0)');
        ctxFire.fillStyle = gradFire;
        ctxFire.fillRect(0, 0, 32, 32);
        const fireTexture = new THREE.CanvasTexture(canvasFire);

        const fireMat = new THREE.PointsMaterial({
            color: 0xffffff, 
            size: 4, 
            map: fireTexture, 
            transparent: true, 
            blending: THREE.AdditiveBlending,
            depthWrite: false
        });
        const fireParticles = new THREE.Points(fireGeo, fireMat);
        fireParticles.visible = false;
        rocketGroup.add(fireParticles);

        // --- PLANETS DATA ---
        const planets = [
            { name: "Earth", color: "#4a90e2", x: 0, y: 0, mapX: 0.4, mapY: 0.5 },
            { name: "Moon", color: "#9ca3af", x: 15000, y: 0, mapX: 0.5, mapY: 0.5 },
            { name: "Mars", color: "#ea580c", x: -20000, y: 0, mapX: 0.6, mapY: 0.5 },
            { name: "Jupiter", color: "#d4a373", x: 30000, y: 0, mapX: 0.7, mapY: 0.5 }
        ];

        // --- GAME STATE ---
        let state = {
            mode: "vab", 
            y: 0, vy: 0, vx: 0, x: 0,
            angle: 0, throttle: 0,
            exploded: false,
            currentPlanet: planets[0],
            lastTime: performance.now()
        };

        const GRAVITY = 9.81;

        // --- CONTROLS ---
        let leftPressed = false;
        let rightPressed = false;
        const throttleZone = document.getElementById('throttle-zone');
        const throttleFill = document.getElementById('throttle-fill');

        throttleZone.addEventListener('pointerdown', (e) => { throttleZone.setPointerCapture(e.pointerId); });
        throttleZone.addEventListener('pointermove', (e) => {
            if (e.buttons === 0) return;
            const rect = throttleZone.getBoundingClientRect();
            let y = e.clientY - rect.top;
            if (y < 0) y = 0; if (y > 200) y = 200;
            let percent = 100 - (y / 200) * 100;
            state.throttle = percent / 100;
            throttleFill.style.height = percent + '%';
        });

        document.getElementById('joy-left').addEventListener('pointerdown', () => { leftPressed = true; });
        document.getElementById('joy-left').addEventListener('pointerup', () => { leftPressed = false; });
        document.getElementById('joy-right').addEventListener('pointerdown', () => { rightPressed = true; });
        document.getElementById('joy-right').addEventListener('pointerup', () => { rightPressed = false; });

        document.getElementById('btn-legs').onclick = function() {
            legsDeployed = !legsDeployed;
            this.innerText = legsDeployed ? "LEGS: DOWN" : "LEGS: UP";
            if(legsDeployed) this.classList.add('deployed');
            else this.classList.remove('deployed');

            // Animate Legs Out/In
            legs.forEach(l => {
                l.group.visible = true; // Make visible to see them deploy
                if(legsDeployed) {
                    l.group.rotation.z = l.side * (Math.PI / 4); // Swing out
                } else {
                    l.group.rotation.z = l.side * (Math.PI / 2); // Fold up
                }
            });
        };

        // --- LAUNCH LOGIC ---
        document.getElementById('btn-launch').onclick = function() {
            if (state.mode === "vab") {
                state.mode = "flight";
                document.getElementById('vab-menu').style.display = 'none';
                this.style.display = 'none';
                document.getElementById('hud').style.display = 'block';
                document.getElementById('throttle-zone').style.display = 'block';
                document.getElementById('arrow-zone').style.display = 'flex';
                document.getElementById('btn-legs').style.display = 'block';
                
                // Change scene for flight
                scene.background = new THREE.Color(0x87CEEB); 
                ground.visible = true;
                pad.visible = true;

                // Reset rocket rotation & position
                rocketGroup.rotation.set(0, 0, 0);
                rocketGroup.position.set(0, 0, 0);
                state.y = 0; state.x = 0; state.vy = 0; state.vx = 0;

                // Hide legs if retracted
                if(!legsDeployed) {
                    legs.forEach(l => l.group.visible = false);
                }
            }
        };

        document.getElementById('btn-reset').onclick = () => window.location.reload();

        // --- MAP LOGIC ---
        const mapOverlay = document.getElementById('map-overlay');
        const mapCanvas = document.getElementById('map-canvas');
        const mapCtx = mapCanvas.getContext('2d');

        document.getElementById('btn-map').onclick = () => {
            if (state.mode !== "flight") return;
            mapOverlay.style.display = 'block';
            mapCanvas.width = window.innerWidth;
            mapCanvas.height = window.innerHeight;
            
            // Draw Map
            mapCtx.fillStyle = "#000511";
            mapCtx.fillRect(0, 0, mapCanvas.width, mapCanvas.height);
            
            // Orbits
            mapCtx.strokeStyle = "rgba(255,255,255,0.2)";
            mapCtx.beginPath();
            mapCtx.moveTo(0, mapCanvas.height * 0.5);
            mapCtx.lineTo(mapCanvas.width, mapCanvas.height * 0.5);
            mapCtx.stroke();

            planets.forEach(p => {
                const px = p.mapX * mapCanvas.width;
                const py = p.mapY * mapCanvas.height;
                
                mapCtx.fillStyle = p.color;
                mapCtx.beginPath();
                mapCtx.arc(px, py, 20, 0, Math.PI * 2);
                mapCtx.fill();
                
                mapCtx.fillStyle = "#fff";
                mapCtx.font = "16px Arial";
                mapCtx.textAlign = "center";
                mapCtx.fillText(p.name, px, py + 40);
            });
        };

        mapCanvas.addEventListener('pointerdown', (e) => {
            const rect = mapCanvas.getBoundingClientRect();
            const x = (e.clientX - rect.left) / rect.width;
            const y = (e.clientY - rect.top) / rect.height;

            planets.forEach(p => {
                const dist = Math.sqrt(Math.pow(x - p.mapX, 2) + Math.pow(y - p.mapY, 2));
                if (dist < 0.1) {
                    // TELEPORT SAFELY INTO ORBIT (5000m up)
                    state.currentPlanet = p;
                    state.x = p.x;
                    state.y = 5000; 
                    state.vx = 0; state.vy = 0;
                    state.angle = 0;
                    
                    // Change environment
                    if (p.name === "Earth") scene.background = new THREE.Color(0x87CEEB);
                    else scene.background = new THREE.Color(0x000000);
                    
                    // Move camera far up too
                    camera.position.set(p.x + 20, 5020, 40);
                    
                    mapOverlay.style.display = 'none';
                }
            });
        });

        // --- PHYSICS & RENDER LOOP ---
        function animate() {
            requestAnimationFrame(animate);
            
            let dt = (performance.now() - state.lastTime) / 1000;
            state.lastTime = performance.now();
            if (dt > 0.1) dt = 0.1;

            if (state.mode === "flight" && !state.exploded) {
                // Rotation
                if (leftPressed) rocketGroup.rotation.z += 1.5 * dt;
                if (rightPressed) rocketGroup.rotation.z -= 1.5 * dt;
                state.angle = -rocketGroup.rotation.z; // Sync state angle

                // Thrust
                let ay = -GRAVITY;
                if (state.throttle > 0 && hasEngine) {
                    let thrustAccel = 40 * state.throttle;
                    ay += thrustAccel * Math.cos(state.angle);
                    state.vx += thrustAccel * Math.sin(state.angle) * dt;
                    
                    fireParticles.visible = true;
                    const positions = fireParticles.geometry.attributes.position.array;
                    for(let i=0; i<particleCount; i++) {
                        positions[i*3+1] += fireVelocities[i].y * dt;
                        if (positions[i*3+1] < -15) {
                            positions[i*3] = (Math.random() - 0.5) * 2;
                            positions[i*3+1] = 0;
                            positions[i*3+2] = (Math.random() - 0.5) * 2;
                        }
                    }
                    fireParticles.geometry.attributes.position.needsUpdate = true;
                } else {
                    fireParticles.visible = false;
                }

                state.vy += ay * dt;
                state.x += state.vx * dt;
                state.y += state.vy * dt;

                // Ground Collision
                if (state.y < 0) {
                    state.y = 0;
                    if (Math.abs(state.vy) > 5) {
                        state.exploded = true;
                        scene.background = new THREE.Color(0xff0000);
                        document.getElementById('hud').innerText = "CRASHED";
                        rocketGroup.visible = false;
                    } else if (!legsDeployed) {
                        state.exploded = true;
                        scene.background = new THREE.Color(0xff0000);
                        document.getElementById('hud').innerText = "CRUSHED (NO GEAR)";
                        rocketGroup.visible = false;
                    } else {
                        state.vy = 0; state.vx = 0; state.angle = 0;
                        rocketGroup.rotation.z = 0;
                        state.throttle = 0;
                        throttleFill.style.height = '0%';
                        document.getElementById('hud').innerText = "LANDED SAFELY";
                    }
                }

                // Update Rocket Position
                rocketGroup.position.set(state.x, state.y, 0);

                // Camera Follow (Smoothly move camera target)
                controls.target.set(state.x, state.y + 10, 0);
                
                // Update camera position based on rocket
                // If the user isn't dragging, we keep the camera relative to the rocket
                camera.position.x = state.x + 20;
                camera.position.y = state.y + 20;

                // HUD
                document.getElementById('val-alt').innerText = state.y.toFixed(1);
                document.getElementById('val-vel').innerText = Math.sqrt(state.vx*state.vx + state.vy*state.vy).toFixed(1);
            } 
            
            if (state.mode === "vab") {
                 // VAB camera slowly pans up as rocket grows
                 controls.target.set(0, currentHeight / 2, 0);
                 camera.position.set(30, currentHeight / 2 + 10, 40);
            }

            controls.update();
            renderer.render(scene, camera);
        }
        animate();
    </script>
</body>
</html>
"""

components.html(game_html, height=900, scrolling=False)
