
/* =========================================================
   BILLING REPORTS
   SwasthaCare
========================================================= */


/* =========================================================
   LOAD BILLING REPORT
========================================================= */

async function loadBillingReport() {

    const searchButton =
        document.querySelector(".btn-search");

    try {

        /* -------------------------------------------------
           Disable button while loading
        ------------------------------------------------- */

        if (searchButton) {
            searchButton.disabled = true;
            searchButton.textContent = "Searching...";
        }


        /* -------------------------------------------------
           Get filter values
        ------------------------------------------------- */

        const startDate =
            document.getElementById("start_date")?.value || "";

        const endDate =
            document.getElementById("end_date")?.value || "";

        const hospitalNo =
            document.getElementById("hospital_no")?.value.trim() || "";

        const billNo =
            document.getElementById("bill_no")?.value.trim() || "";

        const patientName =
            document.getElementById("patient_name")?.value.trim() || "";

        const paymentType =
            document.getElementById("payment_type")?.value || "";


        /* -------------------------------------------------
           Build API URL
        ------------------------------------------------- */

        const params = new URLSearchParams();

        if (startDate) {
            params.append("start_date", startDate);
        }

        if (endDate) {
            params.append("end_date", endDate);
        }

        if (hospitalNo) {
            params.append("hospital_no", hospitalNo);
        }

        if (billNo) {
            params.append("bill_no", billNo);
        }

        if (patientName) {
            params.append("patient_name", patientName);
        }

        if (paymentType) {
            params.append("payment_type", paymentType);
        }


        /* -------------------------------------------------
           API request
        ------------------------------------------------- */

        const response = await fetch(
            `/billing-reports/data?${params.toString()}`,
            {
                method: "GET",
                headers: {
                    "Accept": "application/json"
                }
            }
        );


        /* -------------------------------------------------
           Check HTTP response
        ------------------------------------------------- */

        if (!response.ok) {

            throw new Error(
                `Server returned ${response.status}`
            );
        }


        const data = await response.json();


        /* -------------------------------------------------
           Backend error
        ------------------------------------------------- */

        if (!data.success) {

            throw new Error(
                data.message ||
                "Unable to load billing report."
            );
        }


        /* -------------------------------------------------
           Update summary
        ------------------------------------------------- */

        updateBillingSummary(
            data.summary
        );


        /* -------------------------------------------------
           Update tables
        ------------------------------------------------- */

        renderBills(
            data.bills || []
        );

        renderRefunds(
            data.refunds || []
        );

        renderDeposits(
            data.deposits || []
        );


    } catch (error) {

        console.error(
            "Billing Report Error:",
            error
        );

        alert(
            "Unable to connect to server.\n\n" +
            error.message
        );

    } finally {

        if (searchButton) {

            searchButton.disabled = false;

            searchButton.textContent = "Search";
        }
    }
}


/* =========================================================
   SEARCH BUTTON
========================================================= */

function searchBillingReport() {

    loadBillingReport();
}


/* =========================================================
   UPDATE SUMMARY
========================================================= */

function updateBillingSummary(summary) {

    summary = summary || {};

    setText(
        "total_bills",
        formatNumber(
            summary.total_bills || 0,
            0
        )
    );

    setText(
        "gross_billing",
        formatAmount(
            summary.gross_billing
        )
    );

    setText(
        "discount",
        formatAmount(
            summary.discount
        )
    );

    setText(
        "net_billing",
        formatAmount(
            summary.net_billing
        )
    );

    setText(
        "total_refund",
        formatAmount(
            summary.total_refund
        )
    );

    setText(
        "net_revenue",
        formatAmount(
            summary.net_revenue
        )
    );
}


/* =========================================================
   RENDER BILL TABLE
========================================================= */

function renderBills(bills) {

    const tbody =
        document.getElementById(
            "billing_table_body"
        );

    if (!tbody) {
        return;
    }


    if (!bills.length) {

        tbody.innerHTML = `
            <tr>
                <td colspan="11" class="empty-row">
                    No billing records found.
                </td>
            </tr>
        `;

        return;
    }


    tbody.innerHTML = bills.map(
        (bill, index) => {

            return `
                <tr>

                    <td>${index + 1}</td>

                    <td>
                        ${escapeHtml(
                            bill.bill_no
                        )}
                    </td>

                    <td>
                        ${escapeHtml(
                            bill.date
                        )}
                    </td>

                    <td>
                        ${escapeHtml(
                            bill.time
                        )}
                    </td>

                    <td>
                        ${escapeHtml(
                            bill.hospital_no
                        )}
                    </td>

                    <td>
                        ${escapeHtml(
                            bill.patient_name
                        )}
                    </td>

                    <td>
                        ${escapeHtml(
                            bill.department
                        )}
                    </td>

                    <td>
                        ${formatAmount(
                            bill.subtotal
                        )}
                    </td>

                    <td>
                        ${formatAmount(
                            bill.discount
                        )}
                    </td>

                    <td>
                        ${formatAmount(
                            bill.total
                        )}
                    </td>

                    <td>
                        ${escapeHtml(
                            bill.payment_type
                        )}
                    </td>

                </tr>
            `;
        }
    ).join("");
}


/* =========================================================
   RENDER REFUNDS
========================================================= */

