/**
 * Яндекс.Метрика — car2me.ru
 * Цели в интерфейсе Метрики: тип «JavaScript-событие», идентификаторы из GOALS
 */
const METRIKA_ID = 112130182;

const GOALS = {
  ctaOrder: 'cta_order',
  ctaForm: 'cta_form',
  ctaCase: 'cta_case',
  sectionOrder: 'section_order',
  sectionForm: 'section_form',
  paySber: 'pay_sber',
  cookieAccept: 'cookie_accept',
};

const CONSENT_KEY = 'car2me_analytics_consent';

function metrikaAllowed() {
  return METRIKA_ID > 0 && localStorage.getItem(CONSENT_KEY) === '1';
}

function reachGoal(goal) {
  if (!metrikaAllowed() || typeof window.ym !== 'function') return;
  window.ym(METRIKA_ID, 'reachGoal', goal);
}

function loadMetrika() {
  if (!METRIKA_ID || window.ym) return;

  (function (m, e, t, r, i, k, a) {
    m[i] =
      m[i] ||
      function () {
        (m[i].a = m[i].a || []).push(arguments);
      };
    m[i].l = 1 * new Date();
    for (let j = 0; j < document.scripts.length; j++) {
      if (document.scripts[j].src === r) return;
    }
    k = e.createElement(t);
    a = e.getElementsByTagName(t)[0];
    k.async = 1;
    k.src = r;
    a.parentNode.insertBefore(k, a);
  })(window, document, 'script', 'https://mc.yandex.ru/metrika/tag.js', 'ym');

  window.ym(METRIKA_ID, 'init', {
    clickmap: true,
    trackLinks: true,
    accurateTrackBounce: true,
    webvisor: true,
    trackHash: true,
    ecommerce: 'dataLayer',
  });
}

function sendFirstHit(goal) {
  const tryHit = (attempts = 0) => {
    if (typeof window.ym !== 'function') {
      if (attempts < 30) setTimeout(() => tryHit(attempts + 1), 100);
      return;
    }
    window.ym(METRIKA_ID, 'hit', window.location.href);
    if (goal) window.ym(METRIKA_ID, 'reachGoal', goal);
  };
  tryHit();
}

function initConsentBanner() {
  const banner = document.getElementById('cookie-banner');
  const acceptBtn = document.getElementById('cookie-accept');
  const declineBtn = document.getElementById('cookie-decline');
  if (!banner || !acceptBtn || !declineBtn) return;

  const stored = localStorage.getItem(CONSENT_KEY);
  if (stored === '1' || stored === '0') {
    banner.hidden = true;
    if (stored === '1') loadMetrika();
    return;
  }

  banner.hidden = false;

  acceptBtn.addEventListener('click', () => {
    localStorage.setItem(CONSENT_KEY, '1');
    banner.hidden = true;
    loadMetrika();
    sendFirstHit(GOALS.cookieAccept);
  });

  declineBtn.addEventListener('click', () => {
    localStorage.setItem(CONSENT_KEY, '0');
    banner.hidden = true;
  });
}

function initClickGoals() {
  document.addEventListener('click', (event) => {
    const link = event.target.closest('a[href]');
    if (!link) return;

    const href = link.getAttribute('href') || '';

    if (href === '#order' || href.includes('#order')) {
      reachGoal(GOALS.ctaOrder);
    }
    if (href === '#form' || link.id === 'form-btn') {
      reachGoal(GOALS.ctaForm);
    }
    if (href === '#case') {
      reachGoal(GOALS.ctaCase);
    }
    if (link.classList.contains('pay-link-btn')) {
      reachGoal(GOALS.paySber);
    }
  });
}

function initSectionGoals() {
  const sections = [
    { id: 'order', goal: GOALS.sectionOrder },
    { id: 'form', goal: GOALS.sectionForm },
  ];

  if (!('IntersectionObserver' in window)) return;

  const seen = new Set();

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting || entry.intersectionRatio < 0.35) return;
        const goal = entry.target.dataset.goal;
        if (!goal || seen.has(goal)) return;
        seen.add(goal);
        reachGoal(goal);
      });
    },
    { threshold: [0.35, 0.5] }
  );

  sections.forEach(({ id, goal }) => {
    const el = document.getElementById(id);
    if (!el) return;
    el.dataset.goal = goal;
    observer.observe(el);
  });
}

document.addEventListener('DOMContentLoaded', () => {
  initConsentBanner();
  initClickGoals();
  initSectionGoals();

  if (metrikaAllowed()) {
    loadMetrika();
  }
});
