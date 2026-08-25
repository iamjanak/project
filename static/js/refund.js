// =========================================================
// BILL REFUND JAVASCRIPT
// =========================================================

document.addEventListener("DOMContentLoaded", function () {

    // =====================================================
    // ELEMENTS
    // =====================================================

    const patientNo = document.getElementById("patientNo");
    const searchBtn = document.getElementById("searchPatientBtn");

    const patientInfo = document.getElementById("patientInfo");
    const billSection = document.getElementById("billSection");
    const billSelect = document.getElementById("billSelect");
    const billDetails = document.getElementById("billDetails");

    const refundAmount = document.getElementById("refundAmount");
    const refundReason = document.getElementById("refundReason");

    const refundBtn = document.getElementById("refundBtn");
    const clearBtn = document.getElementById("clearBtn");


    // =====================================================
    // DATA
    // =====================================================

    let patientData = null;
    let bills = [];


    // =====================================================
    // SEARCH BUTTON
    // =====================================================

    searchBtn.addEventListener("click", searchPatient);


    // =====================================================
    // ENTER KEY
    // =====================================================

    patientNo.addEventListener("keydown", function (event) {

        if (event.key === "Enter") {

            event.preventDefault();

            searchPatient();

        }

    });


    // =====================================================
    // SEARCH PATIENT
    // =====================================================

    async function searchPatient() {

        const number = patientNo.value.trim();


        if (!number) {

            showError(
                "Please enter hospital number."
            );

            patientNo.focus();

            return;
        }


        // -------------------------------------------------
        // Loading
        // -------------------------------------------------

        searchBtn.disabled = true;
        searchBtn.textContent = "Searching...";


        try {

            const response = await fetch(
                `/fetch_refund_patient/${encodeURIComponent(number)}`,
                {
                    method: "GET",
                    headers: {
                        "Accept": "application/json"
                    },
                    cache: "no-cache"
                }
            );


            const data = await response.json();


            console.log(
                "REFUND PATIENT RESPONSE:",
                data
            );


            if (!response.ok || !data.success) {

                showError(
                    data.message ||
                    "Patient not found."
                );

                return;
            }


            // -------------------------------------------------
            // Store patient
            // -------------------------------------------------

            patientData = data.patient;


            // -------------------------------------------------
            // Display patient information
            // -------------------------------------------------

            document.getElementById(
                "displayPatientNo"
            ).textContent =
                patientData.patient_no || "-";


            document.getElementById(
                "displayPatientName"
            ).textContent =
                patientData.full_name || "-";


            document.getElementById(
                "displayAge"
            ).textContent =
                patientData.age || "-";


            document.getElementById(
                "displayGender"
            ).textContent =
                patientData.gender || "-";


            // -------------------------------------------------
            // Show patient information
            // -------------------------------------------------

            patientInfo.classList.remove("hidden");


            // -------------------------------------------------
            // Reset previous bills
            // -------------------------------------------------

            bills = [];

            billSelect.innerHTML =
                '<option value="">Loading bills...</option>';


            billDetails.classList.add("hidden");

            refundAmount.value = "";
            refundReason.value = "";


            // -------------------------------------------------
            // Show bill section
            // -------------------------------------------------

            billSection.classList.remove("hidden");


            // =================================================
            // IMPORTANT
            // LOAD BILLS
            // =================================================

            await loadPatientBills(
                patientData.patient_no
            );


        } catch (error) {

            console.error(
                "REFUND SEARCH ERROR:",
                error
            );

            showError(
                "Unable to connect to server."
            );


        } finally {

            searchBtn.disabled = false;

            searchBtn.textContent = "Search";

        }

    }


    // =====================================================
    // LOAD PATIENT BILLS
    // =====================================================

    async function loadPatientBills(patientNumber) {

        console.log(
            "Loading bills for patient:",
            patientNumber
        );


        try {

            const response = await fetch(
                `/fetch_refund_bills/${encodeURIComponent(patientNumber)}`,
                {
                    method: "GET",

                    headers: {
                        "Accept": "application/json"
                    },

                    cache: "no-cache"
                }
            );


            const data = await response.json();


            console.log(
                "REFUND BILLS RESPONSE:",
                data
            );


            if (!response.ok || !data.success) {

                billSelect.innerHTML =
                    '<option value="">Unable to load bills</option>';


                showError(
                    data.message ||
                    "Unable to load patient bills."
                );

                return;
            }


            // -------------------------------------------------
            // Store bills
            // -------------------------------------------------

            bills = data.bills || [];


            console.log(
                "BILLS FOUND:",
                bills
            );


            // -------------------------------------------------
            // No bills
            // -------------------------------------------------

            if (bills.length === 0) {

                billSelect.innerHTML =
                    '<option value="">No refundable bills found</option>';

                return;
            }


            // -------------------------------------------------
            // Default option
            // -------------------------------------------------

            billSelect.innerHTML =
                '<option value="">Select Bill</option>';


            // -------------------------------------------------
            // Add bills
            // -------------------------------------------------

            bills.forEach(function (bill) {

                const option =
                    document.createElement("option");


                option.value =
                    bill.bill_no;


                option.textContent =
                    `${bill.bill_no} - Rs. ${Number(
                        bill.bill_amount || 0
                    ).toFixed(2)} (Refundable: Rs. ${Number(
                        bill.refundable_amount || 0
                    ).toFixed(2)})`;


                billSelect.appendChild(option);

            });


            console.log(
                "Bill dropdown populated successfully."
            );

        } catch (error) {

            console.error(
                "LOAD REFUND BILLS ERROR:",
                error
            );


            billSelect.innerHTML =
                '<option value="">Unable to load bills</option>';


            showError(
                "Unable to load patient bills."
            );

        }

    }


    // =====================================================
    // BILL SELECTION
    // =====================================================

    billSelect.addEventListener(
        "change",
        function () {

            const selectedBill =
                bills.find(function (bill) {

                    return bill.bill_no ===
                        billSelect.value;

                });


            if (!selectedBill) {

                billDetails.classList.add("hidden");

                refundAmount.value = "";

                return;
            }


            // -------------------------------------------------
            // Bill number
            // -------------------------------------------------

            document.getElementById(
                "displayBillNo"
            ).textContent =
                selectedBill.bill_no;


            // -------------------------------------------------
            // Bill amount
            // -------------------------------------------------

            document.getElementById(
                "displayBillAmount"
            ).textContent =
                `Rs. ${Number(
                    selectedBill.bill_amount || 0
                ).toFixed(2)}`;


            // -------------------------------------------------
            // Clear refund amount
            // -------------------------------------------------

            refundAmount.value = "";


            // -------------------------------------------------
            // Show bill details
            // -------------------------------------------------

            billDetails.classList.remove("hidden");

        }
    );


    // =====================================================
    // PROCESS REFUND
    // =====================================================

    refundBtn.addEventListener(
        "click",
        processRefund
    );


   async function processRefund() {

    if (!patientData) {
        showError("Please search for a patient first.");
        return;
    }

    if (!billSelect.value) {
        showError("Please select a bill.");
        billSelect.focus();
        return;
    }

    const amount = Number(refundAmount.value);

    if (!amount || amount <= 0) {
        showError("Please enter a valid refund amount.");
        refundAmount.focus();
        return;
    }

    const selectedBill = bills.find(function (bill) {
        return String(bill.bill_no) === String(billSelect.value);
    });

    if (!selectedBill) {
        showError("Selected bill could not be found.");
        return;
    }

    const refundableAmount =
        Number(selectedBill.refundable_amount || 0);

    if (amount > refundableAmount) {

        showError(
            `Maximum refundable amount is Rs. ${refundableAmount.toFixed(2)}`
        );

        return;
    }

    const reason = refundReason.value.trim();

    if (!reason) {
        showError("Please enter refund reason.");
        refundReason.focus();
        return;
    }

    refundBtn.disabled = true;
    refundBtn.textContent = "Processing...";

    try {

        console.log("Sending refund request...");

        const response = await fetch("/save_refund", {
            method: "POST",

            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json"
            },

            body: JSON.stringify({
                patient_no: patientData.patient_no,
                bill_no: selectedBill.bill_no,
                refund_amount: amount,
                reason: reason
            })
        });

        console.log("HTTP STATUS:", response.status);
        console.log("HTTP OK:", response.ok);

        // Get raw response first
        const responseText = await response.text();

        console.log(
            "RAW SERVER RESPONSE:",
            responseText
        );

        let data;

        try {

            data = JSON.parse(responseText);

        } catch (jsonError) {

            console.error(
                "JSON PARSE ERROR:",
                jsonError
            );

            showError(
                `Server returned an invalid response. HTTP ${response.status}`
            );

            return;
        }

        console.log(
            "PARSED REFUND RESPONSE:",
            data
        );

        if (!response.ok || !data.success) {

            showError(
                data.message ||
                `Refund failed. HTTP ${response.status}`
            );

            return;
        }

        // =============================================
        // SUCCESS
        // =============================================

        const refundNo =
            data.refund_no || "";

        const refundValue =
            Number(
                data.refund_amount || amount
            ).toFixed(2);

        document.getElementById(
            "successMessage"
        ).textContent =
            `Refund ${refundNo} of Rs. ${refundValue} has been processed successfully.`;

        document.getElementById(
            "successPopup"
        ).classList.remove("hidden");

        refundAmount.value = "";
        refundReason.value = "";

        // Reload bills
        await loadPatientBills(
            patientData.patient_no
        );

        billDetails.classList.add("hidden");

    } catch (error) {

        console.error(
            "SAVE REFUND JAVASCRIPT ERROR:",
            error
        );

        showError(
            `Refund request failed: ${error.message}`
        );

    } finally {

        refundBtn.disabled = false;
        refundBtn.textContent = "Process Refund";

    }
}

    // =====================================================
    // CLEAR BUTTON
    // =====================================================

    clearBtn.addEventListener(
        "click",
        clearRefundPage
    );


    function clearRefundPage() {

        patientNo.value = "";

        patientData = null;

        patientInfo.classList.add("hidden");

        bills = [];

        billSelect.innerHTML =
            '<option value="">Select Bill</option>';

        billSection.classList.add("hidden");

        billDetails.classList.add("hidden");

        refundAmount.value = "";
        refundReason.value = "";

        patientNo.focus();

    }

});


// =========================================================
// ERROR POPUP
// =========================================================

function showError(message) {

    const errorMessage =
        document.getElementById("errorMessage");

    const errorPopup =
        document.getElementById("errorPopup");


    if (errorMessage) {

        errorMessage.textContent =
            message;

    }


    if (errorPopup) {

        errorPopup.classList.remove("hidden");

    }

}


// =========================================================
// CLOSE ERROR POPUP
// =========================================================

function closeErrorPopup() {

    const errorPopup =
        document.getElementById("errorPopup");


    if (errorPopup) {

        errorPopup.classList.add("hidden");

    }

}


// =========================================================
// CLOSE SUCCESS POPUP
// =========================================================

function closeSuccessPopup() {

    const successPopup =
        document.getElementById("successPopup");


    if (successPopup) {

        successPopup.classList.add("hidden");

    }

}