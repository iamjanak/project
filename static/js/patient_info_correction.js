"use strict";

/* =========================================================
   GLOBAL
========================================================= */

let currentPatientNo = "";
let currentPatientDepartment = "";


/* =========================================================
   INITIALIZE
========================================================= */

function initPatientCorrection() {

    const searchButton =
        document.getElementById("searchPatientBtn");

    const saveButton =
        document.getElementById("saveCorrectionBtn");

    const clearButton =
        document.getElementById("clearBtn");

    const patientNoInput =
        document.getElementById("patientNo");

    const departmentSelect =
        document.getElementById("department");


    /* -----------------------------------------------------
       SEARCH BUTTON
    ----------------------------------------------------- */

    if (
        searchButton &&
        searchButton.dataset.initialized !== "true"
    ) {

        searchButton.addEventListener(
            "click",
            function (event) {

                event.preventDefault();

                searchPatient();

            }
        );

        searchButton.dataset.initialized = "true";
    }


    /* -----------------------------------------------------
       SAVE BUTTON
    ----------------------------------------------------- */

    if (
        saveButton &&
        saveButton.dataset.initialized !== "true"
    ) {

        saveButton.addEventListener(
            "click",
            function (event) {

                event.preventDefault();

                saveCorrection();

            }
        );

        saveButton.dataset.initialized = "true";
    }


    /* -----------------------------------------------------
       CLEAR BUTTON
    ----------------------------------------------------- */

    if (
        clearButton &&
        clearButton.dataset.initialized !== "true"
    ) {

        clearButton.addEventListener(
            "click",
            function (event) {

                event.preventDefault();

                resetCorrectionForm();

            }
        );

        clearButton.dataset.initialized = "true";
    }


    /* -----------------------------------------------------
       ENTER KEY
    ----------------------------------------------------- */

    if (
        patientNoInput &&
        patientNoInput.dataset.initialized !== "true"
    ) {

        patientNoInput.addEventListener(
            "keydown",
            function (event) {

                if (event.key === "Enter") {

                    event.preventDefault();

                    searchPatient();

                }

            }
        );

        patientNoInput.dataset.initialized = "true";
    }


    /* -----------------------------------------------------
       DEPARTMENT CHANGE
       
       When department changes:
       ONLY doctors from that department are loaded.
    ----------------------------------------------------- */

    if (
        departmentSelect &&
        departmentSelect.dataset.initialized !== "true"
    ) {

        departmentSelect.addEventListener(
            "change",
            function () {

                const department =
                    departmentSelect.value.trim();

                currentPatientDepartment =
                    department;

                loadDoctors(
                    department
                );

            }
        );

        departmentSelect.dataset.initialized = "true";
    }

}


/* =========================================================
   NORMAL PAGE LOAD
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    initPatientCorrection
);


/* =========================================================
   AJAX PAGE LOAD
========================================================= */

if (document.readyState !== "loading") {

    initPatientCorrection();

}


/* =========================================================
   SEARCH PATIENT
========================================================= */

async function searchPatient() {

    const patientNoInput =
        document.getElementById("patientNo");


    if (!patientNoInput) {

        console.error(
            "Patient number input was not found."
        );

        return;
    }


    const patientNo =
        patientNoInput.value.trim();


    if (!patientNo) {

        showError(
            "Please enter a hospital number."
        );

        patientNoInput.focus();

        return;
    }


    setSearchLoading(true);


    try {

        const url =
            `/patient_correction/fetch_patient_for_correction/${encodeURIComponent(patientNo)}`;


        console.log(
            "Searching patient:",
            url
        );


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


        console.log(
            "Patient search status:",
            response.status
        );


        const responseText =
            await response.text();


        let data = null;


        try {

            data =
                JSON.parse(responseText);

        } catch (jsonError) {

            console.error(
                "Server did not return JSON:",
                responseText
            );


            throw new Error(
                `Server returned HTTP ${response.status}. Expected JSON.`
            );

        }


        if (!response.ok) {

            console.error(
                "Patient search server error:",
                data
            );


            showError(
                data.message ||
                `Server error (${response.status}).`
            );

            hidePatientDetails();

            return;
        }


        if (!data.success) {

            showError(
                data.message ||
                "Patient not found."
            );

            hidePatientDetails();

            return;
        }


        const patient =
            data.patient;


        if (!patient) {

            showError(
                "Patient information was not returned by the server."
            );

            hidePatientDetails();

            return;
        }


        console.log(
            "Patient found:",
            patient
        );


        currentPatientNo =
            patient.patient_no;


        /* -------------------------------------------------
           SAVE CURRENT DEPARTMENT
        ------------------------------------------------- */

        currentPatientDepartment =
            String(
                patient.department || ""
            ).trim();


        /* -------------------------------------------------
           POPULATE PATIENT FORM
        ------------------------------------------------- */

        populatePatientForm(
            patient
        );


        showPatientDetails();


        /* -------------------------------------------------
           LOAD CORRECTION HISTORY
        ------------------------------------------------- */

        await loadCorrectionHistory(
            patient.patient_no
        );


    } catch (error) {

        console.error(
            "Patient search error:",
            error
        );


        showError(
            error.message ||
            "Unable to connect to the server."
        );


    } finally {

        setSearchLoading(false);

    }

}


