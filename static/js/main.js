/* ==========================================================================
   Smart Inventory & Stock Management System - Main JavaScript Engine
   Handles Sidebar Toggle, Theme Switching, Toasts, and Live Search
   ========================================================================== */

document.addEventListener('DOMContentLoaded', function() {
  
  // ── 1. Theme Management (Dark / Light Mode) ────────────────────────────────
  const themeToggleBtn = document.getElementById('themeToggle');
  const themeIcon = document.getElementById('themeIcon');
  
  function applyTheme(theme) {
    if (theme === 'light') {
      document.body.classList.add('light-mode');
      document.documentElement.setAttribute('data-bs-theme', 'light');
      if (themeIcon) themeIcon.className = 'bi bi-sun-fill';
    } else {
      document.body.classList.remove('light-mode');
      document.documentElement.setAttribute('data-bs-theme', 'dark');
      if (themeIcon) themeIcon.className = 'bi bi-moon-stars-fill';
    }
  }

  // Load stored theme or system preference
  const savedTheme = localStorage.getItem('smartinv_theme') || 'dark';
  applyTheme(savedTheme);

  if (themeToggleBtn) {
    themeToggleBtn.addEventListener('click', function() {
      const currentTheme = document.body.classList.contains('light-mode') ? 'light' : 'dark';
      const newTheme = currentTheme === 'light' ? 'dark' : 'light';
      localStorage.setItem('smartinv_theme', newTheme);
      document.cookie = `theme=${newTheme};path=/;max-age=31536000`;
      applyTheme(newTheme);
    });
  }

  // ── 2. Sidebar Mobile Toggle ───────────────────────────────────────────────
  const sidebar = document.getElementById('sidebar');
  const sidebarToggle = document.getElementById('sidebarToggle');
  const sidebarClose = document.getElementById('sidebarClose');
  const sidebarOverlay = document.getElementById('sidebarOverlay');

  function openSidebar() {
    if (sidebar) sidebar.classList.add('show');
    if (sidebarOverlay) sidebarOverlay.classList.add('show');
  }

  function closeSidebar() {
    if (sidebar) sidebar.classList.remove('show');
    if (sidebarOverlay) sidebarOverlay.classList.remove('show');
  }

  if (sidebarToggle) sidebarToggle.addEventListener('click', openSidebar);
  if (sidebarClose) sidebarClose.addEventListener('click', closeSidebar);
  if (sidebarOverlay) sidebarOverlay.addEventListener('click', closeSidebar);

  // ── 3. Global Instant Search ────────────────────────────────────────────────
  const globalSearchInput = document.getElementById('globalSearchInput');
  const searchResults = document.getElementById('searchResults');

  if (globalSearchInput && searchResults) {
    let searchDebounce;
    globalSearchInput.addEventListener('input', function() {
      clearTimeout(searchDebounce);
      const query = this.value.trim();

      if (query.length < 2) {
        searchResults.style.display = 'none';
        searchResults.innerHTML = '';
        return;
      }

      searchDebounce = setTimeout(() => {
        fetch(`/products/api/search/?q=${encodeURIComponent(query)}`)
          .then(res => res.json())
          .then(data => {
            searchResults.innerHTML = '';
            if (data.products && data.products.length > 0) {
              data.products.forEach(prod => {
                const item = document.createElement('a');
                item.href = `/products/${prod.id}/`;
                item.className = 'dropdown-item d-flex justify-content-between align-items-center py-2';
                item.innerHTML = `
                  <div>
                    <div class="fw-semibold text-body">${prod.name}</div>
                    <small class="text-muted">SKU: ${prod.sku}</small>
                  </div>
                  <span class="badge bg-primary">₹${prod.selling_price}</span>
                `;
                searchResults.appendChild(item);
              });
              searchResults.style.display = 'block';
            } else {
              searchResults.innerHTML = '<div class="p-3 text-muted text-center small">No matching products found</div>';
              searchResults.style.display = 'block';
            }
          })
          .catch(() => {
            searchResults.style.display = 'none';
          });
      }, 300);
    });

    document.addEventListener('click', function(e) {
      if (!globalSearchInput.contains(e.target) && !searchResults.contains(e.target)) {
        searchResults.style.display = 'none';
      }
    });
  }

  // ── 4. Toast Notification Utility ──────────────────────────────────────────
  window.showToast = function(title, message, type = 'success') {
    const toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) return;

    const toastId = 'toast-' + Date.now();
    const bgClass = type === 'success' ? 'bg-success' : type === 'danger' ? 'bg-danger' : 'bg-info';
    
    const toastHTML = `
      <div id="${toastId}" class="toast align-items-center text-white ${bgClass} border-0" role="alert" aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">
            <strong>${title}</strong><br>${message}
          </div>
          <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
      </div>
    `;

    toastContainer.insertAdjacentHTML('beforeend', toastHTML);
    const toastEl = document.getElementById(toastId);
    const bsToast = new bootstrap.Toast(toastEl, { delay: 4000 });
    bsToast.show();

    toastEl.addEventListener('hidden.bs.toast', () => toastEl.remove());
  };

});
