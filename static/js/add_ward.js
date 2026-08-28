document.addEventListener("DOMContentLoaded", function () {

    console.log("=================================");
    console.log("ADD WARD JS LOADED");
    console.log("=================================");


    // =====================================================
    // ELEMENTS
    // =====================================================

    const form =
        document.getElementById("wardForm");

    const saveButton =
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
    // CHECK FORM
    // =====================================================

    if (!form) {

        console.error(
            "ADD WARD: wardForm NOT FOUND"
        );

        return;
    }


    // =====================================================
    // SAVE URL
    // =====================================================

    const saveUrl =
        window.SAVE_WARD_URL ||
        "/ward/save";


    console.log(
        "WARD SAVE URL:",
        saveUrl
    );


    // =====================================================
    // POPUP HELPERS
    // =====================================================

    function hidePopup(popup) {

        if (!popup) {
            return;
        }

        popup.style.display = "none";
        popup.classList.remove("show");
    }


    function showSuccess(message) {

        if (successMessage) {

            successMessage.textContent =
                message ||
                "Ward added successfully.";
        }


        hidePopup(errorPopup);


        if (successPopup) {

            successPopup.style.display = "flex";
            successPopup.classList.add("show");

        }

    }


    function showError(message) {

        if (errorMessage) {

            errorMessage.textContent =
                message ||
                "Unable to complete the request.";

        }


        hidePopup(successPopup);


        if (errorPopup) {

            errorPopup.style.display = "flex";
            errorPopup.classList.add("show");

        }


        console.error(
            "WARD SAVE ERROR:",
            message
        );

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
                        button.getAttribute(
                            "data-popup"
                        );

                    const popup =
                        document.getElementById(
                            popupId
                        );

                    hidePopup(popup);

                }
            );

        });


    // =====================================================
    // FORM SUBMIT
    // =====================================================

    form.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();


            console.log(
                "================================="
            );

            console.log(
                "WARD FORM SUBMITTED"
            );

            console.log(
                "================================="
            );


            // =================================================
            // GET ELEMENTS
            // =================================================

            const wardCodeElement =
                document.getElementById("wardCode");

            const wardNameElement =
                document.getElementById("wardName");

            const wardTypeElement =
                document.getElementById("wardType");

            const wardFloorElement =
                document.getElementById("wardFloor");

            const wardStatusElement =
                document.getElementById("wardStatus");

            const wardDescriptionElement =
                document.getElementById(
                    "wardDescription"
                );


            // =================================================
            // CHECK ELEMENTS
            // =================================================

            if (
                !wardCodeElement ||
                !wardNameElement ||
                !wardTypeElement ||
                !wardFloorElement ||
                !wardStatusElement ||
                !wardDescriptionElement
            ) {

                showError(
                    "Ward form fields are missing."
                );

                console.error(
                    "One or more ward form elements were not found."
                );

                return;
            }


            // =================================================
            // GET VALUES
            // =================================================

            const wardCode =
                wardCodeElement.value.trim();

            const wardName =
                wardNameElement.value.trim();

            const wardType =
                wardTypeElement.value.trim();

            const floor =
                wardFloorElement.value.trim();

            const status =
                wardStatusElement.value.trim() ||
                "Active";

            const description =
                wardDescriptionElement.value.trim();


            // =================================================
            // VALIDATION
            // =================================================

            if (!wardCode) {

                showError(
                    "Ward code is required."
                );

                wardCodeElement.focus();

                return;
            }


            if (!wardName) {

                showError(
                    "Ward name is required."
                );

                wardNameElement.focus();

                return;
            }


            if (!wardType) {

                showError(
                    "Ward type is required."
                );

                wardTypeElement.focus();

                return;
            }


            // =================================================
            // DATA
            // =================================================

            const data = {

                ward_code:
                    wardCode,

                ward_name:
                    wardName,

                ward_type:
                    wardType,

                floor:
                    floor,

                status:
                    status,

                description:
                    description

            };


            console.log(
                "WARD DATA:",
                data
            );


            console.log(
                "POSTING TO:",
                saveUrl
            );


            // =================================================
            // DISABLE SAVE BUTTON
            // =================================================

            if (saveButton) {

                saveButton.disabled = true;

                saveButton.dataset.originalText =
                    saveButton.textContent;

                saveButton.textContent =
                    "Saving...";

            }


            // =================================================
            // SEND TO FLASK
            // =================================================

            try {

                const response =
                    await fetch(
                        saveUrl,
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
                    "WARD SERVER STATUS:",
                    response.status
                );


                // =================================================
                // READ CONTENT TYPE
                // =================================================

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
                        "NON JSON RESPONSE:",
                        text
                    );


                    if (response.status === 405) {

                        showError(
                            "Save Ward request method is not allowed. Please check the Ward save route."
                        );

                    } else if (
                        response.status === 401
                    ) {

                        showError(
                            "Your session has expired. Please login again."
                        );

                    } else if (
                        response.status === 404
                    ) {

                        showError(
                            "Ward save URL was not found."
                        );

                    } else {

                        showError(
                            "Unable to connect to the server."
                        );

                    }

                    return;
                }


                // =================================================
                // JSON RESPONSE
                // =================================================

                const result =
                    await response.json();


                console.log(
                    "WARD SERVER RESPONSE:",
                    result
                );


                // =================================================
                // SERVER ERROR
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


                console.log(
                    "WARD SAVED SUCCESSFULLY"
                );


                // =================================================
                // RESET FORM
                // =================================================

                form.reset();


                wardStatusElement.value =
                    "Active";


                // =================================================
                // REDIRECT
                // =================================================

                setTimeout(
                    function () {

                        window.location.href =
                            result.redirect ||
                            "/ward/ward_setup";

                    },
                    1000
                );

            }


            // =================================================
            // FETCH ERROR
            // =================================================

            catch (error) {

                console.error(
                    "WARD FETCH ERROR:",
                    error
                );


                showError(
                    "Unable to connect to the server."
                );

            }


            // =================================================
            // ENABLE BUTTON
            // =================================================

            finally {

                if (saveButton) {

                    saveButton.disabled =
                        false;

                    saveButton.textContent =
                        saveButton.dataset.originalText ||
                        "Save Ward";

                }

            }

        }
    );


    console.log(
        "ADD WARD EVENT HANDLER READY"
    );

});