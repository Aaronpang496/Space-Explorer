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

        #start-screen { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.9); display: flex; flex-direction: column; justify-content: center; align-items: center; pointer-events: auto; z-index: 1000000; padding: 0 20px; box-sizing: border-box; }
        #btn-start { background: #00ffcc; color: #000; border: none; padding: 20px 50px; font-size: 28px; font-weight: bold; border-radius: 10px; cursor: pointer; box-shadow: 0 0 20px #00ffcc; }
        .title { color: white; font-size: 48px; font-weight: bold; margin-bottom: 12px; text-shadow: 0 0 20px #4a90e2; text-align: center; }
        .subtitle { color: #7ab; font-size: 13px; margin-bottom: 20px; text-align: center; max-width: 320px; line-height: 1.6;}
        .gold-guide { color: #ffcc44; font-size: 12px; margin-bottom: 30px; text-align: center; line-height: 1.75; max-width: 320px; background: rgba(255,204,68,0.08); padding: 12px 18px; border-radius: 8px; border: 1px solid rgba(255,204,68,0.3); }

        #vab-menu {
            position: absolute; top: 10px; left: 10px; width: 100px;
            background: rgba(20, 30, 40, 0.95); border: 2px solid #34495e; border-radius: 10px;
            display: none; flex-direction: column; align-items: center;
            padding: 10px 0; pointer-events: auto;
            max-height: 82vh; overflow-y: auto; overflow-x: hidden;
            -webkit-overflow-scrolling: touch; overscroll-behavior: contain; touch-action: pan-y;
            z-index: 100000; scrollbar-width: thin; scrollbar-color: #00ffcc #222;
            box-shadow: 0 4px 12px rgba(0,0,0,0.5);
        }
        #vab-menu::-webkit-scrollbar { width: 6px; }
        #vab-menu::-webkit-scrollbar-track { background: #111; border-radius: 3px; }
        #vab-menu::-webkit-scrollbar-thumb { background: #4a90e2; border-radius: 3px; }

        .vab-scroll-hint { position: absolute; left: 10px; width: 100px; text-align: center; font-size: 14px; color: #00ffcc; pointer-events: none; z-index: 100001; display: none; opacity: 0.9; text-shadow: 0 0 6px #00ffcc; }
        .vab-scroll-hint.up { top: 4px; }
        .vab-scroll-hint.down { bottom: 4px; }
        .vab-scroll-hint.visible { display: block; }

        .part-btn { width: 80px; height: 45px; margin: 3px 0; background: #2c3e50; border: 2px solid #34495e; border-radius: 5px; cursor: grab; display: flex; flex-direction: column; justify-content: center; align-items: center; position: relative; touch-action: none;}
        .part-btn.active { border-color: #00ffcc; background: #114444; }
        .part-btn span { font-size: 8px; color: #aaa; position: absolute; bottom: 2px; font-weight: bold;}
        .part-btn.locked { opacity: 0.6; filter: grayscale(0.7); cursor: pointer; border-color: #886622;}
        .part-btn.locked span { color: #ffcc44; }
        .part-btn.locked::before { content: "🔒"; position: absolute; top: 1px; right: 2px; font-size: 11px; color: #ffcc44; text-shadow: 0 0 4px #000; z-index: 2; }
        .part-btn.locked::after { content: ""; position: absolute; inset: 0; background: rgba(0,0,0,0.25); border-radius: 4px; pointer-events: none; }
        .part-section { width: 88px; margin: 8px 0 4px 0; padding: 6px 0 4px 0; border-top: 2px solid #ffcc44; font-size: 9px; color: #ffcc44; text-align: center; letter-spacing: 1px; font-weight: bold; }

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
        .m-gyro { width: 16px; height: 10px; background: #fa4; border-radius: 5px; box-shadow: 0 0 6px #fa4; }
        .m-heat { width: 28px; height: 8px; background: #844; clip-path: polygon(0 0, 100% 0, 80% 100%, 20% 100%); box-shadow: 0 0 4px #f84; }
        .m-booster-l { width: 14px; height: 38px; background: #fdd; border: 1px solid #e88; border-radius: 5px 5px 0 0; }
        .m-tank-xl { width: 26px; height: 46px; background: linear-gradient(90deg,#d8c8ee,#fff,#a890cc); border: 2px solid #a890cc; }
        .m-engine-ion { width: 18px; height: 14px; background: #3af; clip-path: polygon(30% 0%, 70% 0%, 100% 100%, 0% 100%); box-shadow: 0 0 8px #3af; }
        .m-engine-xl { width: 26px; height: 20px; background: #222; clip-path: polygon(20% 0%, 80% 0%, 100% 100%, 0% 100%); box-shadow: inset 0 -3px 0 #f90; }

        #vab-stats { position: absolute; top: 10px; right: 10px; width: 175px; background: rgba(20, 30, 40, 0.9); border: 2px solid #34495e; border-radius: 10px; padding: 10px; color: white; display: none; flex-direction: column; z-index: 100000; pointer-events: none; box-shadow: 0 4px 12px rgba(0,0,0,0.5);}
        .stat-row { display: flex; justify-content: space-between; margin-bottom: 5px; font-size: 12px;}
        .stat-val { color: #00ffcc; font-weight: bold;}
        .stat-gold { color: #ffcc44 !important; font-size: 16px;}
        .stat-hint { margin-top: 8px; padding-top: 8px; border-top: 1px solid #333; font-size: 10px; color: #8ab; line-height: 1.55; }
        .stat-hint b { color: #ffcc44; }

        #trash-can { position: absolute; bottom: 20px; right: 20px; width: 68px; height: 68px; background: rgba(255,0,0,0.3); border: 2px dashed #ff4444; border-radius: 50%; display: none; justify-content: center; align-items: center; font-size: 32px; pointer-events: auto; z-index: 100000; transition: all 0.2s; }
        #trash-can.hover { background: rgba(255,0,0,0.85); border-style: solid; transform: scale(1.12); }

        #top-bar { position: absolute; top: 10px; left: 50%; transform: translateX(-50%); display: none; gap: 10px; pointer-events: auto; z-index: 100000;}
        
        .top-btn { background: #2c3e50; color: white; border: 2px solid #4a90e2; padding: 10px 20px; font-size: 14px; font-weight: bold; border-radius: 8px; cursor: pointer; box-shadow: 0 4px 6px rgba(0,0,0,0.3);}
        .top-btn:active { background: #4a90e2; }

        /* SFS HUD */
        #hud { position: absolute; top: 20px; right: 20px; color: #fff; font-family: 'Segoe UI', Arial, sans-serif; font-size: 13px; text-align: right; display: none; z-index: 100000; line-height: 1.4; text-shadow: 1px 1px 2px #000;}
        #hud .val { font-weight: bold; font-size: 16px; }
        #hud-space { color: #00ffcc; font-weight: bold; display: none; font-size: 16px; margin-bottom: 5px;}

        /* Moved Fuel Gauges */
        #fuel-gauges { position: absolute; bottom: 20px; left: 20px; display: none; flex-direction: column; gap: 4px; z-index: 100000; pointer-events: none;}
        .fuel-row { display: flex; align-items: center; gap: 10px; }
        .fuel-text { color: #fff; font-size: 12px; font-weight: bold; text-shadow: 1px 1px 2px #000; width: 70px;}
        .fuel-bar-bg { width: 80px; height: 10px; background: rgba(0,0,0,0.5); border: 1px solid #888; }
        .fuel-bar-fill { height: 100%; background: #ddd; width: 100%; transition: width 0.1s; }

        #heat-ui { position: absolute; bottom: 20px; left: 20px; display: none; z-index: 100000; color: #ff8844; font-size: 12px; font-weight: bold; text-shadow: 1px 1px 2px #000;}

        /* Moved Throttle and Buttons to avoid overlap */
        #throttle-zone { position: absolute; right: 15px; bottom: 140px; width: 35px; height: 130px; background: rgba(44, 62, 80, 0.4); border: 2px solid #7f8c8d; border-radius: 20px; pointer-events: auto; display: none; z-index: 100000; backdrop-filter: blur(5px); box-shadow: 0 4px 12px rgba(0,0,0,0.5);}
        #throttle-fill { position: absolute; bottom: 0; width: 100%; height: 0%; background: #fff; border-radius: 18px;}

        /* Centered Arrow Buttons Moved Up */
        #arrow-zone { position: absolute; left: 50%; transform: translateX(-50%); bottom: 90px; display: none; gap: 20px; pointer-events: auto; z-index: 100000;}
        .arrow-btn { width: 65px; height: 60px; background: rgba(44, 62, 80, 0.6); border: none; border-radius: 8px; color: #fff; font-size: 24px; display: flex; justify-content: center; align-items: center; cursor: pointer; backdrop-filter: blur(5px); touch-action: none; transition: transform 0.05s, background 0.05s; box-shadow: 0 4px 12px rgba(0,0,0,0.5);}
        .arrow-btn:active { background: rgba(52, 152, 219, 0.8); transform: scale(0.94); }

        #btn-stage { position: absolute; bottom: 20px; right: 70px; width: 60px; height: 60px; background: rgba(44, 62, 80, 0.6); border: none; color: white; border-radius: 8px; font-size: 12px; font-weight: bold; pointer-events: auto; display: none; z-index: 100000; backdrop-filter: blur(5px); box-shadow: 0 4px 12px rgba(0,0,0,0.5);}
        #btn-legs { position: absolute; bottom: 90px; right: 70px; width: 60px; height: 40px; background: rgba(44, 62, 80, 0.6); border: none; color: white; border-radius: 8px; font-size: 11px; font-weight: bold; pointer-events: auto; display: none; z-index: 100000; backdrop-filter: blur(5px); box-shadow: 0 4px 12px rgba(0,0,0,0.5);}
        #btn-legs.deployed { color: #00ffcc; }
        
        #btn-map { position: absolute; top: 15px; left: 15px; width: 50px; height: 35px; background: rgba(44, 62, 80, 0.6); border: none; color: white; border-radius: 6px; font-size: 12px; font-weight: bold; pointer-events: auto; display: none; z-index: 100000; backdrop-filter: blur(5px); box-shadow: 0 4px 12px rgba(0,0,0,0.5);}
        #btn-exit { position: absolute; top: 15px; left: 75px; width: 50px; height: 35px; background: rgba(44, 62, 80, 0.6); border: none; color: white; border-radius: 6px; font-size: 12px; font-weight: bold; pointer-events: auto; display: none; z-index: 100000; backdrop-filter: blur(5px); cursor: pointer; box-shadow: 0 4px 12px rgba(0,0,0,0.5); }

        #minimap-container { position: absolute; top: 60px; right: 15px; width: 80px; height: 80px; border: 2px solid #34495e; border-radius: 50%; background: rgba(0,0,0,0.8); overflow: hidden; display: none; z-index: 100000; box-shadow: 0 4px 12px rgba(0,0,0,0.5);}

        #map-overlay { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 5, 15, 0.97); display: none; pointer-events: auto; z-index: 200000;}
        #map-canvas { position: absolute; top: 0; left: 0; width: 100%; height: 100%; }
        #map-title { position: absolute; top: 20px; left: 80px; color: white; font-size: 24px; font-weight: bold;}
        #map-hint { position: absolute; bottom: 24px; left: 0; width: 100%; text-align: center; color: #9ab; font-size: 13px; }

        #btn-map-exit { position: absolute; top: 20px; left: 20px; background: #2c3e50; color: white; border: 2px solid #4a90e2; padding: 10px 20px; font-size: 14px; font-weight: bold; border-radius: 8px; cursor: pointer; z-index: 200001; box-shadow: 0 4px 6px rgba(0,0,0,0.3);}
        #btn-map-exit:active { background: #4a90e2; }

        #map-warp-info {
            position: absolute; bottom: 80px; left: 50%; transform: translateX(-50%);
            background: rgba(20, 30, 40, 0.9); border: 2px solid #00ffcc; border-radius: 10px;
            padding: 15px 30px; color: white; text-align: center; display: none;
            z-index: 200001; pointer-events: none;
        }
        #map-target-name { font-size: 24px; font-weight: bold; color: #00ffcc; }
        #map-target-dist { font-size: 14px; color: #ffcc44; margin-top: 5px; }

        #status-msg { position: absolute; top: 30%; left: 50%; transform: translate(-50%, -50%); font-size: 26px; font-weight: bold; text-align: center; display: none; text-shadow: 2px 2px 5px #000; pointer-events: none; z-index: 1000000; max-width: 90%;}

        #btn-rebuild { position: absolute; bottom: 30px; left: 50%; transform: translateX(-50%); display: none; padding: 15px 30px; background: #2c3e50; color: #fff; border: 2px solid #4a90e2; border-radius: 8px; font-size: 16px; font-weight: bold; pointer-events: auto; z-index: 100000; cursor: pointer; box-shadow: 0 4px 12px rgba(0,0,0,0.5);}

        #planet-info {
            position: absolute; top: 22%; left: 50%; transform: translateX(-50%);
            background: rgba(20, 30, 40, 0.95); border: 2px solid #00ffcc; border-radius: 12px;
            padding: 16px 24px; color: white; text-align: center; display: none;
            z-index: 1000000; pointer-events: none; min-width: 240px;
            box-shadow: 0 0 40px rgba(0,255,204,0.35);
        }
        #planet-info h2 { margin: 0 0 6px 0; color: #00ffcc; font-size: 26px; letter-spacing: 1px;}
        #planet-info .fact { font-size: 12px; color: #aaccee; margin-bottom: 10px; font-style: italic; }
        #planet-info .row { font-size: 12px; color: #fff; display: flex; justify-content: space-between; padding: 3px 0; gap: 20px;}
        #planet-info .row span:last-child { color: #ffcc44; font-weight: bold;}

        #warp-flash { position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: radial-gradient(circle, #ffffff 0%, #aaddff 40%, rgba(0,0,20,0) 100%);
            opacity: 0; pointer-events: none; z-index: 500000; transition: opacity 0.3s ease-out; }
        #warp-flash.active { opacity: 1; }

        #gold-popup { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
            font-size: 40px; font-weight: bold; color: #ffcc44; text-shadow: 0 0 20px #ffcc44, 2px 2px 4px #000;
            pointer-events: none; z-index: 2000000; opacity: 0; transition: opacity 0.4s, transform 0.4s; }
        #gold-popup.show { opacity: 1; transform: translate(-50%, -70%); }
    </style>
</head>
<body>
    <canvas id="gameCanvas"></canvas>

    <div id="ui-layer">
        <div id="start-screen">
            <div class="title">SPACE EXPLORER</div>
            <div class="subtitle">Build, Launch, and Explore the Solar System.</div>
            <div class="gold-guide">
                🪙 <b>How to earn gold:</b><br>
                +25 &nbsp;first safe landing on a planet<br>
                +50 &nbsp;first time reaching space<br>
                +10 &nbsp;reach 1 km (once per planet)<br>
                +25 &nbsp;reach 5 km (once per planet)<br>
                +50 &nbsp;reach 10 km (once per planet)<br>
                +100 reach 25 km (once per planet)
            </div>
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

            <div class="part-section">⚡ ADVANCED ⚡</div>
            <div class="part-btn locked" data-type="gyroscope"><div class="m-gyro"></div><span>Gyro · 60🪙</span></div>
            <div class="part-btn locked" data-type="heat_shield"><div class="m-heat"></div><span>Heat Sh · 80🪙</span></div>
            <div class="part-btn locked" data-type="booster_large"><div class="m-booster-l"></div><span>Booster L · 100🪙</span></div>
            <div class="part-btn locked" data-type="tank_xl"><div class="m-tank-xl"></div><span>Tank XL · 150🪙</span></div>
            <div class="part-btn locked" data-type="engine_ion"><div class="m-engine-ion"></div><span>Ion Eng · 200🪙</span></div>
            <div class="part-btn locked" data-type="engine_xl"><div class="m-engine-xl"></div><span>Engine XL · 250🪙</span></div>
        </div>

        <div class="vab-scroll-hint up">▲</div>
        <div class="vab-scroll-hint down">▼</div>

        <div id="vab-stats">
            <div class="stat-row"><span style="color:#ffcc44">🪙 Gold:</span> <span class="stat-val stat-gold" id="stat-gold">0</span></div>
            <div class="stat-row"><span>Mass:</span> <span class="stat-val" id="stat-mass">0 kg</span></div>
            <div class="stat-row"><span>Fuel:</span> <span class="stat-val" id="stat-fuel">0 kg</span></div>
            <div class="stat-row"><span>Thrust:</span> <span class="stat-val" id="stat-thrust">0 kN</span></div>
            <div class="stat-hint">
                Drag screen to <b>pan</b> · Tap 🔒 to <b>unlock</b><br>
                🪙 +25 landing · +50 space · +10/+25/+50/+100 altitude
            </div>
        </div>

        <div id="trash-can">🗑️</div>

        <div id="top-bar">
            <button class="top-btn" id="btn-launch">LAUNCH 🚀</button>
            <button class="top-btn" id="btn-reset">RESET 🔄</button>
        </div>

        <button id="btn-map">Map</button>
        <button id="btn-exit">Exit</button>
        <div id="minimap-container"><canvas id="minimap" width="80" height="80"></canvas></div>

        <div id="hud">
            <span id="hud-space">★ IN SPACE ★</span>
            <span id="hud-planet" style="display:none;">Earth</span>
            Height:<br>
            <span class="val" id="val-alt">0m</span><br>
            Velocity:<br>
            <span class="val" id="val-vel">0m/s</span><br>
            <span style="color:#ffcc44; margin-top:5px; display:inline-block;">🪙 <span id="val-gold">0</span></span>
        </div>

        <div id="fuel-gauges">
            <div class="fuel-row">
                <div class="fuel-text">Liquid fuel:</div>
                <div class="fuel-bar-bg"><div class="fuel-bar-fill" id="fuel-bar-1"></div></div>
            </div>
        </div>
        <div id="heat-ui">Heat Shield: <span id="val-heat">0</span>°C</div>

        <div id="throttle-zone"><div id="throttle-fill"></div></div>
        
        <div id="arrow-zone">
            <div class="arrow-btn" id="joy-left">◀</div>
            <div class="arrow-btn" id="joy-right">▶</div>
        </div>
        
        <button id="btn-stage">Stage</button>
        <button id="btn-legs">Legs</button>

        <div id="planet-info">
            <h2 id="pi-name">Earth</h2>
            <div class="fact" id="pi-fact"></div>
            <div class="row"><span>Gravity</span><span id="pi-gravity"></span></div>
            <div class="row"><span>Atmosphere</span><span id="pi-atmo"></span></div>
            <div class="row"><span>Best altitude</span><span id="pi-best"></span></div>
        </div>

        <div id="status-msg"></div>
        <div id="gold-popup"></div>
        <button id="btn-rebuild">REBUILD 🔄</button>
    </div>

    <div id="map-overlay">
        <canvas id="map-canvas"></canvas>
        <button id="btn-map-exit">EXIT</button>
        <div id="map-title">SOLAR SYSTEM MAP</div>
        <div id="map-warp-info">
            <div id="map-target-name"></div>
            <div id="map-target-dist"></div>
        </div>
        <div id="map-hint">Tap a planet to warp there</div>
    </div>

    <div id="warp-flash"></div>

    <script>
    function fitParent() {
        try {
            const f = window.frameElement;
            if (!f) return;
            f.style.width    = window.parent.innerWidth  + 'px';
            f.style.height   = window.parent.innerHeight + 'px';
            f.style.position = 'fixed';
            f.style.top = f.style.left = '0';
            f.style.border = 'none';
            f.style.zIndex = '9999';
        } catch (e) {}
    }
    fitParent();
    window.addEventListener('resize', fitParent);

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
                a: 0.35 + Math.random() * 0.65,
                phase: Math.random() * Math.PI * 2,
                speed: 0.6 + Math.random() * 1.6
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
    let debrisParts = [];
    let vabRocket = [];
    let currentSelectedPart = "pod";

    // Camera Panning
    let vabPanX = 0;
    let vabPanY = 0;
    let isPanning = false;
    let panStartX = 0;
    let panStartY = 0;

    // Map Animation State
    let mapTarget = null;
    let mapDist = 0;
    let mapProgress = 0;
    let mapAnimating = false;
    const planetDistances = {
        "Mercury": 91.7, "Venus": 41.4, "Earth": 0, "Mars": 78.3,
        "Jupiter": 628, "Saturn": 1270, "Uranus": 2720, "Neptune": 4350
    };

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
        legs:         { w: 24, h: 20, m: 100,  f: 0,    t: 0 },
        gyroscope:    { w: 16, h: 10, m: 200,  f: 0,    t: 0,    gyro: true },
        heat_shield:  { w: 30, h: 10, m: 500,  f: 0,    t: 0,    heatShield: true },
        booster_large:{ w: 16, h: 80, m: 1500, f: 5000, t: 1800 },
        tank_xl:      { w: 26, h: 120, m: 4000, f: 18000, t: 0 },
        engine_ion:   { w: 22, h: 20, m: 500,  f: 0,    t: 150,  ion: true, fuelRate: 0.12 },
        engine_xl:    { w: 26, h: 40, m: 3500, f: 0,    t: 6000, fuelRate: 1.0 }
    };

    const partLabels = {
        pod: "Pod", chute: "Chute", nose: "Nose",
        tank_small: "Tank S", tank_med: "Tank M", tank_large: "Tank L",
        engine_small: "Engine S", engine_med: "Engine M", engine_large: "Engine L",
        decoupler: "Decoupler", booster: "Booster", legs: "Legs",
        gyroscope: "Gyro", heat_shield: "Heat Sh",
        booster_large: "Booster L", tank_xl: "Tank XL",
        engine_ion: "Ion Eng", engine_xl: "Engine XL"
    };

    const partCosts = {
        pod: 0, chute: 0, nose: 0,
        tank_small: 0, tank_med: 0, tank_large: 0,
        engine_small: 0, engine_med: 0, engine_large: 0,
        decoupler: 0, booster: 0, legs: 0,
        gyroscope: 60, heat_shield: 80, booster_large: 100,
        tank_xl: 150, engine_ion: 200, engine_xl: 250
    };

    const baseParts = ["pod","chute","nose","tank_small","tank_med","tank_large",
                       "engine_small","engine_med","engine_large","decoupler","booster","legs"];
    const advancedParts = ["gyroscope","heat_shield","booster_large","tank_xl","engine_ion","engine_xl"];

    const MILESTONES = [1000, 5000, 10000, 25000];
    const MILESTONE_GOLD = [10, 25, 50, 100];

    const planetsDB = {
        "Mercury": { ground: "#7a6f5c", g: 3.70,  color: "#b0a89c", sky: [55, 50, 55],    atmo: 0,     radius: 12, fact: "Smallest planet · no atmosphere" },
        "Venus":   { ground: "#b88a4a", g: 8.87,  color: "#e6c88a", sky: [235, 200, 140], atmo: 14000, radius: 18, fact: "Hottest planet · thick clouds" },
        "Earth":   { ground: "#2e4a2e", g: 9.81,  color: "#4a90e2", sky: [135, 206, 235], atmo: 9000,  radius: 18, fact: "Our home · the blue marble" },
        "Mars":    { ground: "#8a2be2", g: 3.71,  color: "#ea580c", sky: [224, 150, 110], atmo: 6000,  radius: 15, fact: "The red planet · thin air" },
        "Jupiter": { ground: "#8b4513", g: 24.79, color: "#d4a373", sky: [216, 170, 130], atmo: 18000, radius: 30, fact: "Largest planet · gas giant" },
        "Saturn":  { ground: "#c4a778", g: 10.44, color: "#e0c890", sky: [200, 180, 130], atmo: 16000, radius: 26, fact: "Famous for its rings" },
        "Uranus":  { ground: "#4a8a9a", g: 8.69,  color: "#7ac8d4", sky: [150, 200, 220], atmo: 11000, radius: 20, fact: "Tilted ice giant" },
        "Neptune": { ground: "#1e3a6e", g: 11.15, color: "#4a6ec8", sky: [60, 80, 180],   atmo: 12000, radius: 20, fact: "Farthest planet · icy winds" }
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
        beenOnGround: true,
        legsDeployed: false, legsProgress: 0,
        chuteDeployed: false,
        currentPlanet: "Earth",
        cameraX: 0, cameraY: 0,
        lastTime: performance.now(),
        particles: [],
        shake: 0,
        records: {},
        landedPlanets: {},
        gold: 0,
        reachedSpace: {},
        altitudeMilestones: {},
        unlocked: {},
        heat: 0
    };

    Object.keys(planetsDB).forEach(function (k) {
        state.records[k] = 0;
        state.reachedSpace[k] = false;
        state.altitudeMilestones[k] = MILESTONES.map(function () { return false; });
    });
    baseParts.forEach(function (p) { state.unlocked[p] = true; });
    advancedParts.forEach(function (p) { state.unlocked[p] = false; });

    const throttleFill = document.getElementById('throttle-fill');
    const statusEl = document.getElementById('status-msg');
    const goldPopup = document.getElementById('gold-popup');
    const rebuildBtn = document.getElementById('btn-rebuild');
    const mapOverlay = document.getElementById('map-overlay');
    const infoCard = document.getElementById('planet-info');
    let statusTimer = null;
    let infoTimer = null;
    let goldTimer = null;

    function showStatus(text, color, seconds) {
        statusEl.innerText = text;
        statusEl.style.color = color;
        statusEl.style.display = 'block';
        if (statusTimer) { clearTimeout(statusTimer); statusTimer = null; }
        if (seconds) {
            statusTimer = setTimeout(function () { statusEl.style.display = 'none'; }, seconds * 1000);
        }
    }

    function hideGoldPopup() {
        goldPopup.classList.remove('show');
        if (goldTimer) { clearTimeout(goldTimer); goldTimer = null; }
    }

    function showGoldGain(amount) {
        if (amount <= 0) return;
        goldPopup.innerText = "+" + amount + " 🪙";
        goldPopup.classList.add('show');
        if (goldTimer) clearTimeout(goldTimer);
        goldTimer = setTimeout(function () {
            goldPopup.classList.remove('show');
        }, 900);
    }

    function addGold(amount, silent) {
        if (amount <= 0) return;
        state.gold += amount;
        updateStats();
        if (!silent) showGoldGain(amount);
    }

    function showPlanetInfo(name, seconds) {
        const p = planetsDB[name];
        document.getElementById('pi-name').innerText = name;
        document.getElementById('pi-fact').innerText = p.fact;
        document.getElementById('pi-gravity').innerText = p.g.toFixed(2) + " m/s²";
        document.getElementById('pi-atmo').innerText = p.atmo > 0 ? (p.atmo / 1000).toFixed(0) + " km" : "None";
        document.getElementById('pi-best').innerText = Math.floor(state.records[name]) + " m";
        infoCard.style.display = 'block';
        if (infoTimer) { clearTimeout(infoTimer); infoTimer = null; }
        infoTimer = setTimeout(function () { infoCard.style.display = 'none'; }, (seconds || 3.5) * 1000);
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
        const oy = H * 0.5 + (rh * sc) / 2 + vabPanY;
        return { ox: W / 2 + vabPanX, oy: oy, sc: sc };
    }

    function screenToBuild(clientX, clientY) {
        const rect = canvas.getBoundingClientRect();
        const mx = clientX - rect.left;
        const my = clientY - rect.top;
        const v = vabView();
        return { x: (mx - v.ox) / v.sc, y: (v.oy - my) / v.sc };
    }

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
        vabPanX = 0;
        vabPanY = 0;
        updateStats();
        updateScrollHints();
    };

    document.getElementById('btn-reset').onclick = function () {
        if (gameState !== "vab") return;
        rocketParts = [];
        addPart("engine_med", 0, 12);
        addPart("tank_med", 0, 54);
        addPart("pod", 0, 96);
        addPart("chute", 0, 114);
        vabPanX = 0;
        vabPanY = 0;
        computeRocketCenter();
        updateStats();
        showStatus("ROCKET RESET", "#00ffcc", 2);
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
        document.getElementById('stat-gold').innerText = state.gold;
        const gEl = document.getElementById('val-gold');
        if (gEl) gEl.innerText = state.gold;
    }

    let isDraggingPart = false;
    let draggedType = null;
    let dragGhost = null;
    let dragFromCanvas = false;
    let dragStartX = 0, dragStartY = 0;

    document.querySelectorAll('.part-btn').forEach(function (item) {
        item.addEventListener('pointerdown', function (e) {
            if (gameState !== "vab") return;
            const type = item.dataset.type;

            if (!state.unlocked[type]) {
                e.preventDefault();
                const cost = partCosts[type];
                if (state.gold >= cost) {
                    state.gold -= cost;
                    state.unlocked[type] = true;
                    item.classList.remove('locked');
                    const lbl = item.querySelector('span');
                    if (lbl) lbl.innerText = partLabels[type];
                    updateStats();
                    showStatus("UNLOCKED " + partLabels[type].toUpperCase() + "  −" + cost + "🪙", "#ffcc44", 2);
                } else {
                    showStatus("NEED " + (cost - state.gold) + " MORE 🪙", "#ff4444", 2);
                }
                return;
            }

            const startX = e.clientX, startY = e.clientY;
            let armed = false;

            function onMove(ev) {
                const dx = ev.clientX - startX;
                const dy = ev.clientY - startY;
                if (!armed && Math.abs(dy) > 8 && Math.abs(dy) > Math.abs(dx)) {
                    cleanup();
                    return;
                }
                if (!armed && Math.hypot(dx, dy) > 6) {
                    armed = true;
                    document.querySelectorAll('.part-btn').forEach(function (b) { b.classList.remove('active'); });
                    item.classList.add('active');
                    currentSelectedPart = type;
                    startDrag(type, ev.clientX, ev.clientY, false);
                }
                if (armed && dragGhost) {
                    const v = vabView();
                    const gw = P[type].w * v.sc;
                    const gh = P[type].h * v.sc;
                    dragGhost.style.left = (ev.clientX - gw / 2) + 'px';
                    dragGhost.style.top = (ev.clientY - gh / 2) + 'px';
                }
            }

            function cleanup() {
                window.removeEventListener('pointermove', onMove);
                window.removeEventListener('pointerup', onUp);
                window.removeEventListener('pointercancel', cleanup);
            }

            function onUp(ev) {
                cleanup();
                if (armed && isDraggingPart) {
                    window.dispatchEvent(new PointerEvent('pointerup', {
                        clientX: ev.clientX, clientY: ev.clientY, bubbles: true
                    }));
                }
            }

            window.addEventListener('pointermove', onMove);
            window.addEventListener('pointerup', onUp, { once: true });
            window.addEventListener('pointercancel', cleanup);
        });
    });

    canvas.addEventListener('pointerdown', function (e) {
        if (gameState !== "vab" || isDraggingPart) return;
        
        const b = screenToBuild(e.clientX, e.clientY);
        let clickedPart = false;

        for (let i = rocketParts.length - 1; i >= 0; i--) {
            const p = rocketParts[i];
            const pw = P[p.type].w, ph = P[p.type].h;
            if (Math.abs(b.x - p.x) < pw / 2 + 6 && Math.abs(b.y - p.y) < ph / 2 + 6) {
                rocketParts.splice(i, 1);
                updateStats();
                startDrag(p.type, e.clientX, e.clientY, true);
                clickedPart = true;
                break;
            }
        }

        if (!clickedPart) {
            isPanning = true;
            panStartX = e.clientX - vabPanX;
            panStartY = e.clientY - vabPanY;
        }
    });

    function startDrag(type, cx, cy, fromCanvas) {
        isDraggingPart = true;
        draggedType = type;
        dragFromCanvas = !!fromCanvas;
        dragStartX = cx;
        dragStartY = cy;

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
        if (isPanning) {
            vabPanX = e.clientX - panStartX;
            vabPanY = e.clientY - panStartY;
        }
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
        if (isPanning) {
            isPanning = false;
        }
        if (!isDraggingPart) return;

        if (dragGhost) { dragGhost.remove(); dragGhost = null; }
        isDraggingPart = false;

        const type = draggedType;
        const fromCanvas = dragFromCanvas;
        draggedType = null;
        dragFromCanvas = false;

        if (!type) return;

        const tr = trashCan.getBoundingClientRect();
        const overTrash = (e.clientX >= tr.left && e.clientX <= tr.right &&
                           e.clientY >= tr.top  && e.clientY <= tr.bottom);
        if (overTrash) { updateStats(); return; }

        const moved = Math.hypot(e.clientX - dragStartX, e.clientY - dragStartY);
        if (fromCanvas && moved < 12) { updateStats(); return; }

        if (gameState !== "vab") { updateStats(); return; }

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

    const TURN_ACCEL = 280;
    const TURN_MAX   = 150;

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
        if (y > 130) y = 130;
        const percent = 100 - (y / 130) * 100;
        state.throttle = percent / 100;
        throttleFill.style.height = percent + '%';
    }

    function bindHold(el, onDown, onUp) {
        el.addEventListener('pointerdown', function (e) {
            e.preventDefault();
            try { el.setPointerCapture(e.pointerId); } catch (err) {}
            onDown();
        });
        ['pointerup', 'pointercancel', 'lostpointercapture'].forEach(function (ev) {
            el.addEventListener(ev, function () { onUp(); });
        });
        el.addEventListener('pointerleave', function (e) {
            if (e.buttons === 0) onUp();
        });
    }

    bindHold(document.getElementById('joy-left'),
             function () { leftPressed = true; },
             function () { leftPressed = false; });
    bindHold(document.getElementById('joy-right'),
             function () { rightPressed = true; },
             function () { rightPressed = false; });

    document.getElementById('btn-legs').onclick = function () {
        state.legsDeployed = !state.legsDeployed;
        this.innerText = state.legsDeployed ? "LEGS: DOWN" : "LEGS: UP";
        if (state.legsDeployed) this.classList.add('deployed');
        else this.classList.remove('deployed');
    };

    document.getElementById('btn-stage').onclick = function () {
        if (gameState !== "flight") return;

        const sideDecouplers = rocketParts.filter(function (p) { return p.type === 'decoupler' && Math.abs(p.x) > 10; });
        let droppedParts = [];

        if (sideDecouplers.length > 0) {
            const dropX = sideDecouplers[0].x;
            droppedParts = rocketParts.filter(function (p) { return Math.abs(p.x - dropX) < 5; });
            rocketParts = rocketParts.filter(function (p) { return Math.abs(p.x - dropX) >= 5; });
        } else {
            const centerDec = rocketParts.filter(function (p) { return p.type === 'decoupler'; });
            if (centerDec.length === 0) return;
            centerDec.sort(function (a, b) { return a.y - b.y; });
            const lowest = centerDec[0];
            droppedParts = rocketParts.filter(function (p) { return p.y < lowest.y; });
            rocketParts = rocketParts.filter(function (p) { return p.y >= lowest.y; });
        }

        if (droppedParts.length > 0) {
            const rad = state.angle * Math.PI / 180;
            const cosA = Math.cos(rad);
            const sinA = Math.sin(rad);
            
            droppedParts.forEach(p => {
                const dxScreen = p.x;
                const dyScreen = state.rocketCenterY - p.y;
                const dxRot = dxScreen * cosA - dyScreen * sinA;
                const dyRot = dxScreen * sinA + dyScreen * cosA;
                const wx = state.x + dxRot;
                const wy = state.y + state.rocketCenterY - dyRot;

                debrisParts.push({
                    type: p.type,
                    x: wx, y: wy,
                    vx: state.vx + (Math.random() - 0.5) * 20,
                    vy: state.vy + (Math.random() - 0.5) * 20,
                    angle: state.angle,
                    angularVelocity: (Math.random() - 0.5) * 40,
                    life: 1.0
                });
            });
        }

        let m = 0, f = 0;
        rocketParts.forEach(function (p) { m += P[p.type].m; f += P[p.type].f; });
        state.dryMass = m;
        state.maxFuel = f;
        if (state.currentFuel > state.maxFuel) state.currentFuel = state.maxFuel;
        computeRocketCenter();
        updateStats();
    };

    function returnToVAB(message) {
        rocketParts = JSON.parse(JSON.stringify(vabRocket));
        computeRocketCenter();
        gameState = "vab";

        document.getElementById('hud').style.display = 'none';
        document.getElementById('minimap-container').style.display = 'none';
        document.getElementById('throttle-zone').style.display = 'none';
        document.getElementById('arrow-zone').style.display = 'none';
        document.getElementById('fuel-gauges').style.display = 'none';
        document.getElementById('heat-ui').style.display = 'none';
        document.getElementById('btn-legs').style.display = 'none';
        document.getElementById('btn-stage').style.display = 'none';
        document.getElementById('btn-map').style.display = 'none';
        document.getElementById('btn-exit').style.display = 'none';

        document.getElementById('vab-menu').style.display = 'flex';
        document.getElementById('top-bar').style.display = 'flex';
        document.getElementById('vab-stats').style.display = 'flex';
        document.getElementById('trash-can').style.display = 'flex';

        statusEl.style.display = 'none';
        rebuildBtn.style.display = 'none';
        mapOverlay.style.display = 'none';
        infoCard.style.display = 'none';
        hideGoldPopup();

        updateStats();
        updateScrollHints();
        if (message) showStatus(message, "#00ffcc", 2);
    }

    document.getElementById('btn-exit').onclick = function () {
        if (gameState !== "flight" && gameState !== "crashed") return;
        returnToVAB("BACK IN BUILD MODE");
    };
    rebuildBtn.onclick = function () { returnToVAB("GOLD KEPT 🪙 — BACK TO VAB"); };

    const planetsMap = [
        { name: "Mercury", color: "#b0a89c", x: 0.15, row: 0 },
        { name: "Venus",   color: "#e6c88a", x: 0.38, row: 0 },
        { name: "Earth",   color: "#4a90e2", x: 0.62, row: 0 },
        { name: "Mars",    color: "#ea580c", x: 0.85, row: 0 },
        { name: "Jupiter", color: "#d4a373", x: 0.15, row: 1 },
        { name: "Saturn",  color: "#e0c890", x: 0.38, row: 1 },
        { name: "Uranus",  color: "#7ac8d4", x: 0.62, row: 1 },
        { name: "Neptune", color: "#4a6ec8", x: 0.85, row: 1 }
    ];

    function mapRowY(row) { return row === 0 ? mapCanvas.height * 0.32 : mapCanvas.height * 0.68; }

    function drawMap() {
        mapCtx.setTransform(1, 0, 0, 1, 0, 0);
        mapCtx.fillStyle = "#000511";
        mapCtx.fillRect(0, 0, mapCanvas.width, mapCanvas.height);

        mapCtx.fillStyle = "#ffffff";
        for (let i = 0; i < 180; i++) {
            const sx = (i * 137.508) % mapCanvas.width;
            const sy = (i * 91.7) % mapCanvas.height;
            mapCtx.globalAlpha = 0.15 + ((i * 37) % 100) / 220;
            mapCtx.fillRect(sx, sy, 1.5, 1.5);
        }
        mapCtx.globalAlpha = 1;

        mapCtx.strokeStyle = "rgba(0,255,204,0.12)";
        mapCtx.lineWidth = 1;
        mapCtx.setLineDash([4, 8]);
        mapCtx.beginPath();
        mapCtx.moveTo(20, mapCanvas.height * 0.5);
        mapCtx.lineTo(mapCanvas.width - 20, mapCanvas.height * 0.5);
        mapCtx.stroke();
        mapCtx.setLineDash([]);

        mapCtx.fillStyle = "rgba(0,255,204,0.55)";
        mapCtx.font = "11px Arial";
        mapCtx.textAlign = "left";
        mapCtx.fillText("INNER PLANETS", 20, mapCanvas.height * 0.32 - 55);
        mapCtx.fillText("OUTER PLANETS", 20, mapCanvas.height * 0.68 - 55);

        mapCtx.textAlign = "center";
        planetsMap.forEach(function (p) {
            const cx = p.x * mapCanvas.width;
            const cy = mapRowY(p.row);
            const rad = planetsDB[p.name].radius;

            if (p.name === "Saturn") {
                mapCtx.strokeStyle = "rgba(230,220,180,0.75)";
                mapCtx.lineWidth = 3;
                mapCtx.beginPath();
                mapCtx.ellipse(cx, cy, rad + 14, rad * 0.35, -0.35, 0, Math.PI * 2);
                mapCtx.stroke();
            }

            const g = mapCtx.createRadialGradient(cx - rad * 0.35, cy - rad * 0.35, 2, cx, cy, rad + 2);
            g.addColorStop(0, "#ffffff");
            g.addColorStop(0.25, p.color);
            g.addColorStop(1, p.color);

            mapCtx.fillStyle = g;
            mapCtx.beginPath();
            mapCtx.arc(cx, cy, rad, 0, Math.PI * 2);
            mapCtx.fill();

            if (state.landedPlanets[p.name]) {
                mapCtx.fillStyle = "#00ffcc";
                mapCtx.font = "10px Arial";
                mapCtx.fillText("✓ LANDED", cx, cy - rad - 10);
            }

            if (p.name === state.currentPlanet) {
                mapCtx.strokeStyle = "#00ffcc";
                mapCtx.lineWidth = 3;
                mapCtx.beginPath();
                mapCtx.arc(cx, cy, rad + 8, 0, Math.PI * 2);
                mapCtx.stroke();
            }

            mapCtx.fillStyle = "#ffffff";
            mapCtx.font = "14px Arial";
            mapCtx.fillText(p.name, cx, cy + rad + 22);
        });

        // Draw Warp Animation
        if (mapTarget) {
            const curP = planetsMap.find(p => p.name === state.currentPlanet);
            const tarP = planetsMap.find(p => p.name === mapTarget);
            if (curP && tarP) {
                const sx = curP.x * mapCanvas.width;
                const sy = mapRowY(curP.row);
                const ex = tarP.x * mapCanvas.width;
                const ey = mapRowY(tarP.row);
                
                // Dashed line
                mapCtx.beginPath();
                mapCtx.setLineDash([5, 5]);
                mapCtx.strokeStyle = "rgba(255,255,255,0.5)";
                mapCtx.lineWidth = 2;
                mapCtx.moveTo(sx, sy);
                mapCtx.lineTo(ex, ey);
                mapCtx.stroke();
                mapCtx.setLineDash([]);

                // Moving arrow
                const ax = sx + (ex - sx) * mapProgress;
                const ay = sy + (ey - sy) * mapProgress;
                const angle = Math.atan2(ey - sy, ex - sx);
                
                mapCtx.save();
                mapCtx.translate(ax, ay);
                mapCtx.rotate(angle);
                mapCtx.fillStyle = "#00ffcc";
                mapCtx.beginPath();
                mapCtx.moveTo(12, 0);
                mapCtx.lineTo(-8, -6);
                mapCtx.lineTo(-8, 6);
                mapCtx.closePath();
                mapCtx.fill();
                
                // Ship glow
                mapCtx.fillStyle = "rgba(0,255,204,0.3)";
                mapCtx.beginPath();
                mapCtx.arc(0, 0, 15, 0, Math.PI*2);
                mapCtx.fill();
                
                mapCtx.restore();
            }
        }
    }

    document.getElementById('btn-map').onclick = function () {
        if (gameState !== "flight") return;
        if (mapOverlay.style.display === 'block') {
            mapOverlay.style.display = 'none';
        } else {
            mapOverlay.style.display = 'block';
            mapTarget = null;
            mapAnimating = false;
            document.getElementById('map-warp-info').style.display = 'none';
            drawMap();
        }
    };

    document.getElementById('btn-map-exit').onclick = function () {
        mapTarget = null;
        mapAnimating = false;
        mapOverlay.style.display = 'none';
        document.getElementById('map-warp-info').style.display = 'none';
    };

    mapCanvas.addEventListener('pointerdown', function (e) {
        if (mapAnimating) return;
        const rect = mapCanvas.getBoundingClientRect();
        const mx = e.clientX - rect.left;
        const my = e.clientY - rect.top;

        planetsMap.forEach(function (p) {
            const cx = p.x * mapCanvas.width;
            const cy = mapRowY(p.row);
            if (Math.hypot(mx - cx, my - cy) < 44) {
                if (p.name === state.currentPlanet) {
                    showStatus("ALREADY HERE", "#ffaa00", 1.5);
                    return;
                }
                mapTarget = p.name;
                mapDist = Math.abs(planetDistances[mapTarget] - planetDistances[state.currentPlanet]);
                mapProgress = 0;
                mapAnimating = true;
                document.getElementById('map-target-name').innerText = "Destination: " + mapTarget;
                document.getElementById('map-target-dist').innerText = "Distance: " + mapDist.toFixed(1) + "M km";
                document.getElementById('map-warp-info').style.display = 'block';
            }
        });
    });

    function travelTo(name) {
        state.currentPlanet = name;

        state.x = 0;
        state.y = 500; // High drop
        state.vx = 0;
        state.vy = -100; // Fast drop
        state.angle = 0;
        state.angularVelocity = 0;
        state.throttle = 0;
        state.chuteDeployed = false;

        state.hasLiftedOff = true;
        state.onGround = false;
        state.beenOnGround = false;
        state.heat = 0;

        state.legsDeployed = false;
        state.legsProgress = 0;
        state.cameraX = 0;
        state.cameraY = 500;
        state.particles = [];
        state.shake = 0;
        debrisParts = [];

        state.currentFuel = state.maxFuel;
        throttleFill.style.height = '0%';
        computeRocketCenter();

        const legsBtn = document.getElementById('btn-legs');
        legsBtn.innerText = "Legs";
        legsBtn.classList.remove('deployed');

        if (gameState === "crashed") {
            gameState = "flight";
            rebuildBtn.style.display = 'none';
            statusEl.style.display = 'none';
        } else {
            gameState = "flight";
        }

        hideGoldPopup();

        showPlanetInfo(name, 3.5);
        showStatus("ARRIVING AT " + name.toUpperCase() + " — DEPLOY CHUTES!", "#00ffcc", 3);
    }

    document.getElementById('btn-launch').onclick = function (e) {
        e.stopPropagation();
        if (gameState !== "vab") return;

        if (rocketParts.length === 0) {
            showStatus("BUILD A ROCKET FIRST", "#ff4444", 2);
            return;
        }

        vabRocket = JSON.parse(JSON.stringify(rocketParts));

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
        state.beenOnGround = true;
        state.cameraX = 0; state.cameraY = 0;
        state.shake = 0;
        state.particles = [];
        state.heat = 0;
        debrisParts = [];

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
        document.getElementById('minimap-container').style.display = 'block';
        document.getElementById('throttle-zone').style.display = 'block';
        document.getElementById('arrow-zone').style.display = 'flex';
        document.getElementById('fuel-gauges').style.display = 'flex';
        document.getElementById('heat-ui').style.display = 'block';
        document.getElementById('btn-legs').style.display = 'block';
        document.getElementById('btn-stage').style.display = 'block';
        document.getElementById('btn-map').style.display = 'block';
        document.getElementById('btn-exit').style.display = 'block';

        throttleFill.style.height = '0%';
        statusEl.style.display = 'none';
        rebuildBtn.style.display = 'none';
        mapOverlay.style.display = 'none';
        hideGoldPopup();

        document.getElementById('btn-legs').innerText = "Legs";
        document.getElementById('btn-legs').classList.remove('deployed');

        showPlanetInfo("Earth", 3.5);
        updateStats();
        updateHUD();
    };

    function updateParticles(dt) {
        for (let i = state.particles.length - 1; i >= 0; i--) {
            const p = state.particles[i];
            p.x += p.vx * dt;
            p.y += p.vy * dt;
            p.vy -= 45 * dt;
            p.vx *= Math.pow(0.45, dt);
            p.vy *= Math.pow(0.55, dt);
            p.life -= dt * 1.25;
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

    function updateDebris(dt) {
        for (let i = debrisParts.length - 1; i >= 0; i--) {
            const d = debrisParts[i];
            d.vy -= planetsDB[state.currentPlanet].g * dt;
            d.x += d.vx * dt;
            d.y += d.vy * dt;
            d.angle += d.angularVelocity * dt;
            
            if (d.y < 0) {
                d.y = 0;
                d.vy = -d.vy * 0.3;
                d.vx *= 0.8;
                d.angularVelocity *= 0.5;
                if (Math.abs(d.vy) < 2) { d.vy = 0; d.vx = 0; d.angularVelocity = 0; }
            }

            if (Math.abs(d.x - state.cameraX) > W * 2 || d.y < -200) {
                debrisParts.splice(i, 1);
            }
        }
    }

    function updatePhysics(dt) {
        if (gameState === "crashed") {
            updateParticles(dt);
            updateDebris(dt);
            state.shake = Math.max(0, state.shake - 50 * dt);
            state.cameraX += (state.x - state.cameraX) * Math.min(1, 8 * dt);
            state.cameraY += (state.y - state.cameraY) * Math.min(1, 8 * dt);
            return;
        }
        if (gameState !== "flight") return;

        const hasGyro = rocketParts.some(function (p) { return p.type === 'gyroscope'; });
        const turnBoost = hasGyro ? 1.9 : 1.0;

        if (leftPressed) state.angularVelocity -= TURN_ACCEL * turnBoost * dt;
        if (rightPressed) state.angularVelocity += TURN_ACCEL * turnBoost * dt;
        if (!leftPressed && !rightPressed) {
            state.angularVelocity *= Math.pow(hasGyro ? 0.05 : 0.12, dt);
        }
        const maxTurn = TURN_MAX * turnBoost;
        state.angularVelocity = Math.max(-maxTurn, Math.min(maxTurn, state.angularVelocity));
        state.angle += state.angularVelocity * dt;

        let thrust = 0;
        let fuelRate = null;
        let hasHeatShield = false;

        rocketParts.forEach(function (p) {
            thrust += P[p.type].t;
            if (p.type === 'heat_shield') hasHeatShield = true;
            if (p.type.indexOf('engine') !== -1) {
                const r = (P[p.type].fuelRate !== undefined) ? P[p.type].fuelRate : 1.0;
                fuelRate = fuelRate === null ? r : Math.max(fuelRate, r);
            }
        });
        if (fuelRate === null) fuelRate = 1.0;

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

            const fuelBurn = 50 * state.throttle * fuelRate * dt;
            state.currentFuel -= fuelBurn;
            if (state.currentFuel <= 0) {
                state.currentFuel = 0;
                state.throttle = 0;
                throttleFill.style.height = '0%';
                showStatus("OUT OF FUEL", "#ffaa00", 2);
            }

            const cosA = Math.cos(rad);
            const sinA = Math.sin(rad);

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

                const isIon = eng.type === 'engine_ion';
                const exV = (isIon ? 180 : 240) + 140 * state.throttle;

                for (let i = 0; i < 4; i++) {
                    const spread = (Math.random() - 0.5) * 0.55;
                    const ca = Math.cos(rad + spread);
                    const sa = Math.sin(rad + spread);

                    let col = "255,150,0";
                    if (isIon) {
                        col = "80,200,255";
                    } else {
                        const r = Math.random();
                        if (r > 0.66) col = "255,240,150";
                        else if (r > 0.33) col = "255,170,40";
                        else col = "255,90,10";
                    }

                    state.particles.push({
                        x: wx + (Math.random() - 0.5) * hw * 0.6,
                        y: wy + (Math.random() - 0.5) * 4,
                        vx: -sa * exV,
                        vy: -ca * exV,
                        life: 0.9,
                        size: Math.random() * 10 + 6,
                        color: col
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
        
        // Legs add aerodynamic drag
        if (state.legsDeployed && state.y < planetsDB[state.currentPlanet].atmo) {
            if (state.vy < -2) state.vy += 3 * dt;
            state.vx *= Math.pow(0.96, dt);
        }

        state.x += state.vx * dt;
        state.y += state.vy * dt;

        const isInAtmo = state.y < planetsDB[state.currentPlanet].atmo;
        const speed = Math.hypot(state.vx, state.vy);
        if (isInAtmo && speed > 500) {
            state.heat = Math.min(1137, (speed - 500) * 2); 
            if (Math.random() < (state.heat/1137)) {
                state.particles.push({
                    x: state.x + (Math.random() - 0.5) * 20,
                    y: state.y + (Math.random() - 0.5) * 40,
                    vx: -state.vx * 0.2 + (Math.random() - 0.5) * 50,
                    vy: -state.vy * 0.2 + (Math.random() - 0.5) * 50,
                    life: 0.5 + Math.random() * 0.5,
                    size: Math.random() * 15 + 5,
                    color: "255,150,50"
                });
            }
        } else {
            state.heat = Math.max(0, state.heat - dt * 100);
        }

        if (state.y <= 0) {
            state.y = 0;
            state.beenOnGround = true;

            if (!state.onGround) {
                state.onGround = true;

                const impact = Math.abs(state.vy);
                const safeSpeed = state.chuteDeployed ? 999 : (state.legsDeployed ? 15 : 8);

                if (state.hasLiftedOff && impact > safeSpeed && !hasHeatShield) {
                    state.vy = 0;
                    state.vx = 0;
                    crash();
                } else if (state.hasLiftedOff && impact > safeSpeed && hasHeatShield && impact > 30) {
                    state.vy = 0;
                    state.vx = 0;
                    crash();
                } else {
                    state.vy = 0;
                    state.vx = 0;
                    state.throttle = 0;
                    throttleFill.style.height = '0%';
                    if (state.hasLiftedOff) {
                        let bonus = "";
                        if (!state.landedPlanets[state.currentPlanet]) {
                            state.landedPlanets[state.currentPlanet] = true;
                            addGold(25);
                            bonus = "  +25🪙";
                        }
                        showStatus("🏆 LANDED SAFELY" + bonus, "#00ffcc", 3);
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

        if (state.y > state.records[state.currentPlanet]) {
            state.records[state.currentPlanet] = state.y;
        }

        const pName = state.currentPlanet;
        let pendingGold = 0;
        for (let i = 0; i < MILESTONES.length; i++) {
            if (state.y >= MILESTONES[i] && !state.altitudeMilestones[pName][i]) {
                state.altitudeMilestones[pName][i] = true;
                pendingGold += MILESTONE_GOLD[i];
            }
        }
        if (pendingGold > 0) {
            addGold(pendingGold);
            showStatus("🏔 MILESTONE  +" + pendingGold + "🪙", "#ffcc44", 2.5);
        }

        if (!state.reachedSpace[state.currentPlanet] && state.beenOnGround) {
            const planet = planetsDB[state.currentPlanet];
            const isSpace = planet.atmo === 0 ? state.y > 1000 : state.y > planet.atmo;
            if (isSpace && state.hasLiftedOff) {
                state.reachedSpace[state.currentPlanet] = true;
                addGold(50);
                showStatus("★ REACHED SPACE  +50🪙", "#00ffcc", 3);
            }
        }

        if (state.legsDeployed && state.legsProgress < 1) state.legsProgress = Math.min(1, state.legsProgress + 2 * dt);
        if (!state.legsDeployed && state.legsProgress > 0) state.legsProgress = Math.max(0, state.legsProgress - 2 * dt);

        updateParticles(dt);
        updateDebris(dt);
        state.shake = Math.max(0, state.shake - 50 * dt);
    }

    function updateHUD() {
        const alt = state.y;
        const vel = Math.hypot(state.vx, state.vy);
        
        let altStr = alt > 1000 ? (alt/1000).toFixed(1) + "km" : alt.toFixed(1) + "m";
        let velStr = vel > 1000 ? (vel/1000).toFixed(1) + "km/s" : vel.toFixed(1) + "m/s";
        
        document.getElementById('val-alt').innerText = altStr;
        document.getElementById('val-vel').innerText = velStr;
        document.getElementById('val-gold').innerText = state.gold;

        const fp = state.maxFuel > 0 ? (state.currentFuel / state.maxFuel) * 100 : 0;
        document.getElementById('fuel-bar-1').style.width = fp + '%';

        if (state.heat > 0) {
            document.getElementById('heat-ui').style.display = 'block';
            document.getElementById('fuel-gauges').style.display = 'none';
            document.getElementById('val-heat').innerText = Math.round(state.heat);
        } else {
            document.getElementById('heat-ui').style.display = 'none';
            document.getElementById('fuel-gauges').style.display = 'flex';
        }

        const planet = planetsDB[state.currentPlanet];
        const spaceEl = document.getElementById('hud-space');
        const isSpace = planet.atmo === 0 ? state.y > 1000 : state.y > planet.atmo;
        if (isSpace) {
            spaceEl.style.display = 'block';
        } else {
            spaceEl.style.display = 'none';
        }
    }

    function drawPart(p, py) {
        const w = P[p.type].w, h = P[p.type].h;
        ctx.save();
        ctx.translate(p.x, py);

        function drawMetalTank(width, height, isXL) {
            const grad = ctx.createLinearGradient(-width / 2, 0, width / 2, 0);
            if (isXL) {
                grad.addColorStop(0, "#9988bb"); grad.addColorStop(0.2, "#d8c8ee"); 
                grad.addColorStop(0.5, "#f8f0ff"); grad.addColorStop(0.8, "#b0a0cc"); grad.addColorStop(1, "#776699");
            } else {
                grad.addColorStop(0, "#666666"); grad.addColorStop(0.2, "#dddddd"); 
                grad.addColorStop(0.5, "#ffffff"); grad.addColorStop(0.8, "#bbbbbb"); grad.addColorStop(1, "#555555");
            }
            ctx.fillStyle = grad;
            ctx.fillRect(-width / 2, -height / 2, width, height);
            
            ctx.fillStyle = "rgba(0,0,0,0.4)";
            ctx.fillRect(-width / 2, -height / 2, width, 2);
            ctx.fillRect(-width / 2, height / 2 - 2, width, 2);
            
            ctx.fillStyle = "rgba(0,0,0,0.15)";
            ctx.fillRect(-width / 2, 0, width, 1);
        }

        function drawMetalCone(width, height) {
            const grad = ctx.createLinearGradient(-width / 2, 0, width / 2, 0);
            grad.addColorStop(0, "#444"); grad.addColorStop(0.5, "#fff"); grad.addColorStop(1, "#333");
            ctx.fillStyle = grad;
            ctx.beginPath();
            ctx.moveTo(-width / 2, height / 2);
            ctx.quadraticCurveTo(-width / 4, -height / 4, 0, -height / 2);
            ctx.quadraticCurveTo(width / 4, -height / 4, width / 2, height / 2);
            ctx.fill();
        }

        if (p.type === "pod") {
            // Realistic Pod (No Window)
            const bodyGrad = ctx.createLinearGradient(-w/2, 0, w/2, 0);
            bodyGrad.addColorStop(0, "#111");
            bodyGrad.addColorStop(0.3, "#555");
            bodyGrad.addColorStop(0.7, "#333");
            bodyGrad.addColorStop(1, "#050505");
            ctx.fillStyle = bodyGrad;

            ctx.beginPath();
            ctx.moveTo(-w/3, -h/2 + 4);
            ctx.bezierCurveTo(-w/1.8, -h/4, -w/1.8, h/4, -w/2.2, h/2 - 2);
            ctx.lineTo(w/2.2, h/2 - 2);
            ctx.bezierCurveTo(w/1.8, h/4, w/1.8, -h/4, w/3, -h/2 + 4);
            ctx.closePath();
            ctx.fill();

            ctx.fillStyle = "#ccc";
            ctx.beginPath();
            ctx.moveTo(-w/3, -h/2 + 4);
            ctx.lineTo(w/3, -h/2 + 4);
            ctx.lineTo(w/3 + 1, -h/2 + 8);
            ctx.lineTo(-w/3 - 1, -h/2 + 8);
            ctx.fill();

            ctx.strokeStyle = "#777";
            ctx.lineWidth = 1;
            for(let i=-3; i<=3; i++) {
                if(i === 0) continue;
                ctx.beginPath();
                ctx.moveTo(i * (w/9), -h/2 + 4);
                ctx.lineTo(i * (w/9), -h/2 + 8);
                ctx.stroke();
            }

            ctx.fillStyle = "#999";
            ctx.beginPath();
            ctx.ellipse(0, -h/2 + 2, w/5, 2, 0, 0, Math.PI*2);
            ctx.fill();

            ctx.fillStyle = "#777";
            ctx.beginPath();
            ctx.moveTo(-w/2.2, h/2 - 2);
            ctx.lineTo(w/2.2, h/2 - 2);
            ctx.lineTo(w/2, h/2 + 1);
            ctx.lineTo(-w/2, h/2 + 1);
            ctx.closePath();
            ctx.fill();

            ctx.fillStyle = "#222";
            ctx.beginPath();
            ctx.moveTo(-w/4, h/2 + 1);
            ctx.lineTo(w/4, h/2 + 1);
            ctx.lineTo(w/3, h/2 + 5);
            ctx.lineTo(-w/3, h/2 + 5);
            ctx.closePath();
            ctx.fill();

        } else if (p.type === "chute") {
            if (!state.chuteDeployed) {
                drawMetalTank(w, h, false);
                ctx.fillStyle = "#555";
                ctx.fillRect(-w/2, -h/2, w, 3);
            }

        } else if (p.type === "nose") {
            drawMetalCone(w, h);

        } else if (p.type.indexOf("tank") !== -1) {
            drawMetalTank(w, h, p.type === "tank_xl");

        } else if (p.type.indexOf("engine") !== -1) {
            const isIon = p.type === "engine_ion";
            
            ctx.fillStyle = "#444";
            ctx.fillRect(-w/3, -h/2, w/1.5, h/4);

            const bellGrad = ctx.createLinearGradient(-w/2, 0, w/2, 0);
            if (isIon) {
                bellGrad.addColorStop(0, "#1a2a4a"); bellGrad.addColorStop(0.3, "#4a6a9a"); bellGrad.addColorStop(0.6, "#1a2a4a"); bellGrad.addColorStop(1, "#0a1a2a");
            } else {
                bellGrad.addColorStop(0, "#111"); bellGrad.addColorStop(0.3, "#888"); bellGrad.addColorStop(0.6, "#333"); bellGrad.addColorStop(1, "#0a0a0a");
            }
            
            ctx.fillStyle = bellGrad;
            ctx.beginPath();
            ctx.moveTo(-w/3, -h/4);
            ctx.lineTo(w/3, -h/4);
            ctx.bezierCurveTo(w/2.5, h/4, w/1.5, h/2, w/1.2, h/2);
            ctx.lineTo(-w/1.2, h/2);
            ctx.bezierCurveTo(-w/1.5, h/2, -w/2.5, h/4, -w/3, -h/4);
            ctx.fill();

            ctx.fillStyle = "#222";
            ctx.beginPath();
            ctx.ellipse(0, h/2, w/1.2, 2, 0, 0, Math.PI*2);
            ctx.fill();

            if (state.throttle > 0 && state.currentFuel > 0 && (gameState === "flight" || gameState === "crashed")) {
                const th = state.throttle;
                const flick = 0.9 + Math.random() * 0.2;
                const flameLen = (60 + 120 * th) * flick;
                const nozzleY = h / 2;
                const nozzleW = w / 1.2;

                const outerGrad = ctx.createLinearGradient(0, nozzleY, 0, nozzleY + flameLen);
                if (isIon) {
                    outerGrad.addColorStop(0, "rgba(80, 200, 255, 0.8)");
                    outerGrad.addColorStop(1, "rgba(50, 100, 255, 0)");
                } else {
                    outerGrad.addColorStop(0, "rgba(255, 100, 0, 0.8)");
                    outerGrad.addColorStop(1, "rgba(255, 0, 0, 0)");
                }
                ctx.fillStyle = outerGrad;
                ctx.beginPath();
                ctx.moveTo(-nozzleW / 2, nozzleY);
                ctx.lineTo(nozzleW / 2, nozzleY);
                ctx.quadraticCurveTo(nozzleW / 2, nozzleY + flameLen * 0.5, 0, nozzleY + flameLen);
                ctx.quadraticCurveTo(-nozzleW / 2, nozzleY + flameLen * 0.5, -nozzleW / 2, nozzleY);
                ctx.fill();

                const innerGrad = ctx.createLinearGradient(0, nozzleY, 0, nozzleY + flameLen * 0.6);
                if (isIon) {
                    innerGrad.addColorStop(0, "rgba(255, 255, 255, 1)");
                    innerGrad.addColorStop(1, "rgba(80, 200, 255, 0)");
                } else {
                    innerGrad.addColorStop(0, "rgba(255, 255, 200, 1)");
                    innerGrad.addColorStop(1, "rgba(255, 200, 0, 0)");
                }
                ctx.fillStyle = innerGrad;
                ctx.beginPath();
                ctx.moveTo(-nozzleW / 4, nozzleY);
                ctx.lineTo(nozzleW / 4, nozzleY);
                ctx.quadraticCurveTo(nozzleW / 4, nozzleY + flameLen * 0.3, 0, nozzleY + flameLen * 0.6);
                ctx.quadraticCurveTo(-nozzleW / 4, nozzleY + flameLen * 0.3, -nozzleW / 4, nozzleY);
                ctx.fill();

                const glow = ctx.createRadialGradient(0, nozzleY, 2, 0, nozzleY, flameLen * 0.8);
                glow.addColorStop(0, isIon ? "rgba(80, 200, 255, 0.4)" : "rgba(255, 150, 50, 0.4)");
                glow.addColorStop(1, "rgba(0, 0, 0, 0)");
                ctx.fillStyle = glow;
                ctx.beginPath();
                ctx.arc(0, nozzleY, flameLen * 0.8, 0, Math.PI * 2);
                ctx.fill();
            }

        } else if (p.type === "decoupler") {
            const grad = ctx.createLinearGradient(-w / 2, 0, w / 2, 0);
            grad.addColorStop(0, "#222"); grad.addColorStop(0.5, "#666"); grad.addColorStop(1, "#222");
            ctx.fillStyle = grad;
            ctx.fillRect(-w / 2, -h / 2, w, h);
            ctx.fillStyle = "#ffcc44";
            ctx.fillRect(-w/4, -h/2, 2, h);
            ctx.fillRect(w/4, -h/2, 2, h);

        } else if (p.type === "booster" || p.type === "booster_large") {
            drawMetalTank(w, h, false);
            drawMetalCone(w, h * 0.2);
            
        } else if (p.type === "legs") {
            ctx.fillStyle = "#444";
            ctx.fillRect(-w / 2, -h / 2, w, h);

        } else if (p.type === "gyroscope") {
            const grad = ctx.createRadialGradient(0, 0, 2, 0, 0, w/2);
            grad.addColorStop(0, "#ffdd88"); grad.addColorStop(1, "#cc8800");
            ctx.fillStyle = grad;
            ctx.beginPath();
            ctx.arc(0, 0, w / 2, 0, Math.PI * 2);
            ctx.fill();

        } else if (p.type === "heat_shield") {
            const grad = ctx.createLinearGradient(-w / 2, 0, w / 2, 0);
            grad.addColorStop(0, "#331111"); grad.addColorStop(0.5, "#884444"); grad.addColorStop(1, "#331111");
            ctx.fillStyle = grad;
            ctx.beginPath();
            ctx.moveTo(-w / 2, -h / 2);
            ctx.lineTo(w / 2, -h / 2);
            ctx.lineTo(w / 2.8, h / 2);
            ctx.lineTo(-w / 2.8, h / 2);
            ctx.fill();
        }

        ctx.restore();
    }

    function drawVAB() {
        ctx.setTransform(1, 0, 0, 1, 0, 0);

        // Lighter SFS Background
        ctx.fillStyle = "#345";
        ctx.fillRect(0, 0, W, H);

        const v = vabView();
        ctx.save();
        ctx.translate(v.ox, v.oy);
        ctx.scale(v.sc, v.sc);

        ctx.strokeStyle = "rgba(255, 255, 255, 0.15)";
        ctx.lineWidth = 1;
        ctx.beginPath();
        for (let i = -100; i <= 100; i++) {
            ctx.moveTo(i * GRID, -5000);
            ctx.lineTo(i * GRID, 100);
            ctx.moveTo(-1000, i * GRID);
            ctx.lineTo(1000, i * GRID);
        }
        ctx.stroke();

        ctx.fillStyle = "#4a6fa5"; // SFS building floor
        ctx.fillRect(-440, 0, 880, 10);

        rocketParts.forEach(function (p) { drawPart(p, -p.y); });
        ctx.restore();
    }

    // ... (Rest of flight code remains the same)
