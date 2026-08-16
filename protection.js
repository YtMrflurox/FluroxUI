// ═══════════════════════════════════════════
// 🛡️ PROTECTION PORTFOLIO - FLURO 2024
// ═══════════════════════════════════════════

(function () {
    'use strict';

    function showWarning(message) {
        const existing = document.getElementById('fluro-warn');
        if (existing) return;

        const el = document.createElement('div');
        el.id = 'fluro-warn';
        el.style.cssText = [
            'position:fixed', 'top:20px', 'right:20px',
            'background:linear-gradient(45deg,#ff6b35,#ff4757)',
            'color:#fff', 'padding:14px 20px', 'border-radius:10px',
            'font-weight:bold', 'z-index:2147483647',
            'box-shadow:0 8px 24px rgba(255,75,87,.4)',
            'font-family:Inter,sans-serif', 'pointer-events:none',
            'opacity:1', 'transition:opacity .3s'
        ].join(';');
        el.textContent = message;
        document.body.appendChild(el);
        setTimeout(() => { el.style.opacity = '0'; }, 2700);
        setTimeout(() => el.remove(), 3000);
    }

    // Clic droit
    document.addEventListener('contextmenu', function (e) {
        e.preventDefault();
        showWarning('🚫 Clic droit bloqué — © FLURO');
    });

    // Raccourcis DevTools + copie clavier
    document.addEventListener('keydown', function (e) {
        const ctrl = e.ctrlKey || e.metaKey;
        const blocked =
            e.key === 'F12' ||
            (ctrl && e.shiftKey && ['I', 'J', 'C', 'i', 'j', 'c'].includes(e.key)) ||
            (ctrl && ['u', 'U', 's', 'S', 'a', 'A', 'p', 'P'].includes(e.key));

        if (blocked) {
            e.preventDefault();
            e.stopImmediatePropagation();
            showWarning('🔒 Action bloquée — © FLURO');
        }
    });

    // Sélection / drag / copie
    ['selectstart', 'dragstart', 'copy', 'cut'].forEach(function (ev) {
        document.addEventListener(ev, function (e) { e.preventDefault(); });
    });

    // user-select CSS
    const s = document.documentElement.style;
    s.userSelect = 'none';
    s.webkitUserSelect = 'none';

    // Message console
    console.clear();
    console.log(
        '%c🛡️ PORTFOLIO PROTÉGÉ — FLURO 2024',
        'color:#ff0000;font-size:20px;font-weight:bold;background:#000;padding:10px;'
    );
    console.log(
        '%c⚠️ Extraction interdite  —  Discord: fluroxouy',
        'color:#00d4ff;font-size:13px;'
    );
})();
