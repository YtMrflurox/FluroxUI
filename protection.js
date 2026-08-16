// ═══════════════════════════════════════════
// 🛡️ PROTECTIONS ANTI-DEV MODE AVION - FLURO
// ═══════════════════════════════════════════

// 1. DÉTECTEUR DEVTOOLS ULTRA AGRESSIF (fonctionne hors ligne)
(function() {
    let attempts = 0;
    let isDevToolsOpen = false;
    
    // Méthode 1: Détection par dimension d'écran
    function checkDevToolsBySize() {
        const threshold = 160;
        if (window.outerHeight - window.innerHeight > threshold || 
            window.outerWidth - window.innerWidth > threshold) {
            return true;
        }
        return false;
    }
    
    // Méthode 2: Détection par debugger timing
    function checkDevToolsByTiming() {
        const start = performance.now();
        debugger;
        const end = performance.now();
        return end - start > 100;
    }
    
    // Méthode 3: Console detection avec toString override
    let devtools = false;
    const image = new Image();
    Object.defineProperty(image, 'id', {
        get: function() {
            devtools = true;
            nukeEverything();
        }
    });
    
    // FONCTION DE DESTRUCTION TOTALE
    function nukeEverything() {
        attempts++;
        
        // Vider complètement la page
        document.documentElement.innerHTML = '';
        document.head.innerHTML = '';
        document.body.innerHTML = '';
        
        // Créer nouveau contenu hostile
        const nukeHTML = `
        <!DOCTYPE html>
        <html>
        <head>
            <title>ACCÈS REFUSÉ - FLURO</title>
            <style>
                * { margin: 0; padding: 0; }
                body {
                    background: linear-gradient(45deg, #ff0000, #000000, #ff0000);
                    background-size: 400% 400%;
                    animation: gradient 2s ease infinite;
                    color: #fff;
                    font-family: 'Courier New', monospace;
                    height: 100vh;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    overflow: hidden;
                }
                .warning {
                    text-align: center;
                    animation: shake 0.5s infinite, blink 1s infinite;
                    border: 5px solid #ffff00;
                    padding: 30px;
                    background: rgba(0,0,0,0.8);
                    border-radius: 20px;
                }
                .skull { font-size: 5em; animation: spin 2s linear infinite; }
                h1 { font-size: 3em; margin: 20px 0; }
                .attempts { color: #ffff00; font-size: 1.5em; }
                
                @keyframes gradient {
                    0% { background-position: 0% 50%; }
                    50% { background-position: 100% 50%; }
                    100% { background-position: 0% 50%; }
                }
                @keyframes shake {
                    0%, 100% { transform: translateX(0); }
                    25% { transform: translateX(-10px); }
                    75% { transform: translateX(10px); }
                }
                @keyframes blink {
                    0%, 50% { opacity: 1; }
                    51%, 100% { opacity: 0.3; }
                }
                @keyframes spin {
                    from { transform: rotate(0deg); }
                    to { transform: rotate(360deg); }
                }
            </style>
        </head>
        <body>
            <div class="warning">
                <div class="skull">💀</div>
                <h1>🚨 SYSTÈME DE SÉCURITÉ ACTIVÉ 🚨</h1>
                <p style="font-size: 1.5em;">OUTILS DE DÉVELOPPEMENT DÉTECTÉS</p>
                <p style="margin: 20px 0;">Portfolio protégé © FLURO 2024</p>
                <p class="attempts">⚡ TENTATIVE N°${attempts} ⚡</p>
                <p style="color: #ff6666; margin-top: 20px;">MODE AVION DÉTECTÉ - ACCÈS REFUSÉ</p>
                <p style="font-size: 0.9em; margin-top: 20px;">Discord: fluroxouy</p>
            </div>
            <script>
                // BLOQUER TOUT MÊME EN MODE AVION
                document.addEventListener('keydown', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    return false;
                });
                document.addEventListener('contextmenu', function(e) {
                    e.preventDefault();
                    return false;
                });
                
                // Auto-fermeture de l'onglet après 10 secondes
                setTimeout(function() {
                    window.close();
                    // Si ça marche pas, corruption totale
                    document.body.innerHTML = '<h1 style="color:red;font-size:5em;">💥 ACCÈS DÉFINITIVEMENT REFUSÉ 💥</h1>';
                }, 10000);
                
                // Boucle infinie pour bloquer la console
                setInterval(function() {
                    debugger;
                }, 100);
            </script>
        </body>
        </html>
        `;
        
        // Remplacer complètement le document
        document.open();
        document.write(nukeHTML);
        document.close();
    }
    
    // VÉRIFICATIONS CONTINUES
    setInterval(function() {
        if (checkDevToolsBySize() || checkDevToolsByTiming()) {
            if (!isDevToolsOpen) {
                isDevToolsOpen = true;
                nukeEverything();
            }
        }
    }, 100);
    
    // Console trap (fonctionne même hors ligne)
    console.log(image);
})();

