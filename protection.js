// ═══════════════════════════════════════════
// 🛡️ PROTECTIONS ANTI-VOL AVANCÉES - FLURO
// ═══════════════════════════════════════════

// Variables obfusquées
const _0x4f3a = ['contextmenu', 'keydown', 'F12', 'preventDefault', 'ctrlKey', 'shiftKey'];
const _0x1b7c = btoa('FLURO-PORTFOLIO-PROTECTED-2024');

// Protection contre extraction automatique
(function() {
    const botPatterns = [
        /bot/i, /crawler/i, /spider/i, /scraper/i,
        /wget/i, /curl/i, /httrack/i, /webcopier/i
    ];
    
    const userAgent = navigator.userAgent;
    const isBot = botPatterns.some(pattern => pattern.test(userAgent));
    
    if (isBot) {
        document.body.innerHTML = `
            <div style="background: #000; color: #ff0000; font-family: monospace; padding: 50px; text-align: center; height: 100vh; display: flex; flex-direction: column; justify-content: center;">
                <h1>⚠️ BOT DÉTECTÉ ⚠️</h1>
                <p>Accès refusé aux robots d'extraction</p>
                <p>© FLURO 2024 - Portfolio protégé</p>
                <p>IP logged: ${Math.random().toString(36).substring(7)}</p>
            </div>
        `;
        return;
    }
})();

// Protection par domaine
if (window.location.hostname !== 'ytmrflurox.github.io' && 
    window.location.hostname !== 'localhost' && 
    window.location.hostname !== '127.0.0.1') {
    document.body.innerHTML = `
        <div style="background: #000; color: #00ff00; font-family: 'Courier New'; padding: 50px; height: 100vh;">
            <h1>[ACCÈS REFUSÉ]</h1>
            <p>Ce portfolio ne peut être consulté que sur le domaine officiel.</p>
            <p>Domaine autorisé: ytmrflurox.github.io</p>
            <p>Domaine actuel: ${window.location.hostname}</p>
            <p>© FLURO 2024</p>
        </div>
    `;
    throw new Error('Domain protection activated');
}

// Anti-bot behavior detection
let pageLoadTime = Date.now();
let interactionCount = 0;

document.addEventListener('mousemove', () => interactionCount++);
document.addEventListener('click', () => interactionCount++);
document.addEventListener('scroll', () => interactionCount++);

// Vérification comportement suspect
setInterval(() => {
    const timeOnPage = Date.now() - pageLoadTime;
    if (timeOnPage > 8000 && interactionCount < 5) {
        console.clear();
        document.head.innerHTML = '';
        document.body.innerHTML = `
            <div style="background: linear-gradient(45deg, #ff0000, #000); color: white; font-family: Arial; height: 100vh; display: flex; align-items: center; justify-content: center; text-align: center; flex-direction: column;">
                <h1 style="font-size: 3em;">🚨 EXTRACTION DÉTECTÉE</h1>
                <p>Comportement de bot détecté</p>
                <p>© FLURO 2024</p>
            </div>
        `;
    }
}, 8000);
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