/* =========================================================
   POPULATE PATIENT FORM
========================================================= */

async function populatePatientForm(
    patient
) {

    const patientId =
        document.getElementById("patientId");

    const displayPatientNo =
        document.getElementById("displayPatientNo");

    const fullName =
        document.getElementById("fullName");

    const dob =
        document.getElementById("dob");

    const age =
        document.getElementById("age");

    const gender =
        document.getElementById("gender");

    const phone =
        document.getElementById("phone");

    const address =
        document.getElementById("address");

    const department =
        document.getElementById("department");

    const doctor =
        document.getElementById("doctor");

    const createdAt =
        document.getElementById("createdAt");

    const updatedAt =
        document.getElementById("updatedAt");

    const reason =
        document.getElementById("reason");


    if (patientId) {

        patientId.value =
            patient.id || "";

    }


    if (displayPatientNo) {

        displayPatientNo.textContent =
            patient.patient_no || "—";

    }


    if (fullName) {

        fullName.value =
            patient.full_name || "";

    }


    if (dob) {

        dob.value =
            patient.dob || "";

    }


    if (age) {

        age.value =
            patient.age ?? "";

    }


    if (gender) {

        setSelectValue(
            "gender",
            patient.gender
        );

    }


    if (phone) {

        phone.value =
            patient.phone || "";

    }


    if (address) {

        address.value =
            patient.address || "";

    }


    /* -----------------------------------------------------
       DEPARTMENT
    ----------------------------------------------------- */

    setSelectValue(
        "department",
        patient.department
    );


    currentPatientDepartment =
        String(
            patient.department || ""
        ).trim();


    /* -----------------------------------------------------
       DOCTOR

       IMPORTANT:
       First load doctors belonging to the patient's
       department, then select the patient's doctor.
    ----------------------------------------------------- */

    await loadDoctors(
        currentPatientDepartment,
        patient.doctor
    );


    if (createdAt) {

        createdAt.textContent =
            patient.created_at || "—";

    }


    if (updatedAt) {

        updatedAt.textContent =
            patient.updated_at || "—";

    }


    if (reason) {

        reason.value = "";

    }

}


/* =========================================================
   SET SELECT VALUE
========================================================= */

function setSelectValue(
    elementId,
    value
) {

    const select =
        document.getElementById(
            elementId
        );


    if (!select) {

        return;

    }


    const normalizedValue =
        String(value || "")
            .trim()
            .toLowerCase();


    let matched = false;


    Array.from(
        select.options
    ).forEach(
        function (option) {

            const optionValue =
                String(option.value || "")
                    .trim()
                    .toLowerCase();


            if (
                optionValue ===
                normalizedValue
            ) {

                select.value =
                    option.value;

                matched = true;

            }

        }
    );


    if (!matched) {

        select.value = "";

    }

}


/* =========================================================
   LOAD DOCTORS BY DEPARTMENT
========================================================= */