// 2. BLOQUER TOUTES LES TOUCHES (même hors ligne)
document.addEventListener('keydown', function(e) {
    // Touches interdites
    const forbidden = [
        'F12', 'F11', 'F10', 'F9', 'F8', 'F7', 'F6', 'F5', 'F4', 'F3', 'F2', 'F1'
    ];
    
    // Combinaisons interdites
    if (e.key === 'F12' || 
        (e.ctrlKey && e.shiftKey && e.key === 'I') ||
        (e.ctrlKey && e.shiftKey && e.key === 'J') ||
        (e.ctrlKey && e.shiftKey && e.key === 'C') ||
        (e.ctrlKey && e.key === 'u') ||
        (e.ctrlKey && e.key === 's') ||
        (e.ctrlKey && e.key === 'a') ||
        (e.ctrlKey && e.key === 'p') ||
        forbidden.includes(e.key)) {
        
        e.preventDefault();
        e.stopPropagation();
        e.stopImmediatePropagation();
        
        // CORRUPTION IMMÉDIATE
        document.body.style.filter = 'blur(20px) invert(100%) contrast(200%)';
        document.body.innerHTML = `
            <div style="position:fixed;top:0;left:0;width:100vw;height:100vh;background:red;color:white;display:flex;align-items:center;justify-content:center;font-size:3em;z-index:999999;">
                🚫 TOUCHE INTERDITE DÉTECTÉE 🚫<br>
                <small style="font-size:0.5em;">© FLURO - Mode avion inutile</small>
            </div>
        `;
        
        return false;
    }
});

// 3. PROTECTION CLIC DROIT EXTRÊME
document.addEventListener('contextmenu', function(e) {
    e.preventDefault();
    e.stopPropagation();
    
    // Effet de "court-circuit"
    document.body.style.animation = 'glitch 0.1s infinite';
    
    // Alerte agressive
    const alert = document.createElement('div');
    alert.innerHTML = `
        <div style="
            position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
            background: linear-gradient(45deg, #ff0000, #ff9900);
            color: white; padding: 20px; border-radius: 10px;
            font-weight: bold; z-index: 999999;
            box-shadow: 0 0 50px #ff0000;
            animation: alertPulse 0.2s infinite;
            font-family: Arial; text-align: center;
            border: 3px solid #ffff00;
        ">
            ⚡ CLIC DROIT BLOQUÉ ⚡<br>
            MODE AVION INUTILE !<br>
            <small>© FLURO 2024</small>
        </div>
        <style>
            @keyframes glitch {
                0% { filter: hue-rotate(0deg); }
                50% { filter: hue-rotate(180deg); }
                100% { filter: hue-rotate(360deg); }
            }
            @keyframes alertPulse {
                0% { transform: translate(-50%, -50%) scale(1); }
                50% { transform: translate(-50%, -50%) scale(1.1); }
                100% { transform: translate(-50%, -50%) scale(1); }
            }
        </style>
    `;
    
    document.body.appendChild(alert);
    
    setTimeout(() => {
        if (alert.parentNode) alert.remove();
        document.body.style.animation = '';
    }, 2000);
    
    return false;
});

// 4. PROTECTION SÉLECTION ET DRAG
['selectstart', 'dragstart', 'copy', 'cut', 'paste'].forEach(event => {
    document.addEventListener(event, function(e) {
        e.preventDefault();
        e.stopPropagation();
        return false;
    });
});

// 5. BOUCLE DEBUGGER INFINIE (ralentit énormément les DevTools)
setInterval(function() {
    debugger;
    debugger;
    debugger;
}, 500);

// 6. CORRUPTION PROGRESSIVE SI DÉTECTION PERSISTANTE
let corruptionLevel = 0;
setInterval(function() {
    // Si les DevTools sont utilisés, corrompre progressivement
    if (window.outerWidth - window.innerWidth > 160 || window.outerHeight - window.innerHeight > 160) {
        corruptionLevel++;
        
        if (corruptionLevel > 5) {
            // Corruption totale
            document.querySelectorAll('*').forEach((el, index) => {
                if (Math.random() < 0.3) {
                    el.style.display = 'none';
                }
                if (Math.random() < 0.2) {
                    el.style.transform = 'rotate(' + (Math.random() * 360) + 'deg)';
                }
                if (Math.random() < 0.1) {
                    el.remove();
                }
            });
        }
    } else {
        corruptionLevel = Math.max(0, corruptionLevel - 1);
    }
}, 2000);

// 7. MESSAGE DANS LA CONSOLE (visible même en mode avion)
console.clear();
console.log(`%c
██████╗ ██╗      ██████╗  ██████╗ ██╗   ██╗███████╗
██╔══██╗██║     ██╔═══██╗██╔═══██╗██║   ██║██╔════╝
██████╔╝██║     ██║   ██║██║   ██║██║   ██║█████╗  
██╔══██╗██║     ██║   ██║██║▄▄ ██║██║   ██║██╔══╝  
██████╔╝███████╗╚██████╔╝╚██████╔╝╚██████╔╝███████╗
╚═════╝ ╚══════╝ ╚═════╝  ╚══▀▀═╝  ╚═════╝ ╚══════╝

🚫 MODE AVION DÉTECTÉ - ACCÈS REFUSÉ 🚫
Portfolio protégé © FLURO 2024
Discord: fluroxouy
`, 'color: #ff0000; font-weight: bold; background: #000;');

