// Nav scroll state
const nav = document.querySelector('.rc-nav');
if (nav) {
  const onScroll = () => nav.classList.toggle('scrolled', window.scrollY > 8);
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });
}

// Dark mode toggle, persisted
function rcSetTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('rc-theme', theme);
}
(function initTheme() {
  const saved = localStorage.getItem('rc-theme');
  const preferred = saved || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  rcSetTheme(preferred);
})();
document.addEventListener('click', (e) => {
  const btn = e.target.closest('[data-theme-toggle]');
  if (!btn) return;
  const current = document.documentElement.getAttribute('data-theme');
  rcSetTheme(current === 'dark' ? 'light' : 'dark');
});

// Count-up animation for stat numbers
function rcCountUp(el) {
  const target = parseFloat(el.dataset.countTo);
  const duration = 900;
  const start = performance.now();
  const from = 0;
  function tick(now) {
    const p = Math.min((now - start) / duration, 1);
    const eased = 1 - Math.pow(1 - p, 3);
    el.textContent = Math.round(from + (target - from) * eased).toLocaleString();
    if (p < 1) requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
}
function rcAnimateProgress(el) {
  const to = el.dataset.progressTo || '0';
  requestAnimationFrame(() => { el.style.width = to + '%'; });
}
const rcObserver = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (!entry.isIntersecting) return;
    entry.target.querySelectorAll('[data-count-to]').forEach(rcCountUp);
    entry.target.querySelectorAll('[data-progress-to]').forEach(rcAnimateProgress);
    rcObserver.unobserve(entry.target);
  });
}, { threshold: 0.3 });
document.querySelectorAll('[data-animate-section]').forEach((el) => rcObserver.observe(el));

// Mobile nav toggle
document.addEventListener('click', (e) => {
  const btn = e.target.closest('[data-mobile-nav-toggle]');
  if (!btn) return;
  document.querySelector('.rc-mobile-nav')?.classList.toggle('open');
});