async function loadDoctors(
    departmentName = "",
    selectedDoctor = ""
) {

    const doctorSelect =
        document.getElementById("doctor");


    if (!doctorSelect) {

        return;

    }


    departmentName =
        String(
            departmentName || ""
        ).trim();


    selectedDoctor =
        String(
            selectedDoctor || ""
        ).trim();


    /* -----------------------------------------------------
       RESET DOCTOR DROPDOWN
    ----------------------------------------------------- */

    doctorSelect.innerHTML = `
        <option value="">
            Select Doctor
        </option>
    `;


    doctorSelect.disabled = true;


    /* -----------------------------------------------------
       NO DEPARTMENT
    ----------------------------------------------------- */

    if (!departmentName) {

        doctorSelect.innerHTML = `
            <option value="">
                Select Department First
            </option>
        `;

        return;
    }


    /* -----------------------------------------------------
       LOADING
    ----------------------------------------------------- */

    doctorSelect.innerHTML = `
        <option value="">
            Loading doctors...
        </option>
    `;


    try {

        /*
         * IMPORTANT:
         *
         * Send the selected department to Flask.
         *
         * Example:
         *
         * /fetch_doctors?department=emr2
         */

        const url =
            `/patient_correction/fetch_doctors?department=${encodeURIComponent(departmentName)}`;


        console.log(
            "Loading doctors for department:",
            departmentName
        );


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


        let data = null;


        try {

            data =
                JSON.parse(responseText);

        } catch (jsonError) {

            console.error(
                "Doctor response was not JSON:",
                responseText
            );

            throw new Error(
                `Doctor request returned HTTP ${response.status}.`
            );

        }


        if (!response.ok) {

            console.error(
                "Doctor loading HTTP error:",
                response.status,
                data
            );


            doctorSelect.innerHTML = `
                <option value="">
                    Unable to load doctors
                </option>
            `;

            return;
        }


        if (!data.success) {

            console.error(
                "Doctor loading failed:",
                data.message
            );


            doctorSelect.innerHTML = `
                <option value="">
                    No doctors available
                </option>
            `;

            return;
        }


        /* -------------------------------------------------
           GET DOCTORS
        ------------------------------------------------- */

        const doctors =
            Array.isArray(data.doctors)
                ? data.doctors
                : [];


        doctorSelect.innerHTML = `
            <option value="">
                Select Doctor
            </option>
        `;


        /* -------------------------------------------------
           NO DOCTORS
        ------------------------------------------------- */

        if (doctors.length === 0) {

            doctorSelect.innerHTML = `
                <option value="">
                    No doctors available
                </option>
            `;

            doctorSelect.disabled = true;

            console.log(
                "No doctors found for department:",
                departmentName
            );

            return;
        }


        /* -------------------------------------------------
           ADD DOCTORS
        ------------------------------------------------- */

        doctors.forEach(
            function (doctor) {

                const option =
                    document.createElement(
                        "option"
                    );


                /*
                 * Backend should return:
                 *
                 * {
                 *     id: 1,
                 *     name: "Doctor Name"
                 * }
                 */

                option.value =
                    doctor.name || "";


                option.textContent =
                    doctor.name || "";


                doctorSelect.appendChild(
                    option
                );

            }
        );


        doctorSelect.disabled = false;


        /* -------------------------------------------------
           RESTORE PATIENT'S CURRENT DOCTOR
        ------------------------------------------------- */

        if (selectedDoctor) {

            setSelectValue(
                "doctor",
                selectedDoctor
            );

        }


        console.log(
            "Doctors loaded:",
            doctors
        );


    } catch (error) {

        console.error(
            "Unable to load doctors:",
            error
        );


        doctorSelect.innerHTML = `
            <option value="">
                Unable to load doctors
            </option>
        `;


        doctorSelect.disabled = true;

    }

}


/* =========================================================
   SAVE CORRECTION
========================================================= */

async function saveCorrection() {

    const patientIdElement =
        document.getElementById(
            "patientId"
        );

    const reasonElement =
        document.getElementById(
            "reason"
        );


    if (!patientIdElement) {

        showError(
            "Patient information is not loaded."
        );

        return;
    }


    const patientId =
        patientIdElement.value.trim();


    const reason =
        reasonElement
            ? reasonElement.value.trim()
            : "";


    if (!patientId) {

        showError(
            "Please search for a patient first."
        );

        return;
    }


    if (!reason) {

        showError(
            "Please enter the reason for correction."
        );

        if (reasonElement) {

            reasonElement.focus();

        }

        return;
    }


    const fullNameElement =
        document.getElementById(
            "fullName"
        );


    const fullName =
        fullNameElement
            ? fullNameElement.value.trim()
            : "";


    if (!fullName) {

        showError(
            "Patient name cannot be empty."
        );

        if (fullNameElement) {

            fullNameElement.focus();

        }

        return;
    }


    const ageElement =
        document.getElementById(
            "age"
        );


    const age =
        ageElement
            ? ageElement.value
            : "";


    if (
        age !== "" &&
        (
            Number(age) < 0 ||
            Number(age) > 150
        )
    ) {

        showError(
            "Please enter a valid age."
        );

        return;
    }


    const payload = {

        patient_id:
            patientId,

        full_name:
            fullName,

        dob:
            document.getElementById(
                "dob"
            )?.value || "",

        age:
            age,

        gender:
            document.getElementById(
                "gender"
            )?.value || "",

        phone:
            document.getElementById(
                "phone"
            )?.value.trim() || "",

        address:
            document.getElementById(
                "address"
            )?.value.trim() || "",

        department:
            document.getElementById(
                "department"
            )?.value || "",

        doctor:
            document.getElementById(
                "doctor"
            )?.value || "",

        reason:
            reason

    };


    setSaveLoading(true);


    try {

        const response =
            await fetch(
                "/patient_correction/save_patient_info_correction",
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
                        JSON.stringify(payload)
                }
            );


        const responseText =
            await response.text();


        let data = null;


        try {

            data =
                JSON.parse(responseText);

        } catch (jsonError) {

            console.error(
                "Save response was not JSON:",
                responseText
            );


            throw new Error(
                `Server returned HTTP ${response.status} instead of JSON.`
            );

        }


        if (!response.ok) {

            showError(
                data.message ||
                `Server error (${response.status}).`
            );

            return;
        }


        if (!data.success) {

            showError(
                data.message ||
                "Unable to save correction."
            );

            return;
        }


        showSuccess(
            data.message ||
            "Patient information corrected successfully."
        );


        await searchPatient();


    } catch (error) {

        console.error(
            "Save correction error:",
            error
        );


        showError(
            error.message ||
            "Unable to connect to the server."
        );


    } finally {

        setSaveLoading(false);

    }

}


