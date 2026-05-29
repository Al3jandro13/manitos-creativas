/* ====================================================
   MANITOS CREATIVAS — Landing Page JavaScript
   ==================================================== */

'use strict';

/* ── Navbar scroll effect ── */
const navbar = document.getElementById('navbar');
if (navbar) {
  window.addEventListener('scroll', () => {
    navbar.classList.toggle('scrolled', window.scrollY > 60);
  });
}

/* ── Hamburger menu ── */
const hamburger = document.getElementById('hamburger');
const navLinks  = document.getElementById('nav-links');
if (hamburger && navLinks) {
  hamburger.addEventListener('click', () => {
    const open = navLinks.style.display === 'flex';
    navLinks.style.cssText = open
      ? ''
      : 'display:flex;flex-direction:column;position:absolute;top:100%;left:0;right:0;background:rgba(255,248,240,.98);backdrop-filter:blur(16px);padding:1.5rem;gap:1.25rem;box-shadow:0 8px 32px rgba(0,0,0,.1);z-index:999;';
  });
}

/* ── Particle Canvas ── */
(function initParticles() {
  const canvas = document.getElementById('particles-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  let W, H, particles = [];

  const COLORS = ['rgba(255,255,255,.25)','rgba(253,230,138,.3)','rgba(249,168,212,.25)',
                  'rgba(196,181,253,.3)','rgba(52,211,153,.25)','rgba(251,191,36,.28)'];

  function resize() {
    W = canvas.width  = canvas.offsetWidth;
    H = canvas.height = canvas.offsetHeight;
  }

  function Particle() {
    this.reset();
  }
  Particle.prototype.reset = function() {
    this.x    = Math.random() * W;
    this.y    = Math.random() * H;
    this.r    = 2 + Math.random() * 5;
    this.vx   = (Math.random() - .5) * .6;
    this.vy   = -.3 - Math.random() * .5;
    this.alpha= .2 + Math.random() * .5;
    this.color= COLORS[Math.floor(Math.random() * COLORS.length)];
    this.life = 0;
    this.maxLife = 200 + Math.random() * 300;
  };
  Particle.prototype.update = function() {
    this.x  += this.vx;
    this.y  += this.vy;
    this.life++;
    if (this.life > this.maxLife || this.y < -30) this.reset();
  };
  Particle.prototype.draw = function() {
    const progress = this.life / this.maxLife;
    const fade = progress < .1 ? progress / .1 : progress > .8 ? (1 - progress) / .2 : 1;
    ctx.globalAlpha = this.alpha * fade;
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2);
    ctx.fillStyle = this.color;
    ctx.fill();
    ctx.globalAlpha = 1;
  };

  function init() {
    resize();
    particles = Array.from({ length: 55 }, () => {
      const p = new Particle();
      p.life = Math.random() * p.maxLife; // stagger
      return p;
    });
  }

  function animate() {
    ctx.clearRect(0, 0, W, H);
    particles.forEach(p => { p.update(); p.draw(); });
    requestAnimationFrame(animate);
  }

  window.addEventListener('resize', resize);
  init();
  animate();
})();

/* ── Animated Counter ── */
function animateCounter(el, target, duration = 1800) {
  let start = null;
  const startVal = 0;
  function step(timestamp) {
    if (!start) start = timestamp;
    const progress = Math.min((timestamp - start) / duration, 1);
    const ease = 1 - Math.pow(1 - progress, 3); // cubic ease-out
    el.textContent = Math.round(startVal + (target - startVal) * ease);
    if (progress < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

/* ── Intersection Observer — Scroll Reveal ── */
const revealObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      revealObserver.unobserve(entry.target);

      // Trigger counters when they become visible
      const counters = entry.target.querySelectorAll('[data-count]');
      counters.forEach(counter => {
        const target = parseInt(counter.dataset.count, 10);
        animateCounter(counter, target);
      });
    }
  });
}, { threshold: 0.12, rootMargin: '0px 0px -60px 0px' });