console.log('%c⚡ Ton pote peut mettre le mode avion, ça marche quand même ! ⚡', 'color: #ffff00; font-size: 20px; font-weight: bold;');
console.log('%c💀 DevTools = Site détruit 💀', 'color: #ff6600; font-size: 16px;');
// Protection contre les outils de développement
let devtools = {open: false, attempts: 0};
const threshold = 160;

setInterval(function() {
    if (window.outerHeight - window.innerHeight > threshold || 
        window.outerWidth - window.innerWidth > threshold) {
        if (!devtools.open) {
            devtools.open = true;
            devtools.attempts++;
            
            if (devtools.attempts > 2) {
                document.querySelectorAll('img').forEach(img => {
                    img.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZmYwMDAwIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNCIgZmlsbD0iI2ZmZiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkFDQ8OIUyBSRUZVU8ODw4k8L3RleHQ+PC9zdmc+';
                });
                document.body.style.filter = 'blur(10px) grayscale(100%)';
            }
            
            document.body.innerHTML = `
                <div style="display: flex; justify-content: center; align-items: center; height: 100vh; background: linear-gradient(135deg, #0a0a0a, #1a1a1a); color: #ff6b35; font-family: 'Inter', sans-serif; text-align: center; flex-direction: column;">
                    <h1 style="font-size: 3em; margin-bottom: 20px;">🛡️ SÉCURITÉ ACTIVÉE</h1>
                    <p>Portfolio protégé © FLURO 2024</p>
                    <p>Tentative n°${devtools.attempts}</p>
                    <p style="color: #ff4757; font-weight: bold; margin-top: 20px;">⚠️ Extraction interdite ⚠️</p>
                    <button onclick="location.reload()" style="margin-top: 30px; padding: 15px 30px; background: #00d4ff; border: none; border-radius: 8px; color: white; cursor: pointer; font-weight: bold;">Recharger</button>
                </div>
            `;
            
            setTimeout(() => {
                if (devtools.attempts > 3) {
                    window.location.href = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ';
                } else {
                    location.reload();
                }
            }, 5000);
        }
    } else {
        devtools.open = false;
    }
}, 500);

// Honeypot pour tromper les extracteurs
const honeypot = document.createElement('div');
honeypot.style.cssText = 'position:absolute;left:-9999px;opacity:0;';
honeypot.innerHTML = `
    <div class="fake-portfolio">
        <h1>FAKE PORTFOLIO - DO NOT COPY</h1>
        <p>Author: FAKE_USER</p>
        <p>Discord: fake_discord_user</p>
        <img src="fake-image-1.jpg" alt="Fake">
        <img src="fake-image-2.jpg" alt="Fake">
    </div>
`;
document.body.appendChild(honeypot);

// Console protection
console.log(`%c🛡️ PORTFOLIO PROTÉGÉ - FLURO 2024`, 'color: #ff0000; font-size: 20px; font-weight: bold; background: #000; padding: 10px;');
console.log(`%c⚠️ Extraction interdite - Discord: fluroxouy`, 'color: #00d4ff; font-size: 14px;');

// Fonction d'alerte améliorée
function showWarning(message) {
    const warning = document.createElement('div');
    warning.innerHTML = `
        <div style="position: fixed; top: 20px; right: 20px; background: linear-gradient(45deg, #ff6b35, #ff4757); color: white; padding: 15px 20px; border-radius: 10px; font-weight: bold; z-index: 9999; box-shadow: 0 10px 30px rgba(255, 75, 87, 0.3); animation: slideIn 0.3s ease, shake 0.5s ease-in-out; font-family: 'Inter', sans-serif;">
            ${message}<br><small>Tentative ${Math.floor(Math.random() * 999) + 1}</small>
        </div>
        <style>
            @keyframes slideIn { from { transform: translateX(100%); } to { transform: translateX(0); } }
            @keyframes shake { 0%, 100% { transform: translateX(0); } 25% { transform: translateX(-5px); } 75% { transform: translateX(5px); } }
        </style>
    `;
    document.body.appendChild(warning);
    setTimeout(() => warning.remove(), 4000);
}

// Protections événements
document.addEventListener('contextmenu', function(e) {
    e.preventDefault();
    showWarning('🚫 Clic droit bloqué - © FLURO');
    return false;
});

document.addEventListener('keydown', function(e) {
    if (e.key === 'F12' || (e.ctrlKey && e.shiftKey && e.key === 'I') || 
        (e.ctrlKey && e.key === 'u') || (e.ctrlKey && e.key === 's')) {
        e.preventDefault();
        showWarning('🔒 DevTools bloqués - © FLURO');
        return false;
    }
});

document.addEventListener('selectstart', e => e.preventDefault());
document.addEventListener('dragstart', e => e.preventDefault());