/* =========================================================
   LOAD CORRECTION HISTORY
========================================================= */

async function loadCorrectionHistory(
    patientNo
) {

    const historyBody =
        document.getElementById(
            "historyBody"
        );


    if (!historyBody) {

        return;

    }


    historyBody.innerHTML = `
        <tr>
            <td
                colspan="6"
                class="history-loading"
            >
                Loading correction history...
            </td>
        </tr>
    `;


    try {

        const url =
            `/patient_correction/patient_correction_history/${encodeURIComponent(patientNo)}`;


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


        let data = null;


        try {

            data =
                JSON.parse(responseText);

        } catch (jsonError) {

            console.error(
                "History response was not JSON:",
                responseText
            );

            throw new Error(
                `History request returned HTTP ${response.status}.`
            );

        }


        if (!response.ok || !data.success) {

            historyBody.innerHTML = `
                <tr>
                    <td
                        colspan="6"
                        class="history-empty"
                    >
                        ${escapeHtml(
                            data.message ||
                            "Unable to load correction history."
                        )}
                    </td>
                </tr>
            `;

            return;
        }


        if (
            !data.history ||
            data.history.length === 0
        ) {

            historyBody.innerHTML = `
                <tr>
                    <td
                        colspan="6"
                        class="history-empty"
                    >
                        No correction history found.
                    </td>
                </tr>
            `;

            return;
        }


        historyBody.innerHTML = "";


        data.history.forEach(
            function (item) {

                const row =
                    document.createElement("tr");


                row.innerHTML = `

                    <td>
                        ${escapeHtml(
                            item.created_at || "—"
                        )}
                    </td>

                    <td>
                        <span class="field-badge">
                            ${escapeHtml(
                                formatFieldName(
                                    item.field_name
                                )
                            )}
                        </span>
                    </td>

                    <td>
                        ${escapeHtml(
                            item.old_value || "—"
                        )}
                    </td>

                    <td>
                        <span class="new-value">
                            ${escapeHtml(
                                item.new_value || "—"
                            )}
                        </span>
                    </td>

                    <td>
                        ${escapeHtml(
                            item.reason || "—"
                        )}
                    </td>

                    <td>
                        ${escapeHtml(
                            item.corrected_by ||
                            "System"
                        )}
                    </td>

                `;


                historyBody.appendChild(
                    row
                );

            }
        );


    } catch (error) {

        console.error(
            "History error:",
            error
        );


        historyBody.innerHTML = `
            <tr>
                <td
                    colspan="6"
                    class="history-empty"
                >
                    ${escapeHtml(
                        error.message ||
                        "Unable to load correction history."
                    )}
                </td>
            </tr>
        `;

    }

}


/* =========================================================
   RESET FORM
========================================================= */

