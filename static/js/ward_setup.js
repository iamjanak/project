javascript
function initWardSetup() {

    console.log("WARD SETUP JS INITIALIZING");

    // =====================================================
    // ELEMENTS
    // =====================================================

    const openBtn =
        document.getElementById("openWardFormBtn");

    const closeBtn =
        document.getElementById("closeWardFormBtn");

    const cancelBtn =
        document.getElementById("cancelWardBtn");

    const formCard =
        document.getElementById("wardFormCard");

    const form =
        document.getElementById("wardForm");

    const saveBtn =
        document.getElementById("saveWardBtn");

    const successPopup =
        document.getElementById("wardSuccessPopup");

    const errorPopup =
        document.getElementById("wardErrorPopup");

    const successMessage =
        document.getElementById("wardSuccessMessage");

    const errorMessage =
        document.getElementById("wardErrorMessage");


    // =====================================================
    // PAGE CHECK
    // =====================================================

    if (!formCard || !form) {

        console.log("WARD SETUP ELEMENTS NOT FOUND");

        return;

    }


    // =====================================================
    // PREVENT DOUBLE INITIALIZATION
    // =====================================================

    if (form.dataset.initialized === "true") {

        console.log("WARD SETUP ALREADY INITIALIZED");

        return;

    }

    form.dataset.initialized = "true";


    // =====================================================
    // POPUP FUNCTIONS
    // =====================================================

    function hidePopup(popup) {

        if (!popup) {
            return;
        }

        popup.classList.remove("show");
        popup.style.display = "none";

    }


    function showSuccess(message) {

        if (!successPopup) {
            return;
        }

        if (successMessage) {

            successMessage.textContent =
                message || "Ward added successfully.";

        }

        hidePopup(errorPopup);

        successPopup.style.display = "flex";
        successPopup.classList.add("show");


        setTimeout(function () {

            hidePopup(successPopup);

        }, 4000);

    }


    function showError(message) {

        if (!errorPopup) {
            return;
        }

        if (errorMessage) {

            errorMessage.textContent =
                message ||
                "Unable to complete the request.";

        }

        hidePopup(successPopup);

        errorPopup.style.display = "flex";
        errorPopup.classList.add("show");


        setTimeout(function () {

            hidePopup(errorPopup);

        }, 5000);


        console.error(
            "WARD ERROR:",
            message
        );

    }


    // =====================================================
    // OPEN FORM
    // =====================================================

    function openWardForm() {

        console.log("OPEN WARD FORM");

        formCard.style.display = "block";

        if (openBtn) {

            openBtn.style.display = "none";

        }


        const wardCode =
            document.getElementById("wardCode");

        if (wardCode) {

            setTimeout(function () {

                wardCode.focus();

            }, 100);

        }

    }


    // =====================================================
    // CLOSE FORM
    // =====================================================

    function closeWardForm() {

        console.log("CLOSE WARD FORM");

        formCard.style.display = "none";

        if (openBtn) {

            openBtn.style.display = "inline-flex";

        }

        form.reset();


        const status =
            document.getElementById("wardStatus");

        if (status) {

            status.value = "Active";

        }

    }


    // =====================================================
    // POPUP CLOSE BUTTONS
    // =====================================================

    document
        .querySelectorAll(".ward-popup-close")
        .forEach(function (button) {

            button.addEventListener(
                "click",
                function () {

                    const popupId =
                        button.getAttribute("data-popup");

                    const popup =
                        document.getElementById(popupId);

                    hidePopup(popup);

                }
            );

        });


    // =====================================================
    // OPEN BUTTON
    // =====================================================

    if (openBtn) {

        openBtn.addEventListener(
            "click",
            function (event) {

                event.preventDefault();

                openWardForm();

            }
        );

    }


    // =====================================================
    // CLOSE BUTTON
    // =====================================================

    if (closeBtn) {

        closeBtn.addEventListener(
            "click",
            function (event) {

                event.preventDefault();

                closeWardForm();

            }
        );

    }


    // =====================================================
    // CANCEL BUTTON
    // =====================================================

    if (cancelBtn) {

        cancelBtn.addEventListener(
            "click",
            function (event) {

                event.preventDefault();

                closeWardForm();

            }
        );

    }


    // =====================================================
    // SAVE WARD
    // =====================================================

    form.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();

            console.log("WARD FORM SUBMITTED");


            // =================================================
            // GET VALUES
            // =================================================

            const wardCodeElement =
                document.getElementById("wardCode");

            const wardNameElement =
                document.getElementById("wardName");

            const wardTypeElement =
                document.getElementById("wardType");

            const floorElement =
                document.getElementById("wardFloor");

            const descriptionElement =
                document.getElementById("wardDescription");

            const statusElement =
                document.getElementById("wardStatus");


            const wardCode =
                wardCodeElement
                    ? wardCodeElement.value.trim()
                    : "";

            const wardName =
                wardNameElement
                    ? wardNameElement.value.trim()
                    : "";

            const wardType =
                wardTypeElement
                    ? wardTypeElement.value.trim()
                    : "";

            const floor =
                floorElement
                    ? floorElement.value.trim()
                    : "";

            const description =
                descriptionElement
                    ? descriptionElement.value.trim()
                    : "";

            const status =
                statusElement
                    ? statusElement.value.trim()
                    : "Active";


            // =================================================
            // VALIDATION
            // =================================================

            if (!wardCode) {

                showError("Ward code is required.");

                if (wardCodeElement) {
                    wardCodeElement.focus();
                }

                return;

            }


            if (!wardName) {

                showError("Ward name is required.");

                if (wardNameElement) {
                    wardNameElement.focus();
                }

                return;

            }


            if (!wardType) {

                showError("Ward type is required.");

                if (wardTypeElement) {
                    wardTypeElement.focus();
                }

                return;

            }


            // =================================================
            // DATA
            // =================================================

            const data = {

                ward_code: wardCode,

                ward_name: wardName,

                ward_type: wardType,

                floor: floor,

                description: description,

                status: status || "Active"

            };


            console.log("WARD DATA:", data);


            // =================================================
            // DISABLE BUTTON
            // =================================================

            if (saveBtn) {

                saveBtn.disabled = true;

                saveBtn.dataset.originalText =
                    saveBtn.textContent;

                saveBtn.textContent =
                    "Saving...";

            }


            // =================================================
            // SEND TO FLASK
            //
            // IMPORTANT:
            // Flask route:
            // POST /ward/save
            // =================================================

            try {

                const response =
                    await fetch(
                        "/ward/save",
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
                                JSON.stringify(data)

                        }
                    );


                console.log(
                    "WARD SAVE STATUS:",
                    response.status
                );


                const contentType =
                    response.headers.get(
                        "content-type"
                    ) || "";


                // =================================================
                // NON JSON RESPONSE
                // =================================================

                if (
                    !contentType.includes(
                        "application/json"
                    )
                ) {

                    const text =
                        await response.text();

                    console.error(
                        "WARD NON-JSON RESPONSE:",
                        text
                    );


                    showError(
                        "Unable to connect to the server."
                    );

                    return;

                }


                const result =
                    await response.json();


                console.log(
                    "WARD SAVE RESPONSE:",
                    result
                );


                // =================================================
                // ERROR
                // =================================================

                if (
                    !response.ok ||
                    result.success !== true
                ) {

                    showError(
                        result.message ||
                        result.error ||
                        "Unable to add ward."
                    );

                    return;

                }


                // =================================================
                // SUCCESS
                // =================================================

                showSuccess(
                    result.message ||
                    "Ward added successfully."
                );


                // =================================================
                // ADD ROW
                // =================================================

                if (result.ward) {

                    addWardToTable(
                        result.ward
                    );

                }


                // =================================================
                // RESET FORM
                // =================================================

                form.reset();


                const status =
                    document.getElementById(
                        "wardStatus"
                    );

                if (status) {

                    status.value =
                        "Active";

                }


                // =================================================
                // CLOSE FORM
                // =================================================

                formCard.style.display =
                    "none";


                if (openBtn) {

                    openBtn.style.display =
                        "inline-flex";

                }


            } catch (error) {

                console.error(
                    "SAVE WARD ERROR:",
                    error
                );


                showError(
                    "Unable to connect to the server."
                );


            } finally {

                if (saveBtn) {

                    saveBtn.disabled =
                        false;

                    saveBtn.textContent =
                        saveBtn.dataset.originalText ||
                        "Save Ward";

                }

            }

        }
    );


    // =====================================================
    // ADD WARD TO TABLE
    // =====================================================

    function addWardToTable(ward) {

        const tableBody =
            document.getElementById(
                "wardTableBody"
            );


        if (!tableBody) {

            console.error(
                "WARD TABLE BODY NOT FOUND"
            );

            return;

        }


        const emptyRow =
            document.getElementById(
                "emptyWardRow"
            );


        if (emptyRow) {

            emptyRow.remove();

        }


        const row =
            document.createElement("tr");


        let statusClass =
            "inactive";


        if (ward.status === "Active") {

            statusClass =
                "active";

        } else if (
            ward.status === "Maintenance"
        ) {

            statusClass =
                "maintenance";

        }


        row.innerHTML = `

            <td></td>

            <td>
                <span class="ward-code">
                    ${escapeHtml(ward.ward_code)}
                </span>
            </td>

            <td>
                <strong>
                    ${escapeHtml(ward.ward_name)}
                </strong>
            </td>

            <td>
                ${escapeHtml(ward.ward_type || "")}
            </td>

            <td>
                ${
                    ward.floor
                        ? escapeHtml(ward.floor)
                        : "—"
                }
            </td>

            <td>
                <span class="status-badge ${statusClass}">
                    ${escapeHtml(ward.status || "")}
                </span>
            </td>

            <td>
                ${ward.created_at || "—"}
            </td>

        `;


        tableBody.prepend(row);


        renumberWardRows();

        updateWardCount();

    }


    // =====================================================
    // NUMBER TABLE ROWS
    // =====================================================

    function renumberWardRows() {

        const tableBody =
            document.getElementById(
                "wardTableBody"
            );


        if (!tableBody) {
            return;
        }


        const rows =
            tableBody.querySelectorAll("tr");


        rows.forEach(
            function (row, index) {

                if (row.children.length > 0) {

                    row.children[0]
                        .textContent =
                        index + 1;

                }

            }
        );

    }


    // =====================================================
    // UPDATE COUNT
    // =====================================================

    function updateWardCount() {

        const countElement =
            document.querySelector(".ward-count");

        const tableBody =
            document.getElementById(
                "wardTableBody"
            );


        if (
            !countElement ||
            !tableBody
        ) {

            return;

        }


        const rows =
            tableBody.querySelectorAll("tr");


        const count =
            rows.length;


        countElement.textContent =
            count +
            " Ward" +
            (
                count !== 1
                    ? "s"
                    : ""
            );

    }


    // =====================================================
    // ESCAPE HTML
    // =====================================================

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


    console.log(
        "WARD SETUP EVENT HANDLERS READY"
    );

}


// =========================================================
// INITIAL LOAD
// =========================================================

if (
    document.readyState === "loading"
) {

    document.addEventListener(
        "DOMContentLoaded",
        initWardSetup,
        {
            once: true
        }
    );

} else {

    initWardSetup();

}


// =========================================================
// AJAX PAGE LOAD
// =========================================================

document.addEventListener(
    "page:loaded",
    function () {

        console.log(
            "WARD PAGE LOADED THROUGH AJAX"
        );


        if (
            document.getElementById("wardForm")
        ) {

            initWardSetup();

        }

    }
);

