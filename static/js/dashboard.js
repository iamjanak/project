// =========================================================
// SWASTHACARE DASHBOARD
// Real backend data only
// =========================================================

document.addEventListener("DOMContentLoaded", function () {

    initializeAdmissionChart();

    initializeRevenueChart();

    initializeAdmissionStatusChart();

    initializeDepartmentChart();

    initializeOccupancyRing();

});


// =========================================================
// READ DATA
// =========================================================

function readChartData(id) {

    const canvas = document.getElementById(id);

    if (!canvas) {
        return {
            labels: [],
            values: []
        };
    }

    let labels = [];
    let values = [];

    try {

        labels = JSON.parse(
            canvas.dataset.labels || "[]"
        );

        values = JSON.parse(
            canvas.dataset.values || "[]"
        );

    } catch (error) {

        console.error(
            "Dashboard chart data error:",
            error
        );

    }

    return {
        canvas,
        labels,
        values
    };
}


// =========================================================
// COMMON OPTIONS
// =========================================================

function commonChartOptions() {

    return {

        responsive: true,

        maintainAspectRatio: false,

        interaction: {
            intersect: false,
            mode: "index"
        },

        plugins: {

            legend: {
                display: false
            },

            tooltip: {

                padding: 12,

                cornerRadius: 8,

                displayColors: false

            }

        },

        scales: {

            x: {

                grid: {
                    display: false
                },

                ticks: {
                    color: "#7c879c",
                    font: {
                        size: 11
                    }
                }

            },

            y: {

                beginAtZero: true,

                grid: {
                    color: "#edf1f6"
                },

                ticks: {
                    color: "#7c879c",
                    font: {
                        size: 11
                    }
                }

            }

        }

    };

}


// =========================================================
// ADMISSION CHART
// =========================================================

function initializeAdmissionChart() {

    const data = readChartData(
        "admissionChart"
    );

    if (!data.canvas) {
        return;
    }

    const ctx = data.canvas.getContext(
        "2d"
    );

    const gradient = ctx.createLinearGradient(
        0,
        0,
        0,
        300
    );

    gradient.addColorStop(
        0,
        "rgba(42, 105, 218, 0.22)"
    );

    gradient.addColorStop(
        1,
        "rgba(42, 105, 218, 0)"
    );


    new Chart(
        data.canvas,
        {

            type: "line",

            data: {

                labels: data.labels,

                datasets: [

                    {

                        label: "Admissions",

                        data: data.values,

                        borderColor: "#2a69da",

                        backgroundColor: gradient,

                        borderWidth: 2.5,

                        pointRadius: 3,

                        pointHoverRadius: 6,

                        pointBackgroundColor: "#ffffff",

                        pointBorderWidth: 2,

                        tension: 0.35,

                        fill: true

                    }

                ]

            },

            options: commonChartOptions()

        }
    );

}


// =========================================================
// REVENUE CHART
// =========================================================

function initializeRevenueChart() {

    const data = readChartData(
        "revenueChart"
    );

    if (!data.canvas) {
        return;
    }


    new Chart(
        data.canvas,
        {

            type: "bar",

            data: {

                labels: data.labels,

                datasets: [

                    {

                        label: "Revenue",

                        data: data.values,

                        backgroundColor:
                            "rgba(32, 154, 112, 0.78)",

                        borderRadius: 5,

                        maxBarThickness: 30

                    }

                ]

            },

            options: {

                ...commonChartOptions(),

                plugins: {

                    legend: {
                        display: false
                    },

                    tooltip: {

                        callbacks: {

                            label: function (
                                context
                            ) {

                                return (
                                    " Rs. " +
                                    Number(
                                        context.raw || 0
                                    ).toLocaleString(
                                        "en-IN",
                                        {
                                            minimumFractionDigits: 2
                                        }
                                    )
                                );

                            }

                        }

                    }

                },

                scales: {

                    x: {

                        grid: {
                            display: false
                        }

                    },

                    y: {

                        beginAtZero: true,

                        grid: {
                            color: "#edf1f6"
                        },

                        ticks: {

                            callback:
                                function (value) {

                                    return "Rs. " +
                                        Number(
                                            value
                                        ).toLocaleString(
                                            "en-IN"
                                        );

                                }

                        }

                    }

                }

            }

        }
    );

}


// =========================================================
// ADMISSION STATUS DONUT
// =========================================================

function initializeAdmissionStatusChart() {

    const data = readChartData(
        "admissionStatusChart"
    );

    if (!data.canvas) {
        return;
    }


    new Chart(
        data.canvas,
        {

            type: "doughnut",

            data: {

                labels: data.labels,

                datasets: [

                    {

                        data: data.values,

                        backgroundColor: [
                            "#2a69da",
                            "#209a70",
                            "#aeb8c7"
                        ],

                        borderWidth: 0,

                        hoverOffset: 6

                    }

                ]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                cutout: "72%",

                plugins: {

                    legend: {
                        display: false
                    },

                    tooltip: {

                        padding: 12,

                        cornerRadius: 8

                    }

                }

            }

        }
    );


    const legend =
        document.getElementById(
            "admissionStatusLegend"
        );

    if (!legend) {
        return;
    }


    const colors = [
        "#2a69da",
        "#209a70",
        "#aeb8c7"
    ];


    legend.innerHTML =
        data.labels.map(
            function (label, index) {

                return `

                    <div class="sc-legend-item">

                        <span
                            class="sc-legend-dot"
                            style="
                                background:${colors[index]};
                            "
                        ></span>

                        <span>
                            ${label}
                        </span>

                        <strong>
                            ${data.values[index] || 0}
                        </strong>

                    </div>

                `;

            }
        ).join("");

}


// =========================================================
// DEPARTMENT CHART
// =========================================================

function initializeDepartmentChart() {

    const data = readChartData(
        "departmentChart"
    );

    if (!data.canvas) {
        return;
    }


    new Chart(
        data.canvas,
        {

            type: "bar",

            data: {

                labels: data.labels,

                datasets: [

                    {

                        label: "Patients",

                        data: data.values,

                        backgroundColor:
                            "rgba(91, 91, 214, 0.78)",

                        borderRadius: 6,

                        maxBarThickness: 32

                    }

                ]

            },

            options: {

                indexAxis: "y",

                responsive: true,

                maintainAspectRatio: false,

                plugins: {

                    legend: {
                        display: false
                    },

                    tooltip: {

                        padding: 12,

                        cornerRadius: 8,

                        displayColors: false

                    }

                },

                scales: {

                    x: {

                        beginAtZero: true,

                        grid: {
                            color: "#edf1f6"
                        },

                        ticks: {
                            color: "#7c879c"
                        }

                    },

                    y: {

                        grid: {
                            display: false
                        },

                        ticks: {
                            color: "#4f5b70",
                            font: {
                                size: 11,
                                weight: "600"
                            }
                        }

                    }

                }

            }

        }
    );

}


// =========================================================
// BED OCCUPANCY RING
// =========================================================

function initializeOccupancyRing() {

    const ring =
        document.querySelector(
            ".sc-progress-ring"
        );

    if (!ring) {
        return;
    }


    let value = parseFloat(
        ring.dataset.value || 0
    );


    value = Math.max(
        0,
        Math.min(
            100,
            value
        )
    );


    ring.style.setProperty(
        "--occupancy",
        value + "%"
    );

}