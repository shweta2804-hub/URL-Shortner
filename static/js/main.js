/* ============================================================
   URL Shortener - Main Application Script
   Modern SaaS Frontend with API integration
   ============================================================ */

// ============================================================
// 1. DARK MODE TOGGLE
// ============================================================
(function initTheme() {
  const savedTheme = localStorage.getItem('theme') || 'light';
  document.documentElement.setAttribute('data-theme', savedTheme);
})();

function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme');
  const next = current === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  localStorage.setItem('theme', next);

  // Update toggle icon
  const toggle = document.querySelector('.theme-toggle i');
  if (toggle) {
    toggle.className = next === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-fill';
  }
}

// ============================================================
// 2. TOAST NOTIFICATION SYSTEM
// ============================================================
function showToast(message, type = 'success') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const icons = {
    success: 'bi bi-check-circle-fill',
    error: 'bi bi-x-circle-fill',
    warning: 'bi bi-exclamation-triangle-fill',
    info: 'bi bi-info-circle-fill'
  };

  const toast = document.createElement('div');
  toast.className = `toast-custom toast-${type}`;
  toast.innerHTML = `
    <span class="toast-icon"><i class="${icons[type] || icons.info}"></i></span>
    <span>${message}</span>
    <button class="toast-close" onclick="this.parentElement.remove()">&times;</button>
  `;

  container.appendChild(toast);

  // Auto-remove after 4 seconds
  setTimeout(() => {
    if (toast.parentElement) {
      toast.style.animation = 'slideOutRight 0.3s ease forwards';
      setTimeout(() => toast.remove(), 300);
    }
  }, 4000);
}

// ============================================================
// 3. PASSWORD STRENGTH INDICATOR
// ============================================================
function checkPasswordStrength(password) {
  let score = 0;
  let label = '';
  let color = '';

  if (password.length >= 6) score += 20;
  if (password.length >= 10) score += 15;
  if (/[a-z]/.test(password)) score += 15;
  if (/[A-Z]/.test(password)) score += 20;
  if (/[0-9]/.test(password)) score += 15;
  if (/[^a-zA-Z0-9]/.test(password)) score += 15;

  if (score < 25) { label = 'Weak'; color = '#ef4444'; }
  else if (score < 50) { label = 'Fair'; color = '#f59e0b'; }
  else if (score < 70) { label = 'Good'; color = '#06b6d4'; }
  else { label = 'Strong'; color = '#10b981'; }

  return { score, label, color };
}

function updatePasswordStrength(inputId = 'password') {
  const input = document.getElementById(inputId);
  const barFill = document.querySelector('.strength-bar-fill');
  const text = document.querySelector('.strength-text');
  if (!input || !barFill || !text) return;

  const result = checkPasswordStrength(input.value);
  const maxScore = 100;
  const percentage = Math.min((result.score / maxScore) * 100, 100);

  barFill.style.width = percentage + '%';
  barFill.style.background = result.color;
  text.textContent = result.label;
  text.style.color = result.color;
}

// ============================================================
// 4. FORM VALIDATION
// ============================================================
function validateField(input) {
  const value = input.value.trim();
  const feedback = input.parentElement.querySelector('.invalid-feedback');
  if (!feedback) return true;

  let valid = true;
  let message = '';

  if (input.required && !value) {
    valid = false;
    message = 'This field is required';
  } else if (input.type === 'email' && value) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(value)) {
      valid = false;
      message = 'Please enter a valid email address';
    }
  } else if (input.id === 'password' && value && value.length < 6) {
    valid = false;
    message = 'Password must be at least 6 characters';
  } else if (input.id === 'confirm_password' && value) {
    const password = document.getElementById('password');
    if (password && value !== password.value) {
      valid = false;
      message = 'Passwords do not match';
    }
  }

  input.classList.toggle('is-invalid', !valid && value !== '');
  input.classList.toggle('is-valid', valid && value !== '');
  feedback.textContent = message;
  return valid;
}

