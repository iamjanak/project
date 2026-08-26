(function () {

    "use strict";

    // =========================================================
    // FOLLOW-UP INITIALIZATION
    // =========================================================

    function initFollowupPage() {

        console.log("Initializing Follow-Up page...");

        const patientNoInput =
            document.getElementById("patientNo");

        const searchBtn =
            document.getElementById("searchPatientBtn");

        const patientMessage =
            document.getElementById("patientMessage");

        const patientInfoCard =
            document.getElementById("patientInfoCard");

        const followupFormCard =
            document.getElementById("followupFormCard");

        const historyCard =
            document.getElementById("historyCard");

        const patientId =
            document.getElementById("patientId");

        const department =
            document.getElementById("department");

        const doctor =
            document.getElementById("doctor");

        const form =
            document.getElementById("followupForm");


        // =========================================================
        // FOLLOW-UP PAGE NOT PRESENT
        // =========================================================

        if (!patientNoInput || !searchBtn) {

            console.log(
                "Follow-Up page elements not found."
            );

            return;
        }


        console.log(
            "Follow-Up page elements found."
        );


        // =========================================================
        // PREVENT DUPLICATE INITIALIZATION
        // =========================================================

        if (
            searchBtn.dataset.followupInitialized === "true"
        ) {

            console.log(
                "Follow-Up already initialized."
            );

            return;
        }


        searchBtn.dataset.followupInitialized = "true";


        // =========================================================
        // SEARCH BUTTON
        // =========================================================

        searchBtn.addEventListener(
            "click",
            function (event) {

                event.preventDefault();

                console.log(
                    "Search Patient button clicked."
                );

                searchPatient();

            }
        );


        // =========================================================
        // ENTER KEY
        // =========================================================

        patientNoInput.addEventListener(
            "keydown",
            function (event) {

                if (event.key === "Enter") {

                    event.preventDefault();

                    searchPatient();

                }

            }
        );


        // =========================================================
        // SEARCH PATIENT
        // =========================================================

        async function searchPatient() {

            const patientNo =
                patientNoInput.value.trim();


            console.log(
                "Searching patient:",
                patientNo
            );


            // -----------------------------------------------------
            // VALIDATION
            // -----------------------------------------------------

            if (!patientNo) {

                showMessage(
                    "Please enter a hospital number.",
                    "error"
                );

                patientNoInput.focus();

                return;
            }


            // -----------------------------------------------------
            // LOADING
            // -----------------------------------------------------

            searchBtn.disabled = true;

            searchBtn.textContent =
                "Searching...";

            showMessage(
                "",
                ""
            );


            try {

                const url =
                    `/fetch_followup_patient/${encodeURIComponent(patientNo)}`;


                console.log(
                    "Request URL:",
                    url
                );


                // -------------------------------------------------
                // REQUEST
                // -------------------------------------------------

                const response =
                    await fetch(
                        url,
                        {
                            method: "GET",

                            headers: {
                                "Accept":
                                    "application/json",

                                "X-Requested-With":
                                    "XMLHttpRequest"
                            },

                            cache: "no-store"
                        }
                    );


                console.log(
                    "Response status:",
                    response.status
                );


                // -------------------------------------------------
                // READ RESPONSE
                // -------------------------------------------------

                const data =
                    await response.json();


                console.log(
                    "Patient API response:",
                    data
                );


                // -------------------------------------------------
                // ERROR
                // -------------------------------------------------

                if (
                    !response.ok ||
                    !data.success
                ) {

                    hidePatientSections();

                    showMessage(
                        data.message ||
                        "Patient not found.",
                        "error"
                    );

                    return;
                }


                // -------------------------------------------------
                // PATIENT CHECK
                // -------------------------------------------------

                if (!data.patient) {

                    hidePatientSections();

                    showMessage(
                        "Patient information was not returned.",
                        "error"
                    );

                    return;
                }


                const patient =
                    data.patient;


                console.log(
                    "Patient found:",
                    patient
                );


                // -------------------------------------------------
                // PATIENT ID
                // -------------------------------------------------

                if (patientId) {

                    patientId.value =
                        patient.id || "";

                }


                // -------------------------------------------------
                // PATIENT INFORMATION
                // -------------------------------------------------

                setText(
                    "patientNoDisplay",
                    patient.patient_no
                );

                setText(
                    "patientName",
                    patient.full_name
                );

                setText(
                    "patientAge",
                    patient.age
                );

                setText(
                    "patientGender",
                    patient.gender
                );

                setText(
                    "patientPhone",
                    patient.phone
                );

                setText(
                    "patientAddress",
                    patient.address
                );

                setText(
                    "currentDepartment",
                    patient.department ||
                    patient.department_name
                );

                setText(
                    "currentDoctor",
                    patient.doctor ||
                    patient.doctor_name
                );


                // -------------------------------------------------
                // SHOW PATIENT SECTIONS
                // -------------------------------------------------

                if (patientInfoCard) {

                    patientInfoCard.style.display =
                        "block";

                }


                if (followupFormCard) {

                    followupFormCard.style.display =
                        "block";

                }


                if (historyCard) {

                    historyCard.style.display =
                        "block";

                }


                // -------------------------------------------------
                // SUCCESS MESSAGE
                // -------------------------------------------------

                showMessage(
                    "Patient found successfully.",
                    "success"
                );


                // -------------------------------------------------
                // RESET DEPARTMENT / DOCTOR
                // -------------------------------------------------

                if (department) {

                    department.value = "";

                }


                if (doctor) {

                    doctor.innerHTML =
                        `
                        <option value="">
                            Select Department First
                        </option>
                        `;

                    doctor.disabled = true;

                }


                // -------------------------------------------------
                // LOAD HISTORY
                // -------------------------------------------------

                await loadHistory(
                    patient.patient_no
                );

            }

            catch (error) {

                console.error(
                    "FOLLOW-UP SEARCH ERROR:",
                    error
                );


                hidePatientSections();


                showMessage(
                    "Unable to connect to the server.",
                    "error"
                );

            }

            finally {

                searchBtn.disabled = false;

                searchBtn.textContent =
                    "Search Patient";

            }

        }


        // =========================================================
        // DEPARTMENT CHANGE
        // =========================================================

        if (department && doctor) {

            department.addEventListener(
                "change",
                async function () {

                    const departmentId =
                        this.value;


                    console.log(
                        "Department selected:",
                        departmentId
                    );


                    doctor.innerHTML =
                        `
                        <option value="">
                            Loading doctors...
                        </option>
                        `;

                    doctor.disabled = true;


                    if (!departmentId) {

                        doctor.innerHTML =
                            `
                            <option value="">
                                Select Department First
                            </option>
                            `;

                        return;
                    }


                    try {

                        const response =
                            await fetch(
                                `/fetch_followup_doctors/${encodeURIComponent(departmentId)}`,
                                {
                                    method: "GET",

                                    headers: {
                                        "Accept":
                                            "application/json",

                                        "X-Requested-With":
                                            "XMLHttpRequest"
                                    },

                                    cache: "no-store"
                                }
                            );


                        const data =
                            await response.json();


                        console.log(
                            "Doctor response:",
                            data
                        );


                        if (
                            !response.ok ||
                            !data.success
                        ) {

                            doctor.innerHTML =
                                `
                                <option value="">
                                    No doctors found
                                </option>
                                `;

                            return;
                        }


                        doctor.innerHTML =
                            `
                            <option value="">
                                Select Doctor
                            </option>
                            `;


                        if (
                            !Array.isArray(data.doctors) ||
                            data.doctors.length === 0
                        ) {

                            doctor.innerHTML =
                                `
                                <option value="">
                                    No active doctors available
                                </option>
                                `;

                            return;
                        }


                        data.doctors.forEach(
                            function (item) {

                                const option =
                                    document.createElement(
                                        "option"
                                    );


                                option.value =
                                    item.id;


                                option.textContent =
                                    item.doc_name ||
                                    item.doctor_name ||
                                    item.name ||
                                    "Doctor";


                                if (
                                    item.specialization
                                ) {

                                    option.textContent +=
                                        ` - ${item.specialization}`;

                                }


                                doctor.appendChild(
                                    option
                                );

                            }
                        );


                        doctor.disabled = false;

                    }

                    catch (error) {

                        console.error(
                            "DOCTOR LOADING ERROR:",
                            error
                        );


                        doctor.innerHTML =
                            `
                            <option value="">
                                Unable to load doctors
                            </option>
                            `;

                        doctor.disabled = true;

                    }

                }
            );

        }


        // =========================================================
        // SAVE FOLLOW-UP
        // =========================================================

        if (form) {

            form.addEventListener(
                "submit",
                async function (event) {

                    event.preventDefault();


                    if (!patientId || !patientId.value) {

                        showMessage(
                            "Please search for a patient first.",
                            "error"
                        );

                        return;
                    }


                    if (!department || !department.value) {

                        showMessage(
                            "Please select a department.",
                            "error"
                        );

                        department.focus();

                        return;
                    }


                    if (!doctor || !doctor.value) {

                        showMessage(
                            "Please select a doctor.",
                            "error"
                        );

                        doctor.focus();

                        return;
                    }


                    const payload = {

                        patient_id:
                            patientId.value,

                        department_id:
                            department.value,

                        doctor_id:
                            doctor.value,

                        visit_type:
                            getValue("visitType"),

                        chief_complaint:
                            getValue("chiefComplaint"),

                        diagnosis:
                            getValue("diagnosis"),

                        treatment:
                            getValue("treatment"),

                        prescription:
                            getValue("prescription"),

                        notes:
                            getValue("notes"),

                        next_followup_date:
                            getValue("nextFollowup")

                    };


                    console.log(
                        "Saving follow-up:",
                        payload
                    );


                    const saveBtn =
                        form.querySelector(
                            'button[type="submit"]'
                        );


                    if (saveBtn) {

                        saveBtn.disabled = true;

                        saveBtn.textContent =
                            "Saving...";

                    }


                    try {

                        const response =
                            await fetch(
                                "/save_followup",
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

                                    body:
                                        JSON.stringify(
                                            payload
                                        )
                                }
                            );


                        const data =
                            await response.json();


                        console.log(
                            "Save response:",
                            data
                        );


                        if (
                            !response.ok ||
                            !data.success
                        ) {

                            showMessage(
                                data.message ||
                                "Unable to save follow-up.",
                                "error"
                            );

                            return;
                        }


                        showSuccessPopup(
                            data.followup_no || ""
                        );


                        // -------------------------------------------------
                        // CLEAR CLINICAL FIELDS
                        // -------------------------------------------------

                        clearValue("chiefComplaint");
                        clearValue("diagnosis");
                        clearValue("treatment");
                        clearValue("prescription");
                        clearValue("notes");
                        clearValue("nextFollowup");


                        // -------------------------------------------------
                        // RELOAD HISTORY
                        // -------------------------------------------------

                        await loadHistory(
                            patientNoInput.value.trim()
                        );

                    }

                    catch (error) {

                        console.error(
                            "SAVE FOLLOW-UP ERROR:",
                            error
                        );


                        showMessage(
                            "Unable to connect to the server.",
                            "error"
                        );

                    }

                    finally {

                        if (saveBtn) {

                            saveBtn.disabled = false;

                            saveBtn.textContent =
                                "Save Follow-Up";

                        }

                    }

                }
            );

        }


        // =========================================================
        // LOAD HISTORY
        // =========================================================

        async function loadHistory(patientNo) {

            if (!patientNo) {
                return;
            }


            try {

                const response =
                    await fetch(
                        `/fetch_followup_history/${encodeURIComponent(patientNo)}`,
                        {
                            method: "GET",

                            headers: {
                                "Accept":
                                    "application/json",

                                "X-Requested-With":
                                    "XMLHttpRequest"
                            },

                            cache: "no-store"
                        }
                    );


                const data =
                    await response.json();


                console.log(
                    "History response:",
                    data
                );


                const historyBody =
                    document.getElementById(
                        "historyBody"
                    );


                if (!historyBody) {
                    return;
                }


                historyBody.innerHTML = "";


                if (
                    !response.ok ||
                    !data.success ||
                    !Array.isArray(data.history) ||
                    data.history.length === 0
                ) {

                    historyBody.innerHTML =
                        `
                        <tr>
                            <td
                                colspan="8"
                                class="empty-history"
                            >
                                No previous follow-up records found.
                            </td>
                        </tr>
                        `;

                    return;
                }


                data.history.forEach(
                    function (item) {

                        const row =
                            document.createElement(
                                "tr"
                            );


                        row.innerHTML =
                            `
                            <td>
                                ${escapeHtml(
                                item.followup_no
                            )}
                            </td>

                            <td>
                                ${escapeHtml(
                                item.visit_date
                            )}
                            </td>

                            <td>
                                ${escapeHtml(
                                item.department ||
                                "-"
                            )}
                            </td>

                            <td>
                                ${escapeHtml(
                                item.doctor ||
                                "-"
                            )}
                            </td>

                            <td>
                                ${escapeHtml(
                                item.visit_type ||
                                "-"
                            )}
                            </td>

                            <td>
                                ${escapeHtml(
                                item.diagnosis ||
                                "-"
                            )}
                            </td>

                            <td>
                                ${escapeHtml(
                                item.next_followup_date ||
                                "-"
                            )}
                            </td>

                            <td>
                                <span class="status-badge">
                                    ${escapeHtml(
                                item.status ||
                                "Active"
                            )}
                                </span>
                            </td>
                            `;


                        historyBody.appendChild(
                            row
                        );

                    }
                );

            }

            catch (error) {

                console.error(
                    "HISTORY LOADING ERROR:",
                    error
                );

            }

        }


        // =========================================================
        // HELPER FUNCTIONS
        // =========================================================

        function getValue(id) {

            const element =
                document.getElementById(id);

            return element
                ? element.value.trim()
                : "";

        }


        function clearValue(id) {

            const element =
                document.getElementById(id);

            if (element) {

                element.value = "";

            }

        }


        function setText(id, value) {

            const element =
                document.getElementById(id);

            if (!element) {
                return;
            }


            element.textContent =
                value !== null &&
                    value !== undefined &&
                    value !== ""
                    ? value
                    : "-";

        }


        function showMessage(message, type) {

            if (!patientMessage) {
                return;
            }


            patientMessage.textContent =
                message;


            patientMessage.className =
                "followup-message";


            if (type) {

                patientMessage.classList.add(
                    type
                );

            }

        }


        function hidePatientSections() {

            if (patientInfoCard) {

                patientInfoCard.style.display =
                    "none";

            }


            if (followupFormCard) {

                followupFormCard.style.display =
                    "none";

            }


            if (historyCard) {

                historyCard.style.display =
                    "none";

            }

        }


        function escapeHtml(value) {

            const div =
                document.createElement(
                    "div"
                );


            div.textContent =
                value ?? "";


            return div.innerHTML;

        }

    }


    // =========================================================
    // INITIALIZATION
    // =========================================================

    function runFollowupInit() {

        // Small delay is important for AJAX page replacement
        setTimeout(
            function () {

                initFollowupPage();

            },
            50
        );

    }


    // Normal page load
    if (
        document.readyState === "loading"
    ) {

        document.addEventListener(
            "DOMContentLoaded",
            runFollowupInit
        );

    } else {

        runFollowupInit();

    }


    // AJAX page load
    document.addEventListener(
        "pageLoaded",
        function () {

            console.log(
                "pageLoaded event detected."
            );

            runFollowupInit();

        }
    );


})();