document.addEventListener('DOMContentLoaded', function () {
  initTheme();
  initSidebar();
  initScrollTop();
});

function initTheme() {
  const savedTheme = localStorage.getItem('dtc_theme') || 'light';
  applyTheme(savedTheme);

  const themeBtn = document.getElementById('btn-toggle-theme');
  if (themeBtn) {
    themeBtn.addEventListener('click', function () {
      const current = document.documentElement.getAttribute('data-theme');
      const next = current === 'dark' ? 'light' : 'dark';
      localStorage.setItem('dtc_theme', next);
      applyTheme(next);
    });
  }
}

function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  updateThemeIcon(theme);

  if (typeof Chart !== 'undefined') {
    if (theme === 'dark') {
      Chart.defaults.color = '#A8A29E';
      Chart.defaults.borderColor = '#44403C';
    } else {
      Chart.defaults.color = '#444444';
      Chart.defaults.borderColor = '#FED7AA';
    }
  }
}

function updateThemeIcon(theme) {
  const icon = document.querySelector('#btn-toggle-theme i');
  if (icon) {
    icon.className = theme === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-stars-fill';
  }
}

function initSidebar() {
  const toggleBtn = document.getElementById('btn-toggle-sidebar');
  const sidebar = document.getElementById('sidebar');
  const content = document.getElementById('content-wrapper');

  if (!toggleBtn || !sidebar || !content) return;

  let overlay = document.getElementById('sidebar-overlay');
  if (!overlay) {
    overlay = document.createElement('div');
    overlay.id = 'sidebar-overlay';
    overlay.style.cssText = 'display:none;position:fixed;inset:0;background:rgba(0,0,0,0.4);z-index:1035;';
    document.body.appendChild(overlay);
  }

  toggleBtn.addEventListener('click', function () {
    if (window.innerWidth <= 992) {
      const isOpen = sidebar.classList.contains('show');
      sidebar.classList.toggle('show', !isOpen);
      overlay.style.display = isOpen ? 'none' : 'block';
    } else {
      sidebar.classList.toggle('collapsed');
      content.classList.toggle('expanded');
    }
  });

  overlay.addEventListener('click', function () {
    sidebar.classList.remove('show');
    overlay.style.display = 'none';
  });

  window.addEventListener('resize', function () {
    if (window.innerWidth > 992) {
      sidebar.classList.remove('show');
      overlay.style.display = 'none';
    }
  });
}

function initScrollTop() {
  const btn = document.getElementById('scroll-top');
  if (!btn) return;

  window.addEventListener('scroll', function () {
    btn.classList.toggle('show', window.scrollY > 300);
  });

  btn.addEventListener('click', function () {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
}

function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const colorMap = {
    success: '#198754',
    error: '#DC3545',
    warning: '#F59E0B',
    info: '#0DCAF0'
  };

  const toastEl = document.createElement('div');
  toastEl.className = 'toast align-items-center border-0 mb-2 text-white';
  toastEl.style.backgroundColor = colorMap[type] || colorMap.info;
  toastEl.setAttribute('role', 'alert');
  toastEl.setAttribute('aria-live', 'assertive');
  toastEl.setAttribute('aria-atomic', 'true');

  toastEl.innerHTML = `
    <div class="d-flex">
      <div class="toast-body fw-medium">${message}</div>
      <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
    </div>
  `;

  container.appendChild(toastEl);
  const toast = new bootstrap.Toast(toastEl, { delay: 4500 });
  toast.show();

  toastEl.addEventListener('hidden.bs.toast', function () {
    toastEl.remove();
  });
}

function showLoading(show = true, text = 'Memproses data...') {
  const overlay = document.getElementById('loading-overlay');
  const label = document.getElementById('loading-text');
  if (!overlay) return;
  if (label && text) label.innerText = text;
  overlay.classList.toggle('active', show);
}

