// charts.js – Shared Chart Helpers for Netmon

const MAX_POINTS = 50;
const MAX_LIVE_DURATION = 2 * 60 * 1000; // 2 minutes

// === Utility Functions ===
function getTimestamp() {
  return new Date().toISOString();
}

// === Convert timestamp to date 2025-01-01 15:15:15
function formatDate(timestamp) {
  const date = new Date(timestamp * 1000);
  const yyyy = date.getFullYear();
  const mm = String(date.getMonth() + 1).padStart(2, '0');
  const dd = String(date.getDate()).padStart(2, '0');
  const hh = String(date.getHours()).padStart(2, '0');
  const min = String(date.getMinutes()).padStart(2, '0');
  const ss = String(date.getSeconds()).padStart(2, '0');
  return `${yyyy}-${mm}-${dd} ${hh}:${min}:${ss}`;
}

function getRandomValue(min = 10, max = 60) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

// === Chart Data Helpers ===
function addLivePoint(dataset) {
  dataset.data.push({ x: getTimestamp(), y: getRandomValue() });
  if (dataset.data.length > MAX_POINTS) dataset.data.shift();
}

function preloadData(dataset) {
  for (let i = 10; i > 0; i--) {
    const time = new Date(Date.now() - i * 3000).toISOString();
    dataset.data.push({ x: time, y: getRandomValue() });
  }
}

function preloadChartData(chart, nodeCount = 4) {
  for (let i = 10; i > 0; i--) {
    const t = new Date(Date.now() - i * 3000).toISOString();
    chart.data.labels.push(t);
    for (let j = 0; j < nodeCount; j++) {
      chart.data.datasets[j].data.push(getRandomValue());
    }
  }
  chart.update();
}

// === Download Chart as Image (White Background + Title) ===
function downloadChartWithTitle(chart, filename, title = 'Live Chart') {
  const canvas = chart.canvas;
  const ctx = canvas.getContext('2d');

  const original = ctx.getImageData(0, 0, canvas.width, canvas.height);
  const chartArea = chart.chartArea;

  // White background
  ctx.save();
  ctx.globalCompositeOperation = 'destination-over';
  ctx.fillStyle = '#ffffff';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.restore();

  // Title
  ctx.save();
  ctx.fillStyle = '#212529';
  ctx.font = '16px sans-serif';
  ctx.textAlign = 'left';
  ctx.fillText(title, chartArea.left, chartArea.top - 10);
  ctx.restore();

  // Download
  const link = document.createElement('a');
  link.href = canvas.toDataURL('image/png');
  link.download = filename;
  link.click();

  // Restore
  ctx.putImageData(original, 0, 0);
}

// === Create Chart Config for Mini Static Charts ===
function getMiniChartDefaults() {
  return {
    type: 'line',
    options: {
      responsive: true,
      animation: { duration: 300, easing: 'easeOutQuart' },
      layout: { padding: { right: 12 } },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#212529',
          titleColor: '#fff',
          bodyColor: '#fff',
          borderColor: '#6c757d',
          borderWidth: 1,
          padding: 10
        }
      },
      scales: {
        x: {
          ticks: { maxRotation: 0 },
          grid: { color: '#f0f0f0' }
        },
        y: {
          beginAtZero: true,
          max: 100,
          ticks: { stepSize: 20 },
          grid: { color: '#f0f0f0' }
        }
      },
      elements: {
        point: { radius: 3 }
      }
    }
  };
}

// === Reusable Live Modal Chart Setup ===
/**
 * Sets up a live modal chart (multi-line) with legend, download, restart, and timeout.
 * @param {Object} config
 * Example:
 * setupLiveChartModal({
 *   modalId: 'cpuLoadModal',
 *   canvasId: 'cpuLoadChart',
 *   restartBtnId: 'restartCpuChartBtn',
 *   alertId: 'cpuChartExpiredNotice',
 *   downloadBtnId: 'downloadCpuChartBtn',
 *   chartTitle: 'CUCM CPU Load',
 *   yLabel: 'CPU %',
 *   yMax: 100,
 *   nodeLabels: ['CUCM PUB', 'CUCM SUB1', 'CUCM SUB2', 'IMP PUB', 'IMP SUB']
 * });
 */
