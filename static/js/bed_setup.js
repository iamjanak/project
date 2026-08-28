(function () {

    console.log("BED SETUP JS LOADED");


    // =====================================================
    // ELEMENTS
    // =====================================================

    const formCard =
        document.getElementById("bedFormCard");

    const form =
        document.getElementById("bedForm");

    const openBtn =
        document.getElementById("openBedFormBtn");

    const closeBtn =
        document.getElementById("closeBedFormBtn");

    const cancelBtn =
        document.getElementById("cancelBedBtn");

    const saveBtn =
        document.getElementById("saveBedBtn");


    // =====================================================
    // OPEN FORM
    // =====================================================

    function openBedForm() {

        if (!formCard) return;

        formCard.style.display = "block";

        if (openBtn) {
            openBtn.style.display = "none";
        }

        setTimeout(function () {

            const room =
                document.getElementById("bedRoom");

            if (room) {
                room.focus();
            }

        }, 100);
    }


    // =====================================================
    // CLOSE FORM
    // =====================================================

    function closeBedForm() {

        if (formCard) {
            formCard.style.display = "none";
        }

        if (openBtn) {
            openBtn.style.display = "inline-flex";
        }

        if (form) {
            form.reset();
        }

        const status =
            document.getElementById("bedStatus");

        if (status) {
            status.value = "Available";
        }
    }


    // =====================================================
    // POPUPS
    // =====================================================

    function hidePopup(popup) {

        if (popup) {
            popup.classList.remove("show");
        }
    }


    function showSuccess(message) {

        const popup =
            document.getElementById(
                "bedSuccessPopup"
            );

        const errorPopup =
            document.getElementById(
                "bedErrorPopup"
            );

        const messageElement =
            document.getElementById(
                "bedSuccessMessage"
            );

        hidePopup(errorPopup);

        if (messageElement) {

            messageElement.textContent =
                message ||
                "Bed added successfully.";
        }

        if (popup) {

            popup.classList.add("show");

            setTimeout(function () {

                hidePopup(popup);

            }, 4000);
        }
    }


    function showError(message) {

        const popup =
            document.getElementById(
                "bedErrorPopup"
            );

        const successPopup =
            document.getElementById(
                "bedSuccessPopup"
            );

        const messageElement =
            document.getElementById(
                "bedErrorMessage"
            );

        hidePopup(successPopup);

        if (messageElement) {

            messageElement.textContent =
                message ||
                "Unable to complete the request.";
        }

        if (popup) {
            popup.classList.add("show");
        }

        console.error(
            "BED ERROR:",
            message
        );
    }


    // =====================================================
    // POPUP CLOSE
    // =====================================================

    document
        .querySelectorAll(".bed-popup-close")
        .forEach(function (button) {

            button.addEventListener(
                "click",
                function () {

                    const popupId =
                        button.getAttribute(
                            "data-popup"
                        );

                    hidePopup(
                        document.getElementById(
                            popupId
                        )
                    );

                }
            );

        });


    // =====================================================
    // BUTTONS
    // =====================================================

    if (openBtn) {

        openBtn.addEventListener(
            "click",
            function (event) {

                event.preventDefault();

                openBedForm();

            }
        );
    }


    if (closeBtn) {

        closeBtn.addEventListener(
            "click",
            function (event) {

                event.preventDefault();

                closeBedForm();

            }
        );
    }


    if (cancelBtn) {

        cancelBtn.addEventListener(
            "click",
            function (event) {

                event.preventDefault();

                closeBedForm();

            }
        );
    }


    // =====================================================
    // SUBMIT
    // =====================================================

    if (form) {

        form.addEventListener(
            "submit",
            async function (event) {

                event.preventDefault();


                // =================================================
                // GET ELEMENTS
                // =================================================

                const roomElement =
                    document.getElementById(
                        "bedRoom"
                    );

                const codeElement =
                    document.getElementById(
                        "bedCode"
                    );

                const nameElement =
                    document.getElementById(
                        "bedName"
                    );

                const priceElement =
                    document.getElementById(
                        "bedPrice"
                    );

                const typeElement =
                    document.getElementById(
                        "bedType"
                    );

                const statusElement =
                    document.getElementById(
                        "bedStatus"
                    );

                const descriptionElement =
                    document.getElementById(
                        "bedDescription"
                    );


                // =================================================
                // GET VALUES
                // =================================================

                const roomId =
                    roomElement
                        ? roomElement.value.trim()
                        : "";

                const bedCode =
                    codeElement
                        ? codeElement.value.trim()
                        : "";

                const bedName =
                    nameElement
                        ? nameElement.value.trim()
                        : "";

                const bedPriceRaw =
                    priceElement
                        ? priceElement.value.trim()
                        : "";

                const bedType =
                    typeElement
                        ? typeElement.value.trim()
                        : "";

                const status =
                    statusElement
                        ? statusElement.value.trim()
                        : "Available";

                const description =
                    descriptionElement
                        ? descriptionElement.value.trim()
                        : "";


                // =================================================
                // VALIDATION
                // =================================================

                if (!roomId) {

                    showError(
                        "Please select a room."
                    );

                    roomElement?.focus();

                    return;
                }


                if (!bedCode) {

                    showError(
                        "Bed code is required."
                    );

                    codeElement?.focus();

                    return;
                }


                if (!bedName) {

                    showError(
                        "Bed name is required."
                    );

                    nameElement?.focus();

                    return;
                }


                // =================================================
                // BED PRICE VALIDATION
                // =================================================

                let bedPrice = null;

                if (bedPriceRaw !== "") {

                    const parsedPrice =
                        Number(bedPriceRaw);

                    if (
                        !Number.isFinite(
                            parsedPrice
                        )
                    ) {

                        showError(
                            "Please enter a valid bed charge."
                        );

                        priceElement?.focus();

                        return;
                    }

                    if (parsedPrice < 0) {

                        showError(
                            "Bed charge cannot be negative."
                        );

                        priceElement?.focus();

                        return;
                    }

                    bedPrice = parsedPrice;
                }


                if (!bedType) {

                    showError(
                        "Please select a bed type."
                    );

                    typeElement?.focus();

                    return;
                }


                // =================================================
                // DATA
                // =================================================

                const bedData = {

                    room_id:
                        Number(roomId),

                    bed_code:
                        bedCode,

                    bed_name:
                        bedName,

                    bed_price:
                        bedPrice,

                    bed_type:
                        bedType,

                    status:
                        status || "Available",

                    description:
                        description
                };


                console.log(
                    "BED DATA:",
                    bedData
                );


                // =================================================
                // SAVE BUTTON
                // =================================================

                const originalText =
                    saveBtn
                        ? saveBtn.textContent
                        : "Save Bed";


                if (saveBtn) {

                    saveBtn.disabled = true;

                    saveBtn.textContent =
                        "Saving...";
                }


                // =================================================
                // REQUEST
                // =================================================

                try {

                    const response =
                        await fetch(
                            "/bed/add",
                            {
                                method: "POST",

                                headers: {
                                    "Content-Type":
                                        "application/json",

                                    "Accept":
                                        "application/json"
                                },

                                credentials:
                                    "same-origin",

                                body:
                                    JSON.stringify(
                                        bedData
                                    )
                            }
                        );


                    // =================================================
                    // RESPONSE TYPE
                    // =================================================

                    const contentType =
                        response.headers.get(
                            "content-type"
                        ) || "";


                    if (
                        !contentType.includes(
                            "application/json"
                        )
                    ) {

                        const text =
                            await response.text();

                        console.error(
                            "NON JSON RESPONSE:",
                            text
                        );

                        showError(
                            "Unable to connect to the server."
                        );

                        return;
                    }


                    // =================================================
                    // JSON
                    // =================================================

                    const result =
                        await response.json();


                    console.log(
                        "BED SERVER RESPONSE:",
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
                            "Unable to add bed."
                        );

                        return;
                    }


                    // =================================================
                    // SUCCESS
                    // =================================================

                    showSuccess(
                        result.message ||
                        "Bed added successfully."
                    );


                    if (result.bed) {

                        addBedToTable(
                            result.bed
                        );
                    }


                    closeBedForm();

                }

                catch (error) {

                    console.error(
                        "BED REQUEST ERROR:",
                        error
                    );

                    showError(
                        "Unable to connect to the server."
                    );

                }

                finally {

                    if (saveBtn) {

                        saveBtn.disabled = false;

                        saveBtn.textContent =
                            originalText;
                    }
                }

            }
        );
    }


    // =====================================================
    // ADD ROW TO TABLE
    // =====================================================

    function addBedToTable(bed) {

        const tableBody =
            document.getElementById(
                "bedTableBody"
            );

        if (!tableBody) return;


        const emptyRow =
            document.getElementById(
                "emptyBedRow"
            );

        if (emptyRow) {
            emptyRow.remove();
        }


        const rowNumber =
            tableBody.querySelectorAll(
                "tr"
            ).length + 1;


        // =================================================
        // STATUS CLASS
        // =================================================

        let statusClass =
            "inactive";

        if (bed.status === "Available") {

            statusClass = "available";

        }
        else if (
            bed.status === "Occupied"
        ) {

            statusClass = "occupied";

        }
        else if (
            bed.status === "Maintenance"
        ) {

            statusClass = "maintenance";
        }


        // =================================================
        // BED PRICE DISPLAY
        // =================================================

        let bedPriceDisplay = "—";

        if (
            bed.bed_price !== null &&
            bed.bed_price !== undefined &&
            bed.bed_price !== ""
        ) {

            const numericPrice =
                Number(bed.bed_price);

            if (
                Number.isFinite(
                    numericPrice
                )
            ) {

                bedPriceDisplay =
                    "Rs. " +
                    numericPrice.toFixed(2);
            }
        }


        // =================================================
        // ROW
        // =================================================

        const row =
            document.createElement("tr");


        row.innerHTML = `

            <td>
                ${rowNumber}
            </td>

            <td>
                <span class="bed-code">
                    ${escapeHtml(
                        bed.bed_code
                    )}
                </span>
            </td>

            <td>
                <strong>
                    ${escapeHtml(
                        bed.bed_name
                    )}
                </strong>
            </td>

            <td>
                ${escapeHtml(
                    bed.room_name || ""
                )}
            </td>

            <td>
                ${escapeHtml(
                    bed.bed_type || ""
                )}
            </td>

            <td>
                ${escapeHtml(
                    bedPriceDisplay
                )}
            </td>

            <td>
                <span class="status-badge ${statusClass}">
                    ${escapeHtml(
                        bed.status || ""
                    )}
                </span>
            </td>

            <td>
                ${escapeHtml(
                    bed.created_at || "—"
                )}
            </td>

        `;


        tableBody.prepend(row);

        updateBedCount();
    }


    // =====================================================
    // COUNT
    // =====================================================

    function updateBedCount() {

        const tableBody =
            document.getElementById(
                "bedTableBody"
            );

        const countElement =
            document.querySelector(
                ".bed-count"
            );

        if (
            !tableBody ||
            !countElement
        ) {
            return;
        }


        const count =
            tableBody.querySelectorAll(
                "tr"
            ).length;


        countElement.textContent =
            count +
            " Bed" +
            (count !== 1 ? "s" : "");
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
        "BED SETUP EVENT HANDLERS READY"
    );

})();