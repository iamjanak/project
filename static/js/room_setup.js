    function initRoomSetup() {

        console.log("ROOM SETUP JS INITIALIZING");


        // =====================================================
        // ELEMENTS
        // =====================================================

        const formCard =
            document.getElementById("roomFormCard");

        const form =
            document.getElementById("roomForm");

        const openBtn =
            document.getElementById("openRoomFormBtn");

        const closeBtn =
            document.getElementById("closeRoomFormBtn");

        const cancelBtn =
            document.getElementById("cancelRoomBtn");

        const saveBtn =
            document.getElementById("saveRoomBtn");


        // =====================================================
        // SAFETY CHECK
        // =====================================================

        if (!form || !formCard) {

            console.warn(
                "ROOM SETUP ELEMENTS NOT FOUND"
            );

            return;

        }


        // =====================================================
        // OPEN ROOM FORM
        // =====================================================

        function openRoomForm() {

            console.log("OPEN ROOM FORM");


            formCard.style.display =
                "block";


            if (openBtn) {

                openBtn.style.display =
                    "none";

            }


            setTimeout(function () {

                formCard.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });

            }, 50);


            const ward =
                document.getElementById(
                    "roomWard"
                );


            if (ward) {

                setTimeout(function () {

                    ward.focus();

                }, 200);

            }

        }


        // =====================================================
        // CLOSE ROOM FORM
        // =====================================================

        function closeRoomForm() {

            console.log(
                "CLOSING ROOM FORM"
            );


            formCard.style.display =
                "none";


            if (openBtn) {

                openBtn.style.display =
                    "inline-flex";

            }


            form.reset();


            const status =
                document.getElementById(
                    "roomStatus"
                );


            if (status) {

                status.value =
                    "Active";

            }

        }


        // =====================================================
        // SUCCESS POPUP
        // =====================================================

        function showRoomSuccess(
            message
        ) {

            const successPopup =
                document.getElementById(
                    "roomSuccessPopup"
                );

            const errorPopup =
                document.getElementById(
                    "roomErrorPopup"
                );

            const successMessage =
                document.getElementById(
                    "roomSuccessMessage"
                );


            if (errorPopup) {

                errorPopup.classList.remove(
                    "show"
                );

            }


            if (successMessage) {

                successMessage.textContent =
                    message ||
                    "Room added successfully.";

            }


            if (successPopup) {

                successPopup.classList.add(
                    "show"
                );


                setTimeout(function () {

                    successPopup.classList.remove(
                        "show"
                    );

                }, 4000);

            }

        }


        // =====================================================
        // ERROR POPUP
        // =====================================================

        function showRoomError(
            message
        ) {

            const successPopup =
                document.getElementById(
                    "roomSuccessPopup"
                );

            const errorPopup =
                document.getElementById(
                    "roomErrorPopup"
                );

            const errorMessage =
                document.getElementById(
                    "roomErrorMessage"
                );


            if (successPopup) {

                successPopup.classList.remove(
                    "show"
                );

            }


            if (errorMessage) {

                errorMessage.textContent =
                    message ||
                    "Unable to complete the request.";

            }


            if (errorPopup) {

                errorPopup.classList.add(
                    "show"
                );

            }


            console.error(
                "ROOM ERROR:",
                message
            );

        }


        // =====================================================
        // CLOSE POPUPS
        // =====================================================

        document
            .querySelectorAll(
                ".room-popup-close"
            )
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


                        if (popup) {

                            popup.classList.remove(
                                "show"
                            );

                        }

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

                    openRoomForm();

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

                    closeRoomForm();

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

                    closeRoomForm();

                }
            );

        }


        // =====================================================
        // FORM SUBMISSION
        // =====================================================

        form.addEventListener(
            "submit",
            async function (event) {

                event.preventDefault();


                console.log(
                    "ROOM FORM SUBMITTED"
                );


                // =================================================
                // GET ELEMENTS
                // =================================================

                const wardElement =
                    form.elements["ward_id"];

                const roomCodeElement =
                    form.elements["room_code"];

                const roomNameElement =
                    form.elements["room_name"];

                const roomTypeElement =
                    form.elements["room_type"];

                const floorElement =
                    form.elements["floor"];

                const statusElement =
                    form.elements["status"];

                const descriptionElement =
                    form.elements["description"];


                // =================================================
                // WARD VALIDATION
                // =================================================

                if (!wardElement) {

                    showRoomError(
                        "Ward field was not found."
                    );

                    return;

                }


                const wardId =
                    String(
                        wardElement.value || ""
                    ).trim();


                if (!wardId) {

                    showRoomError(
                        "Please select a ward."
                    );

                    wardElement.focus();

                    return;

                }


                const numericWardId =
                    Number(wardId);


                if (
                    !Number.isInteger(
                        numericWardId
                    ) ||
                    numericWardId <= 0
                ) {

                    showRoomError(
                        "Invalid ward selected."
                    );

                    wardElement.focus();

                    return;

                }


                // =================================================
                // GET VALUES
                // =================================================

                const roomCode =
                    roomCodeElement
                        ? roomCodeElement.value.trim()
                        : "";


                const roomName =
                    roomNameElement
                        ? roomNameElement.value.trim()
                        : "";


                const roomType =
                    roomTypeElement
                        ? roomTypeElement.value.trim()
                        : "";


                const floor =
                    floorElement
                        ? floorElement.value.trim()
                        : "";


                const status =
                    statusElement
                        ? statusElement.value.trim()
                        : "Active";


                const description =
                    descriptionElement
                        ? descriptionElement.value.trim()
                        : "";


                // =================================================
                // VALIDATE ROOM CODE
                // =================================================

                if (!roomCode) {

                    showRoomError(
                        "Room code is required."
                    );

                    if (roomCodeElement) {

                        roomCodeElement.focus();

                    }

                    return;

                }


                // =================================================
                // VALIDATE ROOM NAME
                // =================================================

                if (!roomName) {

                    showRoomError(
                        "Room name is required."
                    );

                    if (roomNameElement) {

                        roomNameElement.focus();

                    }

                    return;

                }


                // =================================================
                // VALIDATE ROOM TYPE
                // =================================================

                if (!roomType) {

                    showRoomError(
                        "Please select a room type."
                    );

                    if (roomTypeElement) {

                        roomTypeElement.focus();

                    }

                    return;

                }


                // =================================================
                // ROOM DATA
                // =================================================

                const roomData = {

                    ward_id:
                        numericWardId,

                    room_code:
                        roomCode,

                    room_name:
                        roomName,

                    room_type:
                        roomType,

                    floor:
                        floor,

                    status:
                        status || "Active",

                    description:
                        description

                };


                console.log(
                    "ROOM DATA:",
                    roomData
                );


                // =================================================
                // DISABLE SAVE BUTTON
                // =================================================

                const originalText =
                    saveBtn
                        ? saveBtn.textContent
                        : "Save Room";


                if (saveBtn) {

                    saveBtn.disabled =
                        true;

                    saveBtn.textContent =
                        "Saving...";

                }


                // =================================================
                // SEND REQUEST
                // =================================================

                try {

                    const response =
                        await fetch(
                            "/room/add",
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
                                        roomData
                                    )

                            }
                        );


                    console.log(
                        "ROOM SERVER STATUS:",
                        response.status
                    );


                    // =================================================
                    // READ RESPONSE
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
                            "NON-JSON RESPONSE:",
                            text
                        );


                        showRoomError(
                            "Unable to connect to the server."
                        );


                        return;

                    }


                    const data =
                        await response.json();


                    console.log(
                        "ROOM SERVER DATA:",
                        data
                    );


                    // =================================================
                    // SERVER ERROR
                    // =================================================

                    if (
                        !response.ok ||
                        data.success !== true
                    ) {

                        showRoomError(
                            data.message ||
                            data.error ||
                            "Unable to add room."
                        );


                        return;

                    }


                    // =================================================
                    // SUCCESS
                    // =================================================

                    showRoomSuccess(
                        data.message ||
                        "Room added successfully."
                    );


                    // =================================================
                    // ADD ROW
                    // =================================================

                    if (data.room) {

                        addRoomToTable(
                            data.room
                        );

                    }


                    // =================================================
                    // RESET FORM
                    // =================================================

                    form.reset();


                    const status =
                        document.getElementById(
                            "roomStatus"
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
                        "ROOM REQUEST ERROR:",
                        error
                    );


                    showRoomError(
                        error.message ||
                        "Unable to connect to the server."
                    );

                } finally {

                    if (saveBtn) {

                        saveBtn.disabled =
                            false;

                        saveBtn.textContent =
                            originalText;

                    }

                }

            }
        );


        // =====================================================
        // ADD ROOM TO TABLE
        // =====================================================

        function addRoomToTable(room) {

            const tableBody =
                document.getElementById(
                    "roomTableBody"
                );


            if (!tableBody) {

                console.error(
                    "ROOM TABLE BODY NOT FOUND"
                );

                return;

            }


            // =================================================
            // REMOVE EMPTY ROW
            // =================================================

            const emptyRow =
                document.getElementById(
                    "emptyRoomRow"
                );


            if (emptyRow) {

                emptyRow.remove();

            }


            // =================================================
            // ROW NUMBER
            // =================================================

            const rowNumber =
                tableBody.querySelectorAll(
                    "tr"
                ).length + 1;


            // =================================================
            // STATUS CLASS
            // =================================================

            let statusClass =
                "inactive";


            if (room.status === "Active") {

                statusClass =
                    "active";

            } else if (
                room.status === "Maintenance"
            ) {

                statusClass =
                    "maintenance";

            }


            // =================================================
            // CREATE ROW
            // =================================================

            const row =
                document.createElement(
                    "tr"
                );


            row.innerHTML = `

                <td>
                    ${rowNumber}
                </td>

                <td>
                    <span class="room-code">
                        ${escapeHtml(
                            room.room_code
                        )}
                    </span>
                </td>

                <td>
                    <strong>
                        ${escapeHtml(
                            room.room_name
                        )}
                    </strong>
                </td>

                <td>
                    ${escapeHtml(
                        room.room_type || ""
                    )}
                </td>

                <td>
                    ${escapeHtml(
                        room.ward_name || ""
                    )}
                </td>

                <td>
                    ${
                        room.floor
                            ? escapeHtml(
                                room.floor
                            )
                            : "—"
                    }
                </td>

                <td>
                    <span class="status-badge ${statusClass}">
                        ${escapeHtml(
                            room.status || ""
                        )}
                    </span>
                </td>

                <td>
                    ${
                        room.created_at ||
                        "—"
                    }
                </td>

            `;


            tableBody.prepend(
                row
            );


            updateRoomCount();

        }


        // =====================================================
        // UPDATE ROOM COUNT
        // =====================================================

        function updateRoomCount() {

            const tableBody =
                document.getElementById(
                    "roomTableBody"
                );


            const countElement =
                document.querySelector(
                    ".room-count"
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
                " Room" +
                (
                    count !== 1
                        ? "s"
                        : ""
                );

        }


        // =====================================================
        // HTML ESCAPE
        // =====================================================

        function escapeHtml(value) {

            if (
                value === null ||
                value === undefined
            ) {

                return "";

            }


            return String(value)
                .replace(
                    /&/g,
                    "&amp;"
                )
                .replace(
                    /</g,
                    "&lt;"
                )
                .replace(
                    />/g,
                    "&gt;"
                )
                .replace(
                    /"/g,
                    "&quot;"
                )
                .replace(
                    /'/g,
                    "&#039;"
                );

        }


        console.log(
            "ROOM SETUP EVENT HANDLERS READY"
        );

    }


    // =========================================================
    // INITIAL PAGE LOAD
    // =========================================================

    if (
        document.readyState ===
        "loading"
    ) {

        document.addEventListener(
            "DOMContentLoaded",
            initRoomSetup,
            {
                once: true
            }
        );

    } else {

        initRoomSetup();

    }


    // =========================================================
    // AJAX PAGE LOAD
    // =========================================================

    document.addEventListener(
        "page:loaded",
        function () {

            if (
                document.getElementById(
                    "roomForm"
                )
            ) { 

                initRoomSetup();

            }

        }
    );