document.querySelectorAll('.reveal, .reveal-left, .reveal-right').forEach(el => {
  revealObserver.observe(el);
});

// Stat cards in hero-intro: animate counters on scroll-into-view
const hiCardsEl = document.querySelector('.hi-cards-grid');
if (hiCardsEl) {
  const hiCardsObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.querySelectorAll('[data-count]').forEach(counter => {
          animateCounter(counter, parseInt(counter.dataset.count));
        });
        hiCardsObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.4 });
  hiCardsObserver.observe(hiCardsEl);
}

/* ── CTA Bubbles ── */
(function initBubbles() {
  const container = document.getElementById('cta-bubbles');
  if (!container) return;
  const count = 12;
  for (let i = 0; i < count; i++) {
    const bubble = document.createElement('div');
    bubble.className = 'cta-bubble';
    const size = 30 + Math.random() * 80;
    bubble.style.cssText = `
      width:${size}px;height:${size}px;
      left:${Math.random() * 100}%;
      bottom:-${size}px;
      animation-duration:${8 + Math.random() * 8}s;
      animation-delay:${Math.random() * 8}s;
    `;
    container.appendChild(bubble);
  }
})();

/* ── Cursor Parallax on Hero ── */
/* Wide speed range (0.3–3.0) creates strong depth illusion through motion.
   High lerp (0.10) and large multipliers (72/52 px) give snappy response. */
(function initCursorParallax() {
  const hero = document.querySelector('.hero');
  if (!hero) return;

  const targets = [];
  hero.querySelectorAll('[data-speed]').forEach(el => {
    targets.push({
      el,
      speed: parseFloat(el.dataset.speed || 1),
      rot:   parseFloat(el.dataset.rot   || 0),
    });
  });
  if (!targets.length) return;

  let ready = false;
  let lx = 0, ly = 0;
  let tx = 0, ty = 0;

  (function loop() {
    if (ready) {
      lx += (tx - lx) * 0.10;
      ly += (ty - ly) * 0.10;
      targets.forEach(({ el, speed, rot }) => {
        el.style.transform =
          `rotate(${rot}deg) translate(${lx * speed * 72}px, ${ly * speed * 52}px)`;
      });
    }
    requestAnimationFrame(loop);
  })();

  document.addEventListener('mousemove', e => {
    if (!ready) return;
    const rect = hero.getBoundingClientRect();
    if (e.clientY < rect.top || e.clientY > rect.bottom) return;
    tx = (e.clientX / window.innerWidth  - 0.5);
    ty = (e.clientY / window.innerHeight - 0.5);
  });

  // Gently reset when mouse leaves the hero area
  hero.addEventListener('mouseleave', () => { tx = 0; ty = 0; });

  setTimeout(() => { ready = true; }, 2500);
})();

/* ── Activity pill hover sparkle ── */
document.querySelectorAll('.activity-pill').forEach(pill => {
  pill.addEventListener('mouseenter', function() {
    const sparkle = document.createElement('span');
    sparkle.innerHTML = '<i class="bi bi-stars"></i>';
    sparkle.style.cssText = `
      position:absolute;font-size:.9rem;color:#FBBF24;
      top:${Math.random() * 50}%;left:${Math.random() * 80 + 10}%;
      pointer-events:none;z-index:10;
      animation:sparkle-pop .5s ease forwards;
    `;
    this.style.position = 'relative';
    this.style.overflow = 'visible';
    this.appendChild(sparkle);
    setTimeout(() => sparkle.remove(), 500);
  });
});

// Sparkle pop animation
const style = document.createElement('style');
style.textContent = `
  @keyframes sparkle-pop {
    0%   { opacity:0; transform:scale(0) rotate(0); }
    50%  { opacity:1; transform:scale(1.4) rotate(20deg); }
    100% { opacity:0; transform:scale(0) rotate(40deg) translateY(-15px); }
  }
  @keyframes char2-float {
    0%,100% { transform:translateY(0) rotate(-2deg); }
    50%      { transform:translateY(-24px) rotate(2deg); }
  }
  @keyframes char1-float {
    0%,100% { transform:translateY(0) rotate(2deg); }
    50%      { transform:translateY(-20px) rotate(-2deg); }
  }
`;
document.head.appendChild(style);

