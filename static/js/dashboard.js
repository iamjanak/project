// Patient Statistics — bar chart
const patientCtx = document.getElementById('patientStatsChart');
if (patientCtx) {
  new Chart(patientCtx, {
    type: 'bar',
    data: {
      labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
      datasets: [{
        data: [300, 220, 600, 320, 150],
        backgroundColor: (ctx) => ctx.dataIndex === 2 ? '#6c5ce7' : '#efeaff',
        borderRadius: 8,
        maxBarThickness: 40,
      }]
    },
    options: {
      plugins: { legend: { display: false }, tooltip: { enabled: true } },
      scales: {
        y: { beginAtZero: true, grid: { color: '#f0f0f5' }, ticks: { stepSize: 100 } },
        x: { grid: { display: false } }
      }
    }
  });
}

// Total Revenue — grouped bar chart (Income / Expense / Other)
const revenueCtx = document.getElementById('revenueChart');
if (revenueCtx) {
  new Chart(revenueCtx, {
    type: 'bar',
    data: {
      labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
      datasets: [
        {
          label: 'Income',
          data: [140473, 200000, 250000, 342200, 500000, 700000, 830451],
          backgroundColor: '#1e2a4a',
          borderRadius: 6,
          stack: 'a'
        },
        {
          label: 'Expense',
          data: [60000, 80000, 90000, 100000, 120000, 150000, 180000],
          backgroundColor: '#6c5ce7',
          borderRadius: 6,
          stack: 'a'
        },
        {
          label: 'Other',
          data: [20000, 25000, 30000, 35000, 40000, 45000, 50000],
          backgroundColor: '#c9c2f7',
          borderRadius: 6,
          stack: 'a'
        }
      ]
    },
    options: {
      plugins: { legend: { display: false } },
      scales: {
        y: { display: false, stacked: true },
        x: { stacked: true, grid: { display: false } }
      }
    }
  });
}