function setupLiveChartModal({
  modalId,
  canvasId,
  restartBtnId,
  alertId,
  downloadBtnId,
  chartTitle = 'Live Chart',
  yLabel = 'Value',
  yMax = 100,
  nodeLabels = []
}) {
  const colors = ['#0d6efd', '#198754', '#ffc107', '#dc3545', '#6610f2', '#fd7e14', '#6f42c1', '#20c997'];
  let chart = null;
  let interval = null;
  let timeout = null;

  document.getElementById(modalId).addEventListener('shown.bs.modal', () => {
    if (!chart) {
      const ctx = document.getElementById(canvasId).getContext('2d');

      chart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: [],
          datasets: nodeLabels.map((label, i) => ({
            label,
            data: [],
            borderColor: colors[i % colors.length],
            backgroundColor: colors[i % colors.length] + '20',
            fill: true,
            tension: 0.4,
            pointRadius: 3
          }))
        },
        options: {
          responsive: true,
          animation: { duration: 300, easing: 'easeOutQuart' },
          layout: { padding: { top: 40, right: 12 } },
          plugins: {
            legend: {
              display: true,
              position: 'bottom',
              labels: {
                color: '#333',
                usePointStyle: true,
                boxWidth: 10,
                padding: 16
              }
            },
            tooltip: {
              backgroundColor: '#212529',
              titleColor: '#fff',
              bodyColor: '#fff',
              borderColor: '#6c757d',
              borderWidth: 1,
              padding: 10
            }
          },
          scales: {
            x: {
              type: 'time',
              time: {
                unit: 'second',
                tooltipFormat: 'HH:mm:ss',
                displayFormats: {
                  second: 'HH:mm:ss',
                  minute: 'HH:mm'
                }
              },
              ticks: {
                source: 'data',
                autoSkip: true,
                maxTicksLimit: 5,
                maxRotation: 0,
                color: '#333'
              },
              grid: { color: '#eee' }
            },
            y: {
              beginAtZero: true,
              max: yMax,
              title: { display: true, text: yLabel },
              ticks: { stepSize: 10 },
              grid: { color: '#eee' }
            }
          }
        }
      });

      // preload
      for (let j = 10; j > 0; j--) {
        const t = new Date(Date.now() - j * 3000).toISOString();
        chart.data.labels.push(t);
        chart.data.datasets.forEach(ds => ds.data.push(getRandomValue()));
      }
      chart.update();
    }

    interval = setInterval(() => {
      const now = getTimestamp();
      chart.data.labels.push(now);
      chart.data.labels = chart.data.labels.slice(-MAX_POINTS);
      chart.data.datasets.forEach(ds => {
        ds.data.push(getRandomValue());
        ds.data = ds.data.slice(-MAX_POINTS);
      });
      chart.update('none');
    }, 3000);

    timeout = setTimeout(() => {
      clearInterval(interval);
      document.getElementById(alertId).classList.remove('d-none');
    }, MAX_LIVE_DURATION);
  });

  document.getElementById(modalId).addEventListener('hidden.bs.modal', () => {
    clearInterval(interval);
    clearTimeout(timeout);
    document.getElementById(alertId).classList.add('d-none');
  });

  document.getElementById(restartBtnId).addEventListener('click', () => {
    document.getElementById(alertId).classList.add('d-none');
    interval = setInterval(() => {
      const now = getTimestamp();
      chart.data.labels.push(now);
      chart.data.labels = chart.data.labels.slice(-MAX_POINTS);
      chart.data.datasets.forEach(ds => {
        ds.data.push(getRandomValue());
        ds.data = ds.data.slice(-MAX_POINTS);
      });
      chart.update('none');
    }, 3000);
    timeout = setTimeout(() => {
      clearInterval(interval);
      document.getElementById(alertId).classList.remove('d-none');
    }, MAX_LIVE_DURATION);
  });

  document.getElementById(downloadBtnId).addEventListener('click', () => {
    downloadChartWithTitle(chart, `${canvasId}.png`, chartTitle);
  });
}