/* ── Character Click Dialogs ── */
(function initCharDialogs() {
  const LUMI = [
    '<i class="bi bi-heart-fill"></i> ¡Me alegra que estés aquí!',
    '<i class="bi bi-rainbow"></i> ¡Los colores son pura magia!',
    '<i class="bi bi-stars"></i> ¡El arte nos hace felices!',
    '<i class="bi bi-balloon-fill"></i> ¡Hoy va a ser un día increíble!',
    '<i class="bi bi-music-note-beamed"></i> ¡Crear es lo mejor del mundo!',
  ];
  const PINCELIN = [
    '<i class="bi bi-star-fill"></i> ¡Vamos a crear algo increíble!',
    '<i class="bi bi-pencil-fill"></i> ¡Soy el pincel más creativo!',
    '<i class="bi bi-lightning-fill"></i> ¡Tu imaginación no tiene límites!',
    '<i class="bi bi-award-fill"></i> ¡Eres un artista genial!',
    '<i class="bi bi-brush-fill"></i> ¡Pintar es lo más divertido!',
  ];

  const timers = {};

  function showDialog(wrapper, text, key) {
    const old = wrapper.querySelector('.char-click-dialog');
    if (old) { old.remove(); clearTimeout(timers[key]); }

    const bubble = document.createElement('div');
    bubble.className = 'char-click-dialog';
    bubble.innerHTML = text;
    wrapper.style.cursor = 'pointer';
    wrapper.appendChild(bubble);

    timers[key] = setTimeout(() => {
      bubble.classList.add('dismissing');
      setTimeout(() => bubble.remove(), 260);
    }, 3200);
  }

  let lumiIdx = 0, pincelinIdx = 0;

  const lumiWrap = document.querySelector('.char-wrapper-2');
  if (lumiWrap) {
    lumiWrap.style.cursor = 'pointer';
    lumiWrap.addEventListener('click', () => {
      showDialog(lumiWrap, LUMI[lumiIdx], 'lumi');
      lumiIdx = (lumiIdx + 1) % LUMI.length;
    });
  }

  const pincelinWrap = document.querySelector('.char-wrapper-1');
  if (pincelinWrap) {
    pincelinWrap.style.cursor = 'pointer';
    pincelinWrap.addEventListener('click', () => {
      showDialog(pincelinWrap, PINCELIN[pincelinIdx], 'pincelin');
      pincelinIdx = (pincelinIdx + 1) % PINCELIN.length;
    });
  }

  // CTA section — wrap each img in a relative container
  const ctaChars = document.querySelector('.cta-chars');
  if (ctaChars) {
    ctaChars.querySelectorAll('img').forEach((img, i) => {
      const phrases = i === 0 ? LUMI : PINCELIN;
      const key = i === 0 ? 'lumi-cta' : 'pincelin-cta';
      let idx = 0;
      const wrap = document.createElement('span');
      wrap.style.cssText = 'position:relative;display:inline-block;cursor:pointer;';
      img.replaceWith(wrap);
      wrap.appendChild(img);
      wrap.addEventListener('click', () => {
        showDialog(wrap, phrases[idx], key);
        idx = (idx + 1) % phrases.length;
      });
    });
  }
})();

/* ── Smooth scroll for anchor links ── */
document.querySelectorAll('a[href^="#"]').forEach(link => {
  link.addEventListener('click', e => {
    const target = document.querySelector(link.getAttribute('href'));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      // Close mobile menu if open
      if (navLinks && navLinks.style.display === 'flex') {
        navLinks.style.cssText = '';
      }
    }
  });
});
