import ast
from pathlib import Path


APP_FILE = Path("app.py")
OUTPUT_FILE = Path("game.html")


def get_original_game_html():
    if not APP_FILE.exists():
        raise FileNotFoundError(
            "Could not find app.py. Put make_game.py "
            "in the same folder as your original app.py."
        )

    source = APP_FILE.read_text(encoding="utf-8")
    tree = ast.parse(source)

    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "game_html":
                    value = ast.literal_eval(node.value)

                    if not isinstance(value, str):
                        raise ValueError("game_html is not a string.")

                    return value

    raise ValueError(
        "Could not find the original game_html variable in app.py."
    )


NEW_CSS = r"""
/* =====================================
   SPACE EXPLORER: CINEMATIC VISUAL THEME
   ===================================== */

:root {
    --accent: #83ffed;
    --accent-glow: rgba(78, 239, 220, 0.35);
    --panel-bg: rgba(5, 19, 32, 0.88);
    --panel-border: rgba(145, 210, 235, 0.30);
    --gold: #ffd889;
}

body {
    color: #effaff;
    font-family: Inter, "Segoe UI", Arial, sans-serif;
}

/* Start screen */

#start-screen {
    background:
        radial-gradient(
            ellipse at 50% 90%,
            rgba(30, 115, 150, 0.35),
            transparent 50%
        ),
        radial-gradient(
            ellipse at 18% 10%,
            rgba(85, 78, 170, 0.24),
            transparent 42%
        ),
        linear-gradient(160deg, #020712, #0b1c2e 60%, #030812);
}

#start-screen::before {
    content: "";
    position: absolute;
    inset: 0;
    pointer-events: none;
    opacity: 0.7;
    background-image:
        radial-gradient(1px 1px at 14% 18%, white 98%, transparent),
        radial-gradient(1px 1px at 76% 12%, white 98%, transparent),
        radial-gradient(2px 2px at 84% 42%, #bdeaff 98%, transparent),
        radial-gradient(1px 1px at 26% 65%, white 98%, transparent),
        radial-gradient(1px 1px at 65% 72%, white 98%, transparent),
        radial-gradient(2px 2px at 42% 27%, #8bcfff 98%, transparent),
        radial-gradient(1px 1px at 91% 77%, white 98%, transparent);
}

.title {
    position: relative;
    font-size: clamp(34px, 7vw, 76px);
    line-height: 1;
    letter-spacing: 0.08em;
    color: #f3fbff;
    text-shadow:
        0 0 35px rgba(75, 199, 255, 0.40),
        0 5px 25px rgba(0, 0, 0, 0.8);
    animation: intro-arrive 0.9s ease-out both;
}

.subtitle {
    position: relative;
    max-width: 460px;
    color: #b2d0e1;
    font-size: 13px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    animation: intro-arrive 0.9s 0.12s ease-out both;
}

.gold-guide {
    position: relative;
    color: #f4d392;
    background: rgba(8, 23, 37, 0.76);
    border: 1px solid rgba(255, 206, 112, 0.28);
    border-radius: 14px;
    padding: 15px 22px;
    backdrop-filter: blur(12px);
    box-shadow: 0 15px 45px rgba(0, 0, 0, 0.32);
    animation: intro-arrive 0.9s 0.2s ease-out both;
}

#btn-start {
    position: relative;
    background: linear-gradient(135deg, #c0fff4, #39dfd0);
    color: #031b22;
    border: 1px solid #cbfff8;
    border-radius: 10px;
    padding: 16px 38px;
    font-size: 15px;
    letter-spacing: 0.12em;
    box-shadow:
        0 0 30px rgba(48, 230, 215, 0.32),
        0 12px 35px rgba(0, 0, 0, 0.35);
    transition: transform 0.2s, box-shadow 0.2s;
    animation: intro-arrive 0.9s 0.3s ease-out both;
}

#btn-start:hover {
    transform: translateY(-3px);
    box-shadow:
        0 0 45px rgba(48, 230, 215, 0.5),
        0 15px 38px rgba(0, 0, 0, 0.4);
}

/* Panels and buttons */

#vab-menu,
#vab-stats,
#planet-info,
#map-warp-info {
    background: var(--panel-bg);
    border: 1px solid var(--panel-border);
    border-radius: 14px;
    backdrop-filter: blur(14px);
    box-shadow:
        0 14px 35px rgba(0, 0, 0, 0.4),
        inset 0 1px 0 rgba(255, 255, 255, 0.06);
}

.part-btn {
    background: linear-gradient(145deg, #203d51, #102536);
    border: 1px solid rgba(136, 197, 220, 0.26);
    border-radius: 7px;
    transition: background 0.15s, border-color 0.15s;
}

.part-btn:hover {
    background: #28516a;
    border-color: #77d9ec;
}

.part-btn.active {
    border-color: var(--accent);
    background: linear-gradient(145deg, #17545b, #10373f);
    box-shadow: 0 0 14px rgba(65, 232, 215, 0.22);
}

.part-btn.locked {
    border-color: rgba(255, 207, 116, 0.48);
}

.part-section {
    border-top-color: rgba(255, 204, 100, 0.45);
}

.top-btn,
#btn-map,
#btn-exit,
#btn-map-exit,
#btn-rebuild,
#btn-stage,
#btn-legs,
#btn-chute,
.arrow-btn {
    background: rgba(13, 34, 51, 0.88);
    border: 1px solid rgba(135, 206, 235, 0.35);
    border-radius: 9px;
    color: #effaff;
    box-shadow: 0 6px 22px rgba(0, 0, 0, 0.32);
    backdrop-filter: blur(10px);
}

.top-btn:hover,
#btn-map:hover,
#btn-exit:hover,
#btn-map-exit:hover,
#btn-rebuild:hover {
    background: rgba(33, 79, 101, 0.95);
    border-color: var(--accent);
}

#btn-launch {
    color: #071c24;
    background: linear-gradient(135deg, #b4fff3, #31d8cc);
    border-color: #b1fff5;
}

#trash-can {
    background: rgba(118, 28, 39, 0.5);
    border-color: #ff7181;
}

/* Flight HUD */

#hud {
    padding: 12px 15px;
    border: 1px solid var(--panel-border);
    border-radius: 12px;
    background: rgba(6, 20, 34, 0.78);
    backdrop-filter: blur(10px);
    box-shadow: 0 10px 28px rgba(0, 0, 0, 0.3);
}

#hud .val,
.stat-val {
    color: #93fff0;
}

#hud-space {
    color: var(--accent);
    letter-spacing: 0.05em;
}

#minimap-container {
    top: 175px;
    border-color: rgba(118, 223, 224, 0.55);
}

.fuel-bar-bg {
    background: rgba(3, 15, 25, 0.8);
    border: 1px solid rgba(160, 215, 235, 0.45);
    border-radius: 8px;
    overflow: hidden;
}

.fuel-bar-fill,
#throttle-fill {
    background: linear-gradient(90deg, #3bd9cd, #aefff3);
}

#throttle-zone {
    background: rgba(6, 24, 38, 0.8);
    border-color: rgba(155, 226, 238, 0.55);
}

/* Animated notifications */

#status-msg {
    top: 27%;
    min-width: min(280px, 76vw);
    padding: 15px 22px;
    box-sizing: border-box;
    border: 1px solid currentColor;
    border-radius: 12px;
    background: rgba(4, 16, 28, 0.88);
    backdrop-filter: blur(12px);
    font-size: clamp(16px, 3.5vw, 25px);
    letter-spacing: 0.04em;
    line-height: 1.3;
    text-shadow: 0 0 18px currentColor;
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.45);
}

#status-msg.status-enter {
    animation: status-enter 0.5s cubic-bezier(.18, .8, .2, 1) both;
}

#status-msg.status-exit {
    animation: status-exit 0.4s ease-in both;
}

#gold-popup {
    top: 40%;
    padding: 8px 16px;
    border-radius: 12px;
    font-size: clamp(28px, 5vw, 42px);
    background: rgba(30, 22, 8, 0.65);
    border: 1px solid rgba(255, 212, 125, 0.4);
    text-shadow: 0 0 20px rgba(255, 204, 68, 0.8);
    opacity: 0;
    transition: none;
}

#gold-popup.show {
    animation: gold-float 1.4s ease-out both;
}

/* Solar-system map */

#map-overlay {
    background: #030916;
}

#map-title {
    letter-spacing: 0.08em;
    font-size: clamp(16px, 3vw, 24px);
}

#map-hint {
    color: #b5d3e3;
    letter-spacing: 0.03em;
}

@keyframes intro-arrive {
    from {
        opacity: 0;
        transform: translateY(18px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes status-enter {
    from {
        opacity: 0;
        transform: translate(-50%, -35%) scale(0.94);
    }
    to {
        opacity: 1;
        transform: translate(-50%, -50%) scale(1);
    }
}

@keyframes status-exit {
    from {
        opacity: 1;
        transform: translate(-50%, -50%);
    }
    to {
        opacity: 0;
        transform: translate(-50%, -65%);
    }
}

@keyframes gold-float {
    0% {
        opacity: 0;
        transform: translate(-50%, -20%) scale(0.85);
    }
    20% {
        opacity: 1;
        transform: translate(-50%, -50%) scale(1.05);
    }
    70% {
        opacity: 1;
        transform: translate(-50%, -80%) scale(1);
    }
    100% {
        opacity: 0;
        transform: translate(-50%, -115%) scale(0.95);
    }
}

@media (max-width: 600px) {
    #vab-stats {
        top: 65px;
        width: 135px;
        padding: 8px;
    }

    #vab-stats .stat-hint {
        display: none;
    }

    #top-bar {
        gap: 6px;
    }

    .top-btn {
        padding: 9px 12px;
        font-size: 12px;
    }

    #hud {
        top: 10px;
        right: 10px;
        padding: 8px 10px;
        font-size: 11px;
    }

    #hud .val {
        font-size: 14px;
    }

    #minimap-container {
        top: 145px;
        right: 10px;
    }

    #planet-info {
        min-width: 200px;
        max-width: 75vw;
    }

    #map-title {
        left: 95px;
        top: 25px;
    }
}

@media (prefers-reduced-motion: reduce) {
    .title,
    .subtitle,
    .gold-guide,
    #btn-start,
    #status-msg.status-enter,
    #status-msg.status-exit,
    #gold-popup.show {
        animation-duration: 0.01ms;
        animation-delay: 0ms;
    }
}
"""


