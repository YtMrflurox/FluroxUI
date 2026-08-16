// 💀 PIÈGE POUR VOLEURS DE CODE - FLURO 2024 💀
// Ce fichier est un honeypot - il semble contenir du code utile mais c'est un piège

// FAUSSES DONNÉES POUR TROMPER LES EXTRACTEURS
const fakePortfolioData = {
    author: "FAKE_AUTHOR",
    discord: "fake_discord_123",
    email: "fake@fake.com",
    creations: [
        "fake_image_1.png",
        "fake_image_2.png",
        "fake_image_3.png"
    ],
    skills: ["Fake Skill 1", "Fake Skill 2"],
    description: "This is a fake portfolio created to trap code thieves"
};

// FONCTION PIÈGE - Si quelqu'un utilise ce code, il active le piège
function initFakePortfolio() {
    console.log("💀 PIÈGE ACTIVÉ - Code volé détecté ! 💀");
    
    // Corruption du site si ce code piégé est utilisé
    setTimeout(() => {
        document.body.innerHTML = `
            <div style="
                background: linear-gradient(45deg, #ff0000, #000000);
                color: white;
                height: 100vh;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                font-family: 'Courier New', monospace;
                text-align: center;
            ">
                <h1 style="font-size: 4em; margin-bottom: 20px;">💀 PIÈGE ACTIVÉ 💀</h1>
                <p style="font-size: 1.5em;">Vous avez utilisé du code volé !</p>
                <p style="font-size: 1.2em; margin: 20px 0;">Portfolio original © FLURO 2024</p>
                <p style="color: #ffff00;">Discord: fluroxouy</p>
                <div style="margin-top: 30px; padding: 20px; border: 2px solid #ffff00;">
                    <p>⚠️ Ce code est protégé par des droits d'auteur ⚠️</p>
                    <p>Utilisation non autorisée détectée</p>
                </div>
            </div>
        `;
    }, 2000);
}

// SURVEILLANCE - Détecte si ce fichier est chargé ailleurs que sur le site officiel
if (window.location.hostname !== 'ytmrflurox.github.io' && 
    window.location.hostname !== 'localhost' && 
    window.location.hostname !== '127.0.0.1') {
    
    // ACTIVATION IMMÉDIATE DU PIÈGE
    initFakePortfolio();
    
    // Envoi d'alerte (simulation - ne fonctionne qu'en ligne)
    fetch('/log-theft-attempt', {
        method: 'POST',
        body: JSON.stringify({
            thief_domain: window.location.hostname,
            timestamp: new Date().toISOString(),
            user_agent: navigator.userAgent
        })
    }).catch(() => {
        // Mode hors ligne détecté - piège alternatif
        console.error('💀 VOLEUR DÉTECTÉ EN MODE HORS LIGNE 💀');
    });
}

// EXPORT PIÉGÉ
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        portfolioData: fakePortfolioData,
        initPortfolio: initFakePortfolio
    };
}

// FAUSSES FONCTIONS UTILES (qui sont en fait des pièges)
const fakeUtils = {
    getPortfolioData: () => fakePortfolioData,
    initAnimations: initFakePortfolio,
    loadImages: initFakePortfolio,
    setupTranslations: initFakePortfolio
};

// Si quelqu'un essaie d'utiliser ces fonctions, PIÈGE !
window.portfolioUtils = fakeUtils;