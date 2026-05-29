/* ====================================================
   MANITOS CREATIVAS — Main JavaScript
   ==================================================== */

'use strict';

/* ── Page Loader ── */
window.addEventListener('load', () => {
  const loader = document.getElementById('page-loader');
  if (loader) {
    setTimeout(() => loader.classList.add('hidden'), 600);
  }
});

/* ── Toast System ── */
const Toast = {
  container: null,

  init() {
    this.container = document.getElementById('toast-container');
    if (!this.container) {
      this.container = document.createElement('div');
      this.container.id = 'toast-container';
      document.body.appendChild(this.container);
    }
    // Show Django messages as toasts
    if (window.__djangoMessages) {
      window.__djangoMessages.forEach(m => {
        const type = m.tags.includes('error') ? 'error'
          : m.tags.includes('success') ? 'success'
          : 'info';
        this.show(m.text, type);
      });
    }
  },

  show(message, type = 'info', duration = 4000) {
    const icons = {
      success: '<i class="bi bi-check-circle-fill" style="color:#10B981;font-size:1.2rem;"></i>',
      error:   '<i class="bi bi-x-circle-fill" style="color:#EF4444;font-size:1.2rem;"></i>',
      info:    '<i class="bi bi-info-circle-fill" style="color:#7C3AED;font-size:1.2rem;"></i>',
      warning: '<i class="bi bi-exclamation-triangle-fill" style="color:#FBBF24;font-size:1.2rem;"></i>',
    };
    const colors = {
      success: '#10B981',
      error:   '#EF4444',
      info:    '#7C3AED',
      warning: '#FBBF24',
    };
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.style.borderLeftColor = colors[type] || colors.info;
    toast.innerHTML = `
      <span style="display:inline-flex;align-items:center;">${icons[type] || icons.info}</span>
      <span style="flex:1">${message}</span>
      <button onclick="this.parentElement.remove()"
        style="background:none;border:none;cursor:pointer;font-size:1.1rem;color:#9CA3AF;padding:0 .25rem;">×</button>
    `;
    this.container.appendChild(toast);
    setTimeout(() => {
      toast.style.animation = 'none';
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(100px)';
      toast.style.transition = 'all .4s ease';
      setTimeout(() => toast.remove(), 400);
    }, duration);
    return toast;
  },
};

/* ── Accessibility System ── */
const A11y = {
  STORAGE_KEY: 'manitos_a11y',
  active: new Set(),

  init() {
    const btn   = document.getElementById('a11y-btn');
    const panel = document.getElementById('a11y-panel');
    const reset = document.getElementById('a11y-reset');
    if (!btn || !panel) return;

    // Toggle panel
    btn.addEventListener('click', () => panel.classList.toggle('open'));

    // Close on outside click
    document.addEventListener('click', e => {
      if (!btn.contains(e.target) && !panel.contains(e.target)) {
        panel.classList.remove('open');
      }
    });

    // Item toggles
    panel.querySelectorAll('.a11y-item').forEach(item => {
      item.addEventListener('click', () => {
        const key = item.dataset.a11y;
        if (this.active.has(key)) {
          this.deactivate(key, item);
        } else {
          this.activate(key, item);
        }
        this.save();
      });
    });

    // Reset
    if (reset) reset.addEventListener('click', () => this.resetAll());

    // Restore from localStorage
    this.load();
  },

  activate(key, item) {
    document.body.classList.add(`a11y-${key}`);
    this.active.add(key);
    if (item) item.classList.add('active');
  },

  deactivate(key, item) {
    document.body.classList.remove(`a11y-${key}`);
    this.active.delete(key);
    if (item) item.classList.remove('active');
  },

  resetAll() {
    this.active.forEach(key => {
      document.body.classList.remove(`a11y-${key}`);
      const item = document.querySelector(`[data-a11y="${key}"]`);
      if (item) item.classList.remove('active');
    });
    this.active.clear();
    this.save();
    Toast.show('Accesibilidad restaurada', 'info');
  },

  save() {
    try {
      localStorage.setItem(this.STORAGE_KEY, JSON.stringify([...this.active]));
    } catch(e) {}
  },

  load() {
    try {
      const saved = JSON.parse(localStorage.getItem(this.STORAGE_KEY) || '[]');
      saved.forEach(key => {
        const item = document.querySelector(`[data-a11y="${key}"]`);
        this.activate(key, item);
      });
    } catch(e) {}
  },
};

/* ── Confetti ── */
const Confetti = {
  colors: ['#7C3AED','#EC4899','#FBBF24','#10B981','#3B82F6','#F97316'],

  fire(count = 60, duration = 3000) {
    for (let i = 0; i < count; i++) {
      setTimeout(() => this._piece(), Math.random() * 600);
    }
  },

  _piece() {
    const el = document.createElement('div');
    el.className = 'confetti-piece';
    el.style.cssText = `
      left: ${Math.random() * 100}vw;
      top: -10px;
      background: ${this.colors[Math.floor(Math.random() * this.colors.length)]};
      width: ${6 + Math.random() * 8}px;
      height: ${6 + Math.random() * 8}px;
      border-radius: ${Math.random() > .5 ? '50%' : '2px'};
      animation-duration: ${2 + Math.random() * 2}s;
      animation-delay: ${Math.random() * .5}s;
    `;
    document.body.appendChild(el);
    setTimeout(() => el.remove(), 4500);
  },
};

/* ── Stars Animation ── */
function awardStars(container, count) {
  for (let i = 0; i < count; i++) {
    const star = document.createElement('span');
    star.innerHTML = '<i class="bi bi-star-fill"></i>';
    star.style.cssText = `
      position:fixed;
      font-size:${1.5 + Math.random()}rem;
      color:#FBBF24;
      left:${30 + Math.random() * 40}vw;
      top:${20 + Math.random() * 60}vh;
      z-index:99999;
      pointer-events:none;
      animation:star-pop .6s cubic-bezier(.34,1.56,.64,1) ${i*.08}s both,
                star-fade 1s ease ${i*.08 + .6}s both;
    `;
    document.body.appendChild(star);
    setTimeout(() => star.remove(), (i * 80) + 1600);
  }
}

// Inject star animations
const starStyle = document.createElement('style');
starStyle.textContent = `
  @keyframes star-pop {
    from { transform:scale(0) rotate(-30deg); opacity:0; }
    to   { transform:scale(1) rotate(0deg); opacity:1; }
  }
  @keyframes star-fade {
    from { opacity:1; transform:translateY(0); }
    to   { opacity:0; transform:translateY(-40px); }
  }
`;
document.head.appendChild(starStyle);

/* ── Init ── */
document.addEventListener('DOMContentLoaded', () => {
  Toast.init();
  A11y.init();

  // Expose globals
  window.Toast    = Toast;
  window.Confetti = Confetti;
  window.awardStars = awardStars;
});
