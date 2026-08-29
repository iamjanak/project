// =====================================================
// PATIENT DISCHARGE MODULE
// SwasthaCare HMS
//
// Features:
// - Dynamic tab handling
// - Table filtering
// - Discharge confirmation modal
// - Discharge API submission
// - Professional success modal
// - Professional error modal
// - ESC support
// - Backdrop click support
// - AJAX-compatible event delegation
// =====================================================

(function () {

    // =====================================================
    // PREVENT DUPLICATE EVENT LISTENERS
    // =====================================================

    if (window.__patientDischargeDelegationAttached) {

        console.log(
            "Patient Discharge delegation already attached."
        );

        return;
    }

    window.__patientDischargeDelegationAttached = true;


    console.log(
        "PATIENT DISCHARGE JS LOADED"
    );


    // =====================================================
    // ROOT
    // =====================================================

    function getRoot(startElement) {

        if (
            startElement &&
            typeof startElement.closest === "function"
        ) {

            const page =
                startElement.closest(".dis-page");

            if (page) {
                return page;
            }
        }

        return document;
    }


    // =====================================================
    // QUERY
    // =====================================================

    function q(root, id) {

        if (!root) {
            return null;
        }

        return root.querySelector(`#${id}`);
    }


    // =====================================================
    // SUCCESS MODAL
    // =====================================================

    function showSuccessModal(
        admissionNo,
        callback
    ) {

        const modal =
            document.getElementById(
                "successModal"
            );

        const admissionElement =
            document.getElementById(
                "successAdmissionNo"
            );

        if (!modal) {

            console.error(
                "Success modal not found."
            );

            if (callback) {
                callback();
            }

            return;
        }


        if (admissionElement) {

            admissionElement.textContent =
                admissionNo || "—";
        }


        modal.classList.add(
            "is-open"
        );


        document.body.classList.add(
            "discharge-modal-open"
        );


        // -------------------------------------------------
        // Save callback
        // -------------------------------------------------

        window.__dischargeSuccessCallback =
            callback || null;


        console.log(
            "SUCCESS MODAL OPENED"
        );
    }


    // =====================================================
    // CLOSE SUCCESS MODAL
    // =====================================================

    function closeSuccessModal() {

        const modal =
            document.getElementById(
                "successModal"
            );


        if (!modal) {
            return;
        }


        modal.classList.remove(
            "is-open"
        );


        document.body.classList.remove(
            "discharge-modal-open"
        );


        const callback =
            window.__dischargeSuccessCallback;


        window.__dischargeSuccessCallback =
            null;


        if (typeof callback === "function") {

            callback();
        }
    }


    // =====================================================
    // ERROR MODAL
    // =====================================================

    function showErrorModal(message) {

        const modal =
            document.getElementById(
                "errorModal"
            );


        const messageElement =
            document.getElementById(
                "errorMessage"
            );


        if (!modal) {

            console.error(
                "ERROR:",
                message
            );

            return;
        }


        if (messageElement) {

            messageElement.textContent =
                message ||
                "Unable to complete the request.";
        }


        modal.classList.add(
            "is-open"
        );
    }


    // =====================================================
    // CLOSE ERROR MODAL
    // =====================================================

    function closeErrorModal() {

        const modal =
            document.getElementById(
                "errorModal"
            );


        if (!modal) {
            return;
        }


        modal.classList.remove(
            "is-open"
        );
    }


    // =====================================================
    // TABS
    // =====================================================

    function activateTab(
        tabId,
        root
    ) {

        if (!root) {
            root = document;
        }


        const tabButtons =
            root.querySelectorAll(
                ".dis-tab-btn"
            );


        const tabPanels =
            root.querySelectorAll(
                ".dis-tab-panel"
            );


        tabButtons.forEach(
            function (button) {

                button.classList.remove(
                    "is-active"
                );

            }
        );


        tabPanels.forEach(
            function (panel) {

                panel.classList.remove(
                    "is-active"
                );

            }
        );


        const selectedButton =
            root.querySelector(
                `.dis-tab-btn[data-tab="${tabId}"]`
            );


        const selectedPanel =
            root.querySelector(
                `#${tabId}`
            );


        if (selectedButton) {

            selectedButton.classList.add(
                "is-active"
            );
        }


        if (selectedPanel) {

            selectedPanel.classList.add(
                "is-active"
            );
        }
    }


    // =====================================================
    // TABLE FILTER
    // =====================================================

    function filterTable(
        input,
        tableId,
        root
    ) {

        if (!input) {
            return;
        }


        const table =
            q(root, tableId);


        if (!table) {
            return;
        }


        const query =
            input.value
                .trim()
                .toLowerCase();


        const rows =
            table.querySelectorAll(
                "tbody tr"
            );


        rows.forEach(
            function (row) {

                const text =
                    row.textContent
                        .toLowerCase();


                row.style.display =
                    text.includes(query)
                        ? ""
                        : "none";

            }
        );
    }


    // =====================================================
    // OPEN DISCHARGE MODAL
    // =====================================================

    function openDischargeModal(
        button
    ) {

        const root =
            getRoot(button);


        let modalBackdrop =
            q(
                root,
                "dischargeModalBackdrop"
            );


        if (!modalBackdrop) {

            modalBackdrop =
                document.getElementById(
                    "dischargeModalBackdrop"
                );
        }


        if (!modalBackdrop) {

            showErrorModal(
                "Unable to open the discharge window. Please reload the page."
            );

            return;
        }


        const admissionId =
            q(
                modalBackdrop,
                "dischargeAdmissionId"
            );


        const reason =
            q(
                modalBackdrop,
                "dischargeReason"
            );


        const summary =
            q(
                modalBackdrop,
                "dischargeSummary"
            );


        if (!admissionId) {

            showErrorModal(
                "The admission record could not be loaded."
            );

            return;
        }


        // -------------------------------------------------
        // SET ADMISSION ID
        // -------------------------------------------------

        admissionId.value =
            button.dataset.id || "";


        // -------------------------------------------------
        // SUMMARY INFORMATION
        // -------------------------------------------------

        const admissionNo =
            q(
                modalBackdrop,
                "modalAdmissionNo"
            );


        const patientNo =
            q(
                modalBackdrop,
                "modalPatientNo"
            );


        const patientName =
            q(
                modalBackdrop,
                "modalPatientName"
            );


        const bed =
            q(
                modalBackdrop,
                "modalBed"
            );


        const admittedOn =
            q(
                modalBackdrop,
                "modalAdmittedOn"
            );


        if (admissionNo) {

            admissionNo.textContent =
                button.dataset.admissionNo ||
                "—";
        }


        if (patientNo) {

            patientNo.textContent =
                button.dataset.patientNo ||
                "—";
        }


        if (patientName) {

            patientName.textContent =
                button.dataset.patientName ||
                "—";
        }


        if (bed) {

            bed.textContent =
                button.dataset.bed ||
                "—";
        }


        if (admittedOn) {

            admittedOn.textContent =
                button.dataset.admittedOn ||
                "—";
        }


        // -------------------------------------------------
        // RESET FORM
        // -------------------------------------------------

        if (reason) {
            reason.value = "";
        }


        if (summary) {
            summary.value = "";
        }


        // -------------------------------------------------
        // OPEN
        // -------------------------------------------------

        modalBackdrop.classList.add(
            "is-open"
        );


        document.body.classList.add(
            "discharge-modal-open"
        );
    }


    // =====================================================
    // CLOSE DISCHARGE MODAL
    // =====================================================

    function closeDischargeModal() {

        const modal =
            document.getElementById(
                "dischargeModalBackdrop"
            );


        if (!modal) {
            return;
        }


        modal.classList.remove(
            "is-open"
        );


        document.body.classList.remove(
            "discharge-modal-open"
        );
    }


    // =====================================================
    // SUBMIT DISCHARGE
    // =====================================================

    async function submitDischarge(form) {

        const root =
            getRoot(form);


        const admissionIdElement =
            q(
                root,
                "dischargeAdmissionId"
            );


        const reasonElement =
            q(
                root,
                "dischargeReason"
            );


        const summaryElement =
            q(
                root,
                "dischargeSummary"
            );


        const confirmButton =
            q(
                root,
                "confirmDischargeBtn"
            );


        // -------------------------------------------------
        // VALIDATION
        // -------------------------------------------------

        if (!admissionIdElement) {

            showErrorModal(
                "Admission record was not found."
            );

            return;
        }


        const admissionId =
            admissionIdElement.value.trim();


        const reason =
            reasonElement
                ? reasonElement.value.trim()
                : "";


        const summary =
            summaryElement
                ? summaryElement.value.trim()
                : "";


        if (!admissionId) {

            showErrorModal(
                "Invalid admission record."
            );

            return;
        }


        if (!reason) {

            showErrorModal(
                "Please select a discharge reason."
            );

            if (reasonElement) {
                reasonElement.focus();
            }

            return;
        }


        // -------------------------------------------------
        // DISABLE BUTTON
        // -------------------------------------------------

        if (confirmButton) {

            confirmButton.disabled =
                true;

            confirmButton.textContent =
                "Discharging...";
        }


        try {

            // =================================================
            // API REQUEST
            // =================================================

            const response =
                await fetch(
                    `/admission/discharge/${encodeURIComponent(admissionId)}`,
                    {
                        method: "POST",

                        headers: {

                            "Content-Type":
                                "application/json",

                            "Accept":
                                "application/json",

                            "X-Requested-With":
                                "XMLHttpRequest"
                        },

                        credentials:
                            "same-origin",

                        body:
                            JSON.stringify({

                                discharge_reason:
                                    reason,

                                discharge_summary:
                                    summary
                            })
                    }
                );


            // =================================================
            // READ RESPONSE
            // =================================================

            const responseText =
                await response.text();


            let data;


            try {

                data =
                    JSON.parse(
                        responseText
                    );

            } catch (jsonError) {

                console.error(
                    "SERVER RESPONSE:",
                    responseText
                );


                if (
                    response.status === 401
                ) {

                    throw new Error(
                        "Your session has expired. Please login again."
                    );
                }


                if (
                    response.status === 404
                ) {

                    throw new Error(
                        "Discharge API was not found. Please check the Flask route."
                    );
                }


                if (
                    response.status === 405
                ) {

                    throw new Error(
                        "The discharge API does not allow POST requests."
                    );
                }


                if (
                    response.status >= 500
                ) {

                    throw new Error(
                        "A server error occurred. Please check the VS Code terminal."
                    );
                }


                throw new Error(
                    "The server returned an unexpected response."
                );
            }


            console.log(
                "DISCHARGE RESPONSE:",
                data
            );


            // =================================================
            // SERVER ERROR
            // =================================================

            if (
                !response.ok ||
                !data.success
            ) {

                throw new Error(
                    data.message ||
                    data.error ||
                    "Unable to discharge patient."
                );
            }


            // =================================================
            // SUCCESS
            // =================================================

            const successAdmissionNo =
                data.admission &&
                data.admission.admission_no
                    ? data.admission.admission_no
                    : buttonAdmissionFallback(
                        admissionId
                    );


            closeDischargeModal();


            showSuccessModal(
                successAdmissionNo,
                function () {

                    window.location.href =
                        "/admission/patient_discharge";

                }
            );


        } catch (error) {

            console.error(
                "DISCHARGE ERROR:",
                error
            );


            showErrorModal(
                error.message ||
                "Unable to connect to the server."
            );


        } finally {

            if (confirmButton) {

                confirmButton.disabled =
                    false;

                confirmButton.textContent =
                    "Confirm Discharge";
            }
        }
    }


    // =====================================================
    // FALLBACK
    // =====================================================

    function buttonAdmissionFallback(
        admissionId
    ) {

        return admissionId;
    }


    // =====================================================
    // CLICK EVENTS
    // =====================================================

    document.addEventListener(
        "click",
        function (event) {

            // -------------------------------------------------
            // TAB
            // -------------------------------------------------

            const tabButton =
                event.target.closest &&
                event.target.closest(
                    ".dis-tab-btn"
                );


            if (tabButton) {

                const root =
                    getRoot(tabButton);


                const tabId =
                    tabButton.dataset.tab;


                if (tabId) {

                    activateTab(
                        tabId,
                        root
                    );
                }


                return;
            }


            // -------------------------------------------------
            // DISCHARGE
            // -------------------------------------------------

            const dischargeButton =
                event.target.closest &&
                event.target.closest(
                    ".dis-discharge-btn"
                );


            if (dischargeButton) {

                openDischargeModal(
                    dischargeButton
                );

                return;
            }


            // -------------------------------------------------
            // CANCEL
            // -------------------------------------------------

            const cancelButton =
                event.target.closest &&
                event.target.closest(
                    "#cancelDischargeBtn"
                );


            if (cancelButton) {

                closeDischargeModal();

                return;
            }


            // -------------------------------------------------
            // DISCHARGE BACKDROP
            // -------------------------------------------------

            const dischargeBackdrop =
                event.target.closest &&
                event.target.closest(
                    "#dischargeModalBackdrop"
                );


            if (
                dischargeBackdrop &&
                event.target ===
                    dischargeBackdrop
            ) {

                closeDischargeModal();

                return;
            }


            // -------------------------------------------------
            // SUCCESS DONE
            // -------------------------------------------------

            if (
                event.target.closest &&
                event.target.closest(
                    "#successOkBtn"
                )
            ) {

                closeSuccessModal();

                return;
            }


            // -------------------------------------------------
            // SUCCESS CLOSE
            // -------------------------------------------------

            if (
                event.target.closest &&
                event.target.closest(
                    "#successCloseBtn"
                )
            ) {

                closeSuccessModal();

                return;
            }


            // -------------------------------------------------
            // SUCCESS BACKDROP
            // -------------------------------------------------

            const successBackdrop =
                event.target.closest &&
                event.target.closest(
                    "#successModal"
                );


            if (
                successBackdrop &&
                event.target ===
                    successBackdrop
            ) {

                closeSuccessModal();

                return;
            }


            // -------------------------------------------------
            // ERROR OK
            // -------------------------------------------------

            if (
                event.target.closest &&
                event.target.closest(
                    "#errorOkBtn"
                )
            ) {

                closeErrorModal();

                return;
            }


            // -------------------------------------------------
            // ERROR BACKDROP
            // -------------------------------------------------

            const errorBackdrop =
                event.target.closest &&
                event.target.closest(
                    "#errorModal"
                );


            if (
                errorBackdrop &&
                event.target ===
                    errorBackdrop
            ) {

                closeErrorModal();

                return;
            }

        }
    );


    // =====================================================
    // FORM SUBMIT
    // =====================================================

    document.addEventListener(
        "submit",
        function (event) {

            const form =
                event.target;


            if (
                form &&
                form.id ===
                    "dischargeForm"
            ) {

                event.preventDefault();


                submitDischarge(
                    form
                );
            }

        }
    );


    // =====================================================
    // FILTER
    // =====================================================

    document.addEventListener(
        "input",
        function (event) {

            if (!event.target) {
                return;
            }


            const root =
                getRoot(
                    event.target
                );


            if (
                event.target.id ===
                "admittedFilter"
            ) {

                filterTable(
                    event.target,
                    "admittedTable",
                    root
                );

                return;
            }


            if (
                event.target.id ===
                "dischargedFilter"
            ) {

                filterTable(
                    event.target,
                    "dischargedTable",
                    root
                );

                return;
            }

        }
    );


    // =====================================================
    // ESC
    // =====================================================

    document.addEventListener(
        "keydown",
        function (event) {

            if (
                event.key !==
                "Escape"
            ) {
                return;
            }


            const successModal =
                document.getElementById(
                    "successModal"
                );


            const errorModal =
                document.getElementById(
                    "errorModal"
                );


            const dischargeModal =
                document.getElementById(
                    "dischargeModalBackdrop"
                );


            if (
                successModal &&
                successModal.classList.contains(
                    "is-open"
                )
            ) {

                closeSuccessModal();

                return;
            }


            if (
                errorModal &&
                errorModal.classList.contains(
                    "is-open"
                )
            ) {

                closeErrorModal();

                return;
            }


            if (
                dischargeModal &&
                dischargeModal.classList.contains(
                    "is-open"
                )
            ) {

                closeDischargeModal();

                return;
            }

        }
    );


    // =====================================================
    // GLOBAL FUNCTIONS
    //
    // These are optional, but useful if another HMS
    // module needs to close the modal.
    // =====================================================

    window.showSuccessModal =
        showSuccessModal;


    window.closeSuccessModal =
        closeSuccessModal;


    window.showErrorModal =
        showErrorModal;


    window.closeErrorModal =
        closeErrorModal;


    console.log(
        "PATIENT DISCHARGE DELEGATED LISTENERS READY"
    );

})();