// ============================================================
// 5. AUTH (LOGIN / REGISTER)
// ============================================================
function handleLogin(event) {
  event.preventDefault();
  const form = event.target;
  const email = form.querySelector('[name="email"]').value.trim();
  const password = form.querySelector('[name="password"]').value.trim();

  if (!email || !password) {
    showToast('Please fill in all fields', 'error');
    return;
  }

  const submitBtn = form.querySelector('button[type="submit"]');
  submitBtn.disabled = true;
  submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span> Signing in...';

  fetch('/api/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  })
  .then(res => res.json())
  .then(data => {
    if (data.token) {
      localStorage.setItem('token', data.token);
      localStorage.setItem('user', JSON.stringify(data.user));
      showToast('Welcome back! Redirecting...', 'success');
      setTimeout(() => { window.location.href = '/dashboard'; }, 800);
    } else {
      showToast(data.error || 'Invalid credentials', 'error');
      submitBtn.disabled = false;
      submitBtn.textContent = 'Sign In';
    }
  })
  .catch(err => {
    showToast('Connection error. Please try again.', 'error');
    submitBtn.disabled = false;
    submitBtn.textContent = 'Sign In';
  });
}

function handleRegister(event) {
  event.preventDefault();
  const form = event.target;
  const username = form.querySelector('[name="username"]').value.trim();
  const email = form.querySelector('[name="email"]').value.trim();
  const password = form.querySelector('[name="password"]').value.trim();

  if (!username || !email || !password) {
    showToast('Please fill in all fields', 'error');
    return;
  }

  if (password.length < 6) {
    showToast('Password must be at least 6 characters', 'error');
    return;
  }

  const submitBtn = form.querySelector('button[type="submit"]');
  submitBtn.disabled = true;
  submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span> Creating account...';

  fetch('/api/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, email, password })
  })
  .then(res => res.json())
  .then(data => {
    if (data.token) {
      localStorage.setItem('token', data.token);
      localStorage.setItem('user', JSON.stringify(data.user));
      showToast('Account created successfully!', 'success');
      setTimeout(() => { window.location.href = '/dashboard'; }, 1000);
    } else {
      const msg = data.details ? data.details.join(', ') : data.error;
      showToast(msg || 'Registration failed', 'error');
      submitBtn.disabled = false;
      submitBtn.textContent = 'Create Account';
    }
  })
  .catch(err => {
    showToast('Connection error. Please try again.', 'error');
    submitBtn.disabled = false;
    submitBtn.textContent = 'Create Account';
  });
}

// ============================================================
// 6. DASHBOARD API
// ============================================================
function getToken() {
  return localStorage.getItem('token');
}