function resetCorrectionForm() {

    const ids = [
        "patientNo",
        "patientId",
        "fullName",
        "dob",
        "age",
        "gender",
        "phone",
        "address",
        "department",
        "doctor",
        "reason"
    ];


    ids.forEach(
        function (id) {

            const element =
                document.getElementById(id);


            if (element) {

                element.value = "";

            }

        }
    );


    const doctor =
        document.getElementById("doctor");


    if (doctor) {

        doctor.innerHTML = `
            <option value="">
                Select Department First
            </option>
        `;

        doctor.disabled = true;

    }


    const displayPatientNo =
        document.getElementById(
            "displayPatientNo"
        );

    const createdAt =
        document.getElementById(
            "createdAt"
        );

    const updatedAt =
        document.getElementById(
            "updatedAt"
        );


    if (displayPatientNo) {

        displayPatientNo.textContent =
            "—";

    }


    if (createdAt) {

        createdAt.textContent =
            "—";

    }


    if (updatedAt) {

        updatedAt.textContent =
            "—";

    }


    hidePatientDetails();


    currentPatientNo = "";

    currentPatientDepartment = "";


    const patientNo =
        document.getElementById(
            "patientNo"
        );


    if (patientNo) {

        patientNo.focus();

    }

}


/* =========================================================
   SEARCH LOADING
========================================================= */

function setSearchLoading(
    loading
) {

    const button =
        document.getElementById(
            "searchPatientBtn"
        );


    if (!button) {

        return;

    }


    if (loading) {

        button.disabled = true;

        button.innerHTML = `
            <span class="button-spinner"></span>
            <span>Searching...</span>
        `;

    } else {

        button.disabled = false;

        button.innerHTML = `
            <span>Search Patient</span>
        `;

    }

}


/* =========================================================
   SAVE LOADING
========================================================= */

function setSaveLoading(
    loading
) {

    const button =
        document.getElementById(
            "saveCorrectionBtn"
        );


    if (!button) {

        return;

    }


    if (loading) {

        button.disabled = true;

        button.innerHTML = `
            <span class="button-spinner"></span>
            <span>Saving...</span>
        `;

    } else {

        button.disabled = false;

        button.innerHTML = `
            <span>Save Correction</span>
        `;

    }

}


/* =========================================================
   SUCCESS POPUP
========================================================= */

function showSuccess(
    message
) {

    const popup =
        document.getElementById(
            "successPopup"
        );

    const messageElement =
        document.getElementById(
            "successMessage"
        );


    if (!popup) {

        console.log(
            message
        );

        return;

    }


    if (messageElement) {

        messageElement.textContent =
            message;

    }


    hidePopup(
        "errorPopup"
    );


    popup.classList.add(
        "show"
    );


    clearTimeout(
        popup.successTimer
    );


    popup.successTimer =
        setTimeout(
            function () {

                hidePopup(
                    "successPopup"
                );

            },
            4000
        );

}


/* =========================================================
   ERROR POPUP
========================================================= */

function showError(
    message
) {

    const popup =
        document.getElementById(
            "errorPopup"
        );

    const messageElement =
        document.getElementById(
            "errorMessage"
        );


    console.error(
        "Patient Correction:",
        message
    );


    if (!popup) {

        alert(message);

        return;

    }


    if (messageElement) {

        messageElement.textContent =
            message;

    }


    hidePopup(
        "successPopup"
    );


    popup.classList.add(
        "show"
    );


    clearTimeout(
        popup.errorTimer
    );


    popup.errorTimer =
        setTimeout(
            function () {

                hidePopup(
                    "errorPopup"
                );

            },
            5000
        );

}


/* =========================================================
   HIDE POPUP
========================================================= */

function hidePopup(
    popupId
) {

    const popup =
        document.getElementById(
            popupId
        );


    if (!popup) {

        return;

    }


    popup.classList.remove(
        "show"
    );

}


/* =========================================================
   FORMAT FIELD NAME
========================================================= */

function formatFieldName(
    field
) {

    if (!field) {

        return "—";

    }


    return String(field)
        .replaceAll(
            "_",
            " "
        )
        .replace(
            /\b\w/g,
            function (character) {

                return character.toUpperCase();

            }
        );

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

/* =========================================================
   SHOW PATIENT DETAILS
========================================================= */

function showPatientDetails() {

    const patientDetails =
        document.getElementById(
            "patientDetails"
        );

    const historyCard =
        document.getElementById(
            "historyCard"
        );


    if (patientDetails) {

        patientDetails.style.display =
            "block";


        setTimeout(
            function () {

                patientDetails.classList.add(
                    "visible"
                );

            },
            10
        );

    }


    if (historyCard) {

        historyCard.style.display =
            "block";

    }

}


/* =========================================================
   HIDE PATIENT DETAILS
========================================================= */

function hidePatientDetails() {

    const patientDetails =
        document.getElementById(
            "patientDetails"
        );

    const historyCard =
        document.getElementById(
            "historyCard"
        );


    if (patientDetails) {

        patientDetails.style.display =
            "none";

        patientDetails.classList.remove(
            "visible"
        );

    }


    if (historyCard) {

        historyCard.style.display =
            "none";

    }

}