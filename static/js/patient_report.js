"use strict";


/* =========================================================
   INITIALIZE
========================================================= */

function initPatientReport() {

    const searchButton =
        document.getElementById(
            "searchReportBtn"
        );

    const clearButton =
        document.getElementById(
            "clearReportBtn"
        );

    const printButton =
        document.getElementById(
            "printReportBtn"
        );


    if (
        searchButton &&
        searchButton.dataset.initialized !== "true"
    ) {

        searchButton.addEventListener(
            "click",
            function () {

                loadPatientReport();

            }
        );

        searchButton.dataset.initialized = "true";

    }


    if (
        clearButton &&
        clearButton.dataset.initialized !== "true"
    ) {

        clearButton.addEventListener(
            "click",
            function () {

                clearPatientReport();

            }
        );

        clearButton.dataset.initialized = "true";

    }


    if (
        printButton &&
        printButton.dataset.initialized !== "true"
    ) {

        printButton.addEventListener(
            "click",
            function () {

                window.print();

            }
        );

        printButton.dataset.initialized = "true";

    }

}


/* =========================================================
   PAGE LOAD
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    initPatientReport
);


if (document.readyState !== "loading") {

    initPatientReport();

}


/* =========================================================
   LOAD PATIENT REPORT
========================================================= */

async function loadPatientReport() {

    const tableBody =
        document.getElementById(
            "patientReportBody"
        );


    if (!tableBody) {

        return;

    }


    const patientNo =
        document.getElementById(
            "patientNo"
        )?.value.trim() || "";


    const patientName =
        document.getElementById(
            "patientName"
        )?.value.trim() || "";


    const phone =
        document.getElementById(
            "phone"
        )?.value.trim() || "";


    const department =
        document.getElementById(
            "department"
        )?.value || "";


    const doctor =
        document.getElementById(
            "doctor"
        )?.value || "";


    const params =
        new URLSearchParams();


    if (patientNo) {

        params.append(
            "patient_no",
            patientNo
        );

    }


    if (patientName) {

        params.append(
            "patient_name",
            patientName
        );

    }


    if (phone) {

        params.append(
            "phone",
            phone
        );

    }


    if (department) {

        params.append(
            "department",
            department
        );

    }


    if (doctor) {

        params.append(
            "doctor",
            doctor
        );

    }


    tableBody.innerHTML = `
        <tr>
            <td
                colspan="10"
                class="report-loading"
            >
                Loading patient records...
            </td>
        </tr>
    `;


    try {

        const url =
            `/patient_report/fetch?${params.toString()}`;


        const response =
            await fetch(
                url,
                {
                    method: "GET",

                    headers: {
                        "Accept":
                            "application/json"
                    },

                    credentials:
                        "same-origin",

                    cache:
                        "no-store"
                }
            );


        const responseText =
            await response.text();


        let data;


        try {

            data =
                JSON.parse(responseText);

        } catch (error) {

            throw new Error(
                `Server returned HTTP ${response.status}.`
            );

        }


        if (!response.ok || !data.success) {

            throw new Error(
                data.message ||
                "Unable to load patient report."
            );

        }


        renderPatientReport(
            data.patients || []
        );


    } catch (error) {

        console.error(
            "Patient report error:",
            error
        );


        tableBody.innerHTML = `
            <tr>
                <td
                    colspan="10"
                    class="report-empty"
                >
                    ${escapeHtml(
                        error.message ||
                        "Unable to load patient report."
                    )}
                </td>
            </tr>
        `;

    }

}


/* =========================================================
   RENDER REPORT
========================================================= */

function renderPatientReport(
    patients
) {

    const tableBody =
        document.getElementById(
            "patientReportBody"
        );

    const totalPatients =
        document.getElementById(
            "totalPatients"
        );


    if (!tableBody) {

        return;

    }


    if (totalPatients) {

        totalPatients.textContent =
            patients.length;

    }


    if (
        !patients ||
        patients.length === 0
    ) {

        tableBody.innerHTML = `
            <tr>
                <td
                    colspan="10"
                    class="report-empty"
                >
                    No patient records found.
                </td>
            </tr>
        `;

        return;

    }


    tableBody.innerHTML = "";


    patients.forEach(
        function (patient, index) {

            const row =
                document.createElement(
                    "tr"
                );


            row.innerHTML = `

                <td>
                    ${index + 1}
                </td>

                <td>
                    ${escapeHtml(
                        patient.patient_no || "—"
                    )}
                </td>

                <td>
                    ${escapeHtml(
                        patient.full_name || "—"
                    )}
                </td>

                <td>
                    ${escapeHtml(
                        patient.dob || "—"
                    )}
                </td>

                <td>
                    ${escapeHtml(
                        patient.age ?? "—"
                    )}
                </td>

                <td>
                    ${escapeHtml(
                        patient.gender || "—"
                    )}
                </td>

                <td>
                    ${escapeHtml(
                        patient.phone || "—"
                    )}
                </td>

                <td>
                    ${escapeHtml(
                        patient.department || "—"
                    )}
                </td>

                <td>
                    ${escapeHtml(
                        patient.doctor || "—"
                    )}
                </td>

                <td>
                    ${escapeHtml(
                        patient.created_at || "—"
                    )}
                </td>

            `;


            tableBody.appendChild(
                row
            );

        }
    );

}


/* =========================================================
   CLEAR REPORT
========================================================= */

function clearPatientReport() {

    const fields = [

        "patientNo",
        "patientName",
        "phone",
        "department",
        "doctor"

    ];


    fields.forEach(
        function (id) {

            const element =
                document.getElementById(
                    id
                );


            if (element) {

                element.value = "";

            }

        }
    );


    const totalPatients =
        document.getElementById(
            "totalPatients"
        );


    if (totalPatients) {

        totalPatients.textContent =
            "0";

    }


    const tableBody =
        document.getElementById(
            "patientReportBody"
        );


    if (tableBody) {

        tableBody.innerHTML = `
            <tr>
                <td
                    colspan="10"
                    class="report-empty"
                >
                    Search patient records to view the report.
                </td>
            </tr>
        `;

    }

}


/* =========================================================
   ESCAPE HTML
========================================================= */

function escapeHtml(
    value
) {

    return String(value)
        .replaceAll(
            "&",
            "&amp;"
        )
        .replaceAll(
            "<",
            "&lt;"
        )
        .replaceAll(
            ">",
            "&gt;"
        )
        .replaceAll(
            '"',
            "&quot;"
        )
        .replaceAll(
            "'",
            "&#039;"
        );

}