function getAuthHeaders() {
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${getToken()}`
  };
}

// Load user profile & stats
function loadDashboard() {
  const token = getToken();
  if (!token) {
    window.location.href = '/';
    return;
  }

  // Set user name
  try {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    const nameEl = document.getElementById('user-name');
    if (nameEl && user.username) nameEl.textContent = user.username;
    const greetingEl = document.getElementById('user-greeting');
    if (greetingEl && user.username) greetingEl.textContent = user.username;
  } catch(e) {}

  // Load stats
  fetch('/api/profile', { headers: getAuthHeaders() })
    .then(res => res.json())
    .then(data => {
      if (data.stats) {
        document.getElementById('total-urls').textContent = data.stats.total_urls || 0;
        document.getElementById('total-clicks').textContent = data.stats.total_clicks || 0;
        document.getElementById('top-url').textContent = data.stats.top_url || 'N/A';
        document.getElementById('avg-clicks').textContent = data.stats.avg_clicks || 0;
      }
    })
    .catch(() => {});

  // Load URLs
  loadUrls();
}

// Load URL list
function loadUrls() {
  fetch('/api/urls', { headers: getAuthHeaders() })
    .then(res => res.json())
    .then(data => {
      const container = document.getElementById('url-table-body');
      const emptyState = document.getElementById('empty-state');
      const table = document.getElementById('url-table');

      if (!container) return;

      container.innerHTML = '';

      if (!data.urls || data.urls.length === 0) {
        if (emptyState) emptyState.style.display = 'block';
        if (table) table.style.display = 'none';
        return;
      }

      if (emptyState) emptyState.style.display = 'none';
      if (table) table.style.display = '';

      // Update URL count stat
      document.getElementById('total-urls').textContent = data.urls.length;

      data.urls.forEach(url => {
        const shortUrl = `${window.location.origin}/${url.short_code}`;
        const created = new Date(url.created_at).toLocaleDateString('en-US', {
          year: 'numeric', month: 'short', day: 'numeric'
        });

        const row = document.createElement('tr');
        row.innerHTML = `
          <td><div class="url-cell" title="${escapeHtml(url.original_url)}">${escapeHtml(url.original_url)}</div></td>
          <td><code style="color: var(--accent-primary); font-size: 0.85rem;">${shortUrl}</code></td>
          <td><span class="badge-click"><i class="bi bi-eye me-1"></i>${url.clicks || 0}</span></td>
          <td style="color: var(--text-secondary); font-size: 0.85rem;">${created}</td>
          <td>
            <div class="d-flex gap-1">
              <button class="btn-icon" title="Copy short URL" onclick="copyToClipboard('${shortUrl}', this)">
                <i class="bi bi-files"></i>
              </button>
              <button class="btn-icon" title="Delete URL" onclick="confirmDelete(${url.id})" style="color: var(--accent-danger);">
                <i class="bi bi-trash3"></i>
              </button>
            </div>
          </td>
        `;
        container.appendChild(row);
      });
    })
    .catch(() => {});
}

// Shorten URL
function shortenUrl() {
  const input = document.getElementById('url-input');
  const url = input.value.trim();
  const btn = document.getElementById('shorten-btn');

  if (!url) {
    showToast('Please enter a URL', 'error');
    input.focus();
    return;
  }

  if (!url.startsWith('http://') && !url.startsWith('https://')) {
    showToast('URL must start with http:// or https://', 'error');
    input.focus();
    return;
  }

  btn.disabled = true;
  btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span> Shortening...';

  fetch('/api/shorten', {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ url })
  })
  .then(res => res.json())
  .then(data => {
    btn.disabled = false;
    btn.innerHTML = '<i class="bi bi-link-45deg me-2"></i>Shorten URL';

    if (data.url) {
      input.value = '';
      showToast('URL shortened successfully!', 'success');
      loadUrls();
      loadDashboard();
    } else {
      showToast(data.error || 'Failed to shorten URL', 'error');
    }
  })
  .catch(() => {
    btn.disabled = false;
    btn.innerHTML = '<i class="bi bi-link-45deg me-2"></i>Shorten URL';
    showToast('Connection error. Please try again.', 'error');
  });
}

// ============================================================
// 7. CLIPBOARD (Copy to Clipboard)
// ============================================================
function copyToClipboard(text, btnElement) {
  navigator.clipboard.writeText(text).then(() => {
    if (btnElement) {
      const icon = btnElement.querySelector('i');
      if (icon) {
        const originalClass = icon.className;
        icon.className = 'bi bi-check-lg';
        btnElement.classList.add('copied');
        setTimeout(() => {
          icon.className = originalClass;
          btnElement.classList.remove('copied');
        }, 1500);
      }
    }
    showToast('Copied to clipboard!', 'success');
  }).catch(() => {
    // Fallback
    const textarea = document.createElement('textarea');
    textarea.value = text;
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand('copy');
    document.body.removeChild(textarea);
    showToast('Copied to clipboard!', 'success');
  });
}

// ============================================================
// 8. DELETE CONFIRMATION
// ============================================================
function confirmDelete(urlId) {
  // Remove existing overlay
  const existing = document.querySelector('.delete-confirm-overlay');
  if (existing) existing.remove();

  const overlay = document.createElement('div');
  overlay.className = 'delete-confirm-overlay';
  overlay.innerHTML = `
    <div class="delete-confirm-box">
      <div class="delete-icon"><i class="bi bi-exclamation-triangle-fill"></i></div>
      <h5>Delete URL?</h5>
      <p>This action cannot be undone. The short link will stop working.</p>
      <div class="delete-actions">
        <button class="btn btn-ghost" onclick="this.closest('.delete-confirm-overlay').remove()">Cancel</button>
        <button class="btn btn-primary" style="background: var(--accent-danger); box-shadow: none;" onclick="deleteUrl(${urlId})">
          <i class="bi bi-trash3 me-2"></i>Delete
        </button>
      </div>
    </div>
  `;
  document.body.appendChild(overlay);
}

function deleteUrl(urlId) {
  // Close overlay
  const overlay = document.querySelector('.delete-confirm-overlay');
  if (overlay) overlay.remove();

  fetch(`/api/urls/${urlId}`, {
    method: 'DELETE',
    headers: getAuthHeaders()
  })
  .then(res => {
    if (res.ok) {
      showToast('URL deleted successfully', 'success');
      loadUrls();
      loadDashboard();
    } else {
      showToast('Failed to delete URL', 'error');
    }
  })
  .catch(() => {
    showToast('Connection error', 'error');
  });
}

// ============================================================
// 9. LOGOUT
// ============================================================
function logout() {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  window.location.href = '/';
}

// ============================================================
// 10. UTILITY: Escape HTML
// ============================================================
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// ============================================================
// 11. INIT
// ============================================================
document.addEventListener('DOMContentLoaded', function() {
  // Auto-init toast container
  if (!document.getElementById('toast-container')) {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  // Password strength listeners
  const pwInput = document.getElementById('password');
  if (pwInput) {
    pwInput.addEventListener('input', function() {
      updatePasswordStrength('password');
    });
  }

  // Confirm password validation
  const confirmPw = document.getElementById('confirm_password');
  if (confirmPw) {
    confirmPw.addEventListener('input', function() {
      validateField(this);
    });
  }

  // Auto-validate form inputs on blur
  document.querySelectorAll('.needs-validation input').forEach(input => {
    input.addEventListener('blur', function() { validateField(this); });
  });

  // Theme toggle from localStorage
  const theme = localStorage.getItem('theme') || 'light';
  const toggle = document.querySelector('.theme-toggle i');
  if (toggle) {
    toggle.className = theme === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-fill';
  }

  // Dashboard specific
  if (window.location.pathname === '/dashboard') {
    loadDashboard();

    // Enter key to shorten
    const urlInput = document.getElementById('url-input');
    if (urlInput) {
      urlInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
          e.preventDefault();
          shortenUrl();
        }
      });
    }
  }
});