function renderRefunds(refunds) {

    const tbody =
        document.getElementById(
            "refund_table_body"
        );

    if (!tbody) {
        return;
    }


    if (!refunds.length) {

        tbody.innerHTML = `
            <tr>
                <td colspan="9" class="empty-row">
                    No refund records found.
                </td>
            </tr>
        `;

        return;
    }


    tbody.innerHTML = refunds.map(
        (refund, index) => {

            return `
                <tr>

                    <td>${index + 1}</td>

                    <td>
                        ${escapeHtml(
                            refund.refund_no
                        )}
                    </td>

                    <td>
                        ${escapeHtml(
                            refund.bill_no
                        )}
                    </td>

                    <td>
                        ${escapeHtml(
                            refund.date
                        )}
                    </td>

                    <td>
                        ${escapeHtml(
                            refund.hospital_no
                        )}
                    </td>

                    <td>
                        ${escapeHtml(
                            refund.patient_name
                        )}
                    </td>

                    <td>
                        ${formatAmount(
                            refund.bill_amount
                        )}
                    </td>

                    <td>
                        ${formatAmount(
                            refund.refund_amount
                        )}
                    </td>

                    <td>
                        ${escapeHtml(
                            refund.reason
                        )}
                    </td>

                </tr>
            `;
        }
    ).join("");
}


/* =========================================================
   RENDER DEPOSITS
========================================================= */

function renderDeposits(deposits) {

    const tbody =
        document.getElementById(
            "deposit_table_body"
        );

    if (!tbody) {
        return;
    }


    if (!deposits.length) {

        tbody.innerHTML = `
            <tr>
                <td colspan="8" class="empty-row">
                    No deposit records found.
                </td>
            </tr>
        `;

        return;
    }


    tbody.innerHTML = deposits.map(
        (deposit, index) => {

            return `
                <tr>

                    <td>${index + 1}</td>

                    <td>
                        ${escapeHtml(
                            deposit.deposit_no
                        )}
                    </td>

                    <td>
                        ${escapeHtml(
                            deposit.date
                        )}
                    </td>

                    <td>
                        ${escapeHtml(
                            deposit.time
                        )}
                    </td>

                    <td>
                        ${escapeHtml(
                            deposit.hospital_no
                        )}
                    </td>

                    <td>
                        ${escapeHtml(
                            deposit.patient_name
                        )}
                    </td>

                    <td>
                        ${formatAmount(
                            deposit.amount
                        )}
                    </td>

                    <td>
                        ${escapeHtml(
                            deposit.remarks
                        )}
                    </td>

                </tr>
            `;
        }
    ).join("");
}


/* =========================================================
   RESET REPORT
========================================================= */

function resetBillingReport() {

    const fields = [
        "start_date",
        "end_date",
        "hospital_no",
        "bill_no",
        "patient_name",
        "payment_type"
    ];


    fields.forEach(
        function (id) {

            const element =
                document.getElementById(id);

            if (element) {
                element.value = "";
            }
        }
    );


    updateBillingSummary({

        total_bills: 0,

        gross_billing: 0,

        discount: 0,

        net_billing: 0,

        total_refund: 0,

        total_deposit: 0,

        net_revenue: 0
    });


    renderBills([]);

    renderRefunds([]);

    renderDeposits([]);
}


/* =========================================================
   PRINT BILLING REPORT
========================================================= */

function printBillingReport() {

    window.print();
}


/* =========================================================
   EXPORT EXCEL
========================================================= */

function exportBillingExcel() {

    const startDate =
        document.getElementById("start_date")?.value || "";

    const endDate =
        document.getElementById("end_date")?.value || "";

    const hospitalNo =
        document.getElementById("hospital_no")?.value.trim() || "";

    const billNo =
        document.getElementById("bill_no")?.value.trim() || "";

    const patientName =
        document.getElementById("patient_name")?.value.trim() || "";

    const paymentType =
        document.getElementById("payment_type")?.value || "";


    const params =
        new URLSearchParams();


    if (startDate) {
        params.append(
            "start_date",
            startDate
        );
    }

    if (endDate) {
        params.append(
            "end_date",
            endDate
        );
    }

    if (hospitalNo) {
        params.append(
            "hospital_no",
            hospitalNo
        );
    }

    if (billNo) {
        params.append(
            "bill_no",
            billNo
        );
    }

    if (patientName) {
        params.append(
            "patient_name",
            patientName
        );
    }

    if (paymentType) {
        params.append(
            "payment_type",
            paymentType
        );


    }


    window.location.href =
        `/billing-reports/export-excel?${params.toString()}`;
}


/* =========================================================
   HELPER - SET TEXT
========================================================= */

function setText(id, value) {

    const element =
        document.getElementById(id);

    if (element) {
        element.textContent = value;
    }
}


/* =========================================================
   HELPER - FORMAT NUMBER
========================================================= */

function formatNumber(
    value,
    decimals = 2
) {

    const number =
        Number(value || 0);

    return number.toLocaleString(
        "en-US",
        {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        }
    );
}


/* =========================================================
   HELPER - FORMAT AMOUNT
========================================================= */

function formatAmount(value) {

    return formatNumber(
        value,
        2
    );
}


/* =========================================================
   HELPER - ESCAPE HTML
========================================================= */

function escapeHtml(value) {

    if (
        value === null ||
        value === undefined
    ) {
        return "";
    }

    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


/* =========================================================
   PAGE INITIALIZATION
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        console.log(
            "Billing Reports JS loaded."
        );

    }
);