NEW_JAVASCRIPT = r"""
/* =====================================
   CINEMATIC VISUAL UPGRADES
   Added after the original game logic.
   ===================================== */

// Smooth status messages. A zero duration keeps the message
// visible until the game hides it, as with a crash.
let cinematicStatusHideTimer = null;

showStatus = function (text, color, seconds) {
    if (statusTimer) clearTimeout(statusTimer);

    if (cinematicStatusHideTimer) {
        clearTimeout(cinematicStatusHideTimer);
    }

    statusEl.innerText = text;
    statusEl.style.color = color;
    statusEl.style.display = "block";

    statusEl.classList.remove("status-enter", "status-exit");
    void statusEl.offsetWidth;
    statusEl.classList.add("status-enter");

    if (seconds > 0) {
        statusTimer = setTimeout(function () {
            statusEl.classList.remove("status-enter");
            statusEl.classList.add("status-exit");

            cinematicStatusHideTimer = setTimeout(function () {
                statusEl.style.display = "none";
                statusEl.classList.remove("status-exit");
            }, 400);
        }, seconds * 1000);
    }
};

showGoldGain = function (amount) {
    if (amount <= 0) return;

    if (goldTimer) clearTimeout(goldTimer);

    goldPopup.innerText = "+" + amount + " 🪙";
    goldPopup.classList.remove("show");
    void goldPopup.offsetWidth;
    goldPopup.classList.add("show");

    goldTimer = setTimeout(function () {
        goldPopup.classList.remove("show");
    }, 1400);
};


// New build-hangar background. Rocket coordinates stay the same.
drawVAB = function () {
    ctx.setTransform(1, 0, 0, 1, 0, 0);

    const background = ctx.createLinearGradient(0, 0, 0, H);
    background.addColorStop(0, "#07111f");
    background.addColorStop(0.55, "#142d40");
    background.addColorStop(1, "#08131d");

    ctx.fillStyle = background;
    ctx.fillRect(0, 0, W, H);

    const glow = ctx.createRadialGradient(
        W / 2, H * 0.12, 0,
        W / 2, H * 0.4, H * 0.8
    );

    glow.addColorStop(0, "rgba(107, 210, 245, 0.18)");
    glow.addColorStop(0.5, "rgba(40, 100, 135, 0.08)");
    glow.addColorStop(1, "rgba(0, 0, 0, 0)");

    ctx.fillStyle = glow;
    ctx.fillRect(0, 0, W, H);

    ctx.strokeStyle = "rgba(142, 200, 225, 0.08)";
    ctx.lineWidth = 2;

    for (let x = 0; x < W; x += 120) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, H);
        ctx.stroke();
    }

    for (let y = 70; y < H; y += 120) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(W, y);
        ctx.stroke();
    }

    for (let x = 90; x < W; x += 220) {
        const light = ctx.createRadialGradient(
            x, 20, 2, x, 20, 90
        );

        light.addColorStop(0, "rgba(190, 245, 255, 0.32)");
        light.addColorStop(1, "rgba(100, 200, 255, 0)");

        ctx.fillStyle = light;
        ctx.fillRect(x - 90, 0, 180, 110);
    }

    const v = vabView();

    ctx.save();
    ctx.translate(v.ox, v.oy);
    ctx.scale(v.sc, v.sc);

    ctx.strokeStyle = "rgba(168, 222, 239, 0.11)";
    ctx.lineWidth = 1 / v.sc;
    ctx.beginPath();

    for (let i = -100; i <= 100; i++) {
        ctx.moveTo(i * GRID, -5000);
        ctx.lineTo(i * GRID, 100);
        ctx.moveTo(-1000, i * GRID);
        ctx.lineTo(1000, i * GRID);
    }

    ctx.stroke();

    ctx.setLineDash([8, 8]);
    ctx.strokeStyle = "rgba(94, 246, 223, 0.28)";
    ctx.beginPath();
    ctx.moveTo(0, -5000);
    ctx.lineTo(0, 0);
    ctx.stroke();
    ctx.setLineDash([]);

    const platform = ctx.createLinearGradient(0, 0, 0, 24);
    platform.addColorStop(0, "#527589");
    platform.addColorStop(0.25, "#2a485b");
    platform.addColorStop(1, "#10232f");

    ctx.fillStyle = platform;
    ctx.fillRect(-440, 0, 880, 24);

    ctx.fillStyle = "rgba(117, 238, 224, 0.65)";
    ctx.fillRect(-440, 0, 880, 2);

    rocketParts.forEach(function (part) {
        drawPart(part, -part.y);
    });

    ctx.restore();
};


// Add a subtle cinematic vignette to flight without changing
// rocket physics, particles, or the existing scenery.
const originalDrawFlight = drawFlight;

drawFlight = function () {
    originalDrawFlight();

    ctx.save();
    ctx.setTransform(1, 0, 0, 1, 0, 0);

    const vignette = ctx.createRadialGradient(
        W / 2, H * 0.46, Math.min(W, H) * 0.18,
        W / 2, H * 0.46, Math.max(W, H) * 0.72
    );

    vignette.addColorStop(0, "rgba(0, 0, 0, 0)");
    vignette.addColorStop(0.65, "rgba(0, 4, 12, 0.05)");
    vignette.addColorStop(1, "rgba(0, 4, 12, 0.55)");

    ctx.fillStyle = vignette;
    ctx.fillRect(0, 0, W, H);

    ctx.restore();
};


// Add a gentle outer glow to the map while keeping existing
// planet positions and click targets unchanged.
const originalDrawMap = drawMap;

drawMap = function () {
    originalDrawMap();

    mapCtx.save();
    mapCtx.setTransform(1, 0, 0, 1, 0, 0);

    const glow = mapCtx.createRadialGradient(
        W / 2, H / 2, Math.min(W, H) * 0.1,
        W / 2, H / 2, Math.max(W, H) * 0.75
    );

    glow.addColorStop(0, "rgba(5, 20, 40, 0)");
    glow.addColorStop(1, "rgba(0, 3, 14, 0.48)");

    mapCtx.fillStyle = glow;
    mapCtx.fillRect(0, 0, W, H);

    mapCtx.restore();
};
"""


def main():
    html = get_original_game_html()

    if "</style>" not in html or "</script>" not in html:
        raise ValueError(
            "Could not find the expected style or script tags."
        )

    # Insert the new styles after the existing styles.
    html = html.replace(
        "</style>",
        NEW_CSS + "\n</style>",
        1,
    )

    # Insert enhancements after the original game logic.
    script_end = html.rfind("</script>")
    html = (
        html[:script_end]
        + "\n"
        + NEW_JAVASCRIPT
        + "\n"
        + html[script_end:]
    )

    OUTPUT_FILE.write_text(html, encoding="utf-8")
    print(f"Created complete game: {OUTPUT_FILE.resolve()}")


if __name__ == "__main__":
    main()
