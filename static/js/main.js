/* ═══════════════════════════════════════════════
   ExpenseIQ — main.js
   Dark Mode, Sidebar, Chart.js initialization
═══════════════════════════════════════════════ */

'use strict';

// ── Dark / Light Mode ─────────────────────────
(function initTheme() {
  const saved = localStorage.getItem('expenseiq-theme') || 'light';
  document.documentElement.setAttribute('data-theme', saved);
  updateThemeIcon(saved);
})();

function toggleTheme() {
  const html    = document.documentElement;
  const current = html.getAttribute('data-theme') || 'light';
  const next    = current === 'light' ? 'dark' : 'light';
  html.setAttribute('data-theme', next);
  localStorage.setItem('expenseiq-theme', next);
  updateThemeIcon(next);
}

function updateThemeIcon(theme) {
  const icon = document.getElementById('themeIcon');
  if (!icon) return;
  icon.className = theme === 'dark' ? 'fa-solid fa-sun' : 'fa-solid fa-moon';
}

// ── Sidebar Toggle (mobile) ────────────────────
function toggleSidebar() {
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('sidebarOverlay');
  if (!sidebar) return;
  sidebar.classList.toggle('open');
  overlay && overlay.classList.toggle('show');
}

// ── Chart.js Defaults ─────────────────────────
function applyChartDefaults() {
  if (typeof Chart === 'undefined') return;
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  const textColor = isDark ? '#94a3b8' : '#6b7280';
  const gridColor = isDark ? '#334155' : '#f3f4f6';

  Chart.defaults.font.family = "'Inter', system-ui, sans-serif";
  Chart.defaults.font.size   = 12;
  Chart.defaults.color       = textColor;
  Chart.defaults.plugins.legend.labels.color = textColor;
  Chart.defaults.scale = {
    grid:  { color: gridColor },
    ticks: { color: textColor },
  };
}

// ── Bar Chart (Income vs. Expenses) ───────────
function initBarChart() {
  const canvas = document.getElementById('barChart');
  if (!canvas) return;

  const labels  = window.MONTH_LABELS || [];
  const income  = window.BAR_INCOME   || [];
  const expense = window.BAR_EXPENSE  || [];

  console.log('initBarChart - labels:', labels, 'income:', income, 'expense:', expense);

  if (!labels.length && !income.length && !expense.length) {
    console.warn('No bar chart data available');
    return;
  }

  if (typeof Chart === 'undefined') {
    console.error('Chart.js not loaded');
    return;
  }

  // Destroy existing chart if it exists
  const existingChart = Chart.getChart(canvas);
  if (existingChart) {
    console.log('Destroying existing bar chart');
    existingChart.destroy();
  }

  applyChartDefaults();

  new Chart(canvas, {
    type: 'bar',
    data: {
      labels,
      datasets: [
        {
          label: 'Income',
          data: income,
          backgroundColor: 'rgba(16,185,129,.75)',
          borderRadius: 6,
          borderSkipped: false,
        },
        {
          label: 'Expenses',
          data: expense,
          backgroundColor: 'rgba(239,68,68,.75)',
          borderRadius: 6,
          borderSkipped: false,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend:  { position: 'top', align: 'end' },
        tooltip: {
          callbacks: {
            label: ctx => ` ₹${ctx.formattedValue}`,
          },
        },
      },
      scales: {
        x: { grid: { display: false } },
        y: {
          beginAtZero: true,
          ticks: {
            callback: v => '₹' + v.toLocaleString('en-IN'),
          },
        },
      },
    },
  });
}

// ── Pie Chart (Category distribution) ─────────
function initPieChart() {
  const canvas = document.getElementById('pieChart');
  if (!canvas) {
    console.log('pieChart canvas not found');
    return;
  }

  const labels = window.PIE_LABELS || [];
  const values = window.PIE_VALUES || [];
  const colors = window.PIE_COLORS || [];

  console.log('initPieChart - labels:', labels, 'values:', values);

  if (!values.length) {
    console.warn('No pie chart data available');
    return;
  }

  if (typeof Chart === 'undefined') {
    console.error('Chart.js not loaded for pie chart');
    return;
  }

  // Destroy existing chart if it exists
  const existingChart = Chart.getChart(canvas);
  if (existingChart) {
    console.log('Destroying existing pie chart');
    existingChart.destroy();
  }

  applyChartDefaults();

  new Chart(canvas, {
    type: 'doughnut',
    data: {
      labels,
      datasets: [{
        data: values,
        backgroundColor: colors,
        borderColor: document.documentElement.getAttribute('data-theme') === 'dark' ? '#1e293b' : '#ffffff',
        borderWidth: 3,
        hoverOffset: 6,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '68%',
      plugins: {
        legend: {
          position: 'bottom',
          labels: { padding: 14, usePointStyle: true, pointStyleWidth: 10 },
        },
        tooltip: {
          callbacks: {
            label: ctx => ` ${ctx.label}: ₹${ctx.formattedValue}`,
          },
        },
      },
    },
  });
}

// ── Bootstrap Tooltips ─────────────────────────
function initTooltips() {
  if (typeof bootstrap === 'undefined') return;
  const tips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
  tips.forEach(el => new bootstrap.Tooltip(el));
}

// ── Auto-dismiss alerts ─────────────────────────
function initAlerts() {
  document.querySelectorAll('.alert-dismissible').forEach(function(el) {
    setTimeout(function() { el.style.opacity = '0'; setTimeout(() => el.remove(), 400); }, 5000);
  });
}

// ── DOMContentLoaded ───────────────────────────
document.addEventListener('DOMContentLoaded', function () {
  // Only initialize tooltips and alerts on all pages
  // Charts are initialized on dashboard page separately
  initTooltips();
  initAlerts();

  // Re-apply theme on dynamic content
  document.getElementById('themeToggle')?.addEventListener('click', function () {
    // Charts need a color refresh on theme toggle
    setTimeout(function () {
      document.querySelectorAll('canvas').forEach(function (c) {
        const chartInstance = Chart.getChart(c);
        if (chartInstance) {
          applyChartDefaults();
          chartInstance.update();
        }
      });
    }, 50);
  });
});
