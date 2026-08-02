// ==========================================================
// Hospital Admin Dashboard — revenue chart
// Renders the bar chart and pins the "Revenue 90k" callout
// exactly above the highlighted bar, using Chart.js's own
// computed bar coordinates (so it stays aligned on resize).
// ==========================================================

document.addEventListener('DOMContentLoaded', function () {

    const hdCtx = document.getElementById('hospitalRevenueChart');
    if (!hdCtx) return;

    // TODO: swap this for real data passed from the backend,
    // e.g. render it into a data-* attribute on the canvas and
    // read it here with JSON.parse(hdCtx.dataset.values).
    const hdValues = [42, 65, 46, 55, 40, 90, 58, 48];
    const hdHighlightIndex = hdValues.indexOf(Math.max(...hdValues));

    const hdChart = new Chart(hdCtx, {
        type: 'bar',
        data: {
            labels: ['01', '02', '03', '04', '05', '06', '07', '08'],
            datasets: [{
                data: hdValues,
                backgroundColor: hdValues.map((_, i) =>
                    i === hdHighlightIndex ? '#6c5ce7' : '#e6e1fb'
                ),
                borderRadius: 8,
                maxBarThickness: 34,
            }]
        },
        options: {
            plugins: {
                legend: { display: false },
                tooltip: { enabled: false }
            },
            scales: {
                y: { display: false, beginAtZero: true },
                x: {
                    grid: { display: false },
                    ticks: { color: '#8a8a99', font: { size: 11 } }
                }
            },
            animation: {
                onComplete: positionCallout
            },
            onResize: () => requestAnimationFrame(positionCallout)
        }
    });

    function positionCallout() {
        const callout = document.getElementById('hdChartCallout');
        if (!callout) return;

        const meta = hdChart.getDatasetMeta(0).data[hdHighlightIndex];
        if (!meta) return;

        callout.style.left = `${meta.x}px`;
        callout.style.top = `${meta.y - 14}px`;

        const valueEl = callout.querySelector('.hd-callout-value');
        if (valueEl) valueEl.textContent = `${hdValues[hdHighlightIndex]}k`;
    }

});