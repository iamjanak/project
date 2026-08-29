// =====================================================
// ADMIT PATIENT MODULE
//
// Uses EVENT DELEGATION so it keeps working even if this
// module's HTML is swapped in/out without a full page
// reload.
//
// Uses scoped lookups through the nearest ".adm-page"
// container to avoid problems caused by duplicate IDs.
// =====================================================

(function () {

    if (window.__admitPatientDelegationAttached) {
        console.log(
            "Admit Patient delegation already attached, skipping re-attach."
        );
        return;
    }

    window.__admitPatientDelegationAttached = true;

    console.log("=================================");
    console.log("ADMIT PATIENT JS LOADED");
    console.log("=================================");


    // =====================================================
    // FIND THE CORRECT MODULE CONTAINER
    // =====================================================

    function getRoot(startEl) {

        if (
            startEl &&
            typeof startEl.closest === "function"
        ) {

            const container =
                startEl.closest(".adm-page");

            if (container) {
                return container;
            }
        }

        return document;
    }


    function q(root, id) {

        return root.querySelector(`#${id}`);

    }


    // =====================================================
    // CHECK ADMISSION FORM READY
    // =====================================================

    function checkAdmissionReady(root) {

        const patientIdInput =
            q(root, "patientId");

        const departmentSelect =
            q(root, "department");

        const wardSelect =
            q(root, "ward");

        const roomSelect =
            q(root, "room");

        const bedSelect =
            q(root, "bed");

        const admitPatientBtn =
            q(root, "admitPatientBtn");


        if (
            !patientIdInput ||
            !departmentSelect ||
            !wardSelect ||
            !roomSelect ||
            !bedSelect ||
            !admitPatientBtn
        ) {
            return;
        }


        admitPatientBtn.disabled =
            !patientIdInput.value ||
            !departmentSelect.value ||
            !wardSelect.value ||
            !roomSelect.value ||
            !bedSelect.value;

    }


    // =====================================================
    // PROFESSIONAL SUCCESS MODAL
    // =====================================================

    function showAdmissionSuccess(admissionNo) {

        // Remove existing modal if one somehow exists
        const existingModal =
            document.getElementById(
                "admissionSuccessModal"
            );

        if (existingModal) {
            existingModal.remove();
        }


        const modal =
            document.createElement("div");

        modal.id =
            "admissionSuccessModal";

        modal.className =
            "admission-success-overlay";


        modal.innerHTML = `

            <div
                class="admission-success-modal"
                role="dialog"
                aria-modal="true"
                aria-labelledby="admissionSuccessTitle"
            >

                <!-- SUCCESS ICON -->

                <div class="admission-success-icon">

                    <span>✓</span>

                </div>


                <!-- TITLE -->

                <h3 id="admissionSuccessTitle">
                    Patient Admitted Successfully
                </h3>


                <!-- MESSAGE -->

                <p class="admission-success-message">
                    The patient has been successfully
                    admitted to the hospital.
                </p>


                <!-- ADMISSION NUMBER -->

                <div class="admission-success-number">

                    <span>
                        Admission Number
                    </span>

                    <strong>
                        ${admissionNo || "—"}
                    </strong>

                </div>


                <!-- CONTINUE BUTTON -->

                <button
                    type="button"
                    class="admission-success-btn"
                    id="admissionSuccessContinueBtn"
                >
                    Continue
                </button>

            </div>

        `;


        document.body.appendChild(modal);


        // =================================================
        // CONTINUE BUTTON
        // =================================================

        const continueBtn =
            document.getElementById(
                "admissionSuccessContinueBtn"
            );


        if (continueBtn) {

            continueBtn.focus();

            continueBtn.addEventListener(
                "click",
                function () {

                    window.location.href =
                        "/admission/patient_admission?tab=list";

                }
            );

        }


        // =================================================
        // CLICK OUTSIDE MODAL
        // =================================================

        modal.addEventListener(
            "click",
            function (event) {

                if (event.target === modal) {

                    window.location.href =
                        "/admission/patient_admission?tab=list";

                }

            }
        );


        // =================================================
        // ESCAPE KEY
        // =================================================

        function handleEscape(event) {

            if (event.key === "Escape") {

                document.removeEventListener(
                    "keydown",
                    handleEscape
                );

                window.location.href =
                    "/admission/patient_admission?tab=list";

            }

        }


        document.addEventListener(
            "keydown",
            handleEscape
        );

    }


    // =====================================================
    // SEARCH PATIENT
    // =====================================================

    async function searchPatient(root) {

        const patientNoInput =
            q(root, "patientNo");

        const searchPatientBtn =
            q(root, "searchPatientBtn");

        const patientIdInput =
            q(root, "patientId");

        const selectedPatientCardWrap =
            q(root, "selectedPatientCardWrap");

        const admissionDetailsCard =
            q(root, "admissionDetailsCard");

        const departmentSelect =
            q(root, "department");


        if (
            !patientNoInput ||
            !searchPatientBtn ||
            !patientIdInput ||
            !selectedPatientCardWrap ||
            !admissionDetailsCard
        ) {

            console.error(
                "ADMIT PATIENT ERROR: Required HTML element not found."
            );

            return;

        }


        const patientNo =
            patientNoInput.value.trim();


        if (!patientNo) {

            alert(
                "Please enter hospital number."
            );

            patientNoInput.focus();

            return;

        }


        searchPatientBtn.disabled = true;

        const originalText =
            searchPatientBtn.textContent;

        searchPatientBtn.textContent =
            "Searching...";


        try {

            console.log(
                "Searching patient:",
                patientNo
            );


            const response = await fetch(

                `/admission/search_patient/${encodeURIComponent(patientNo)}`,

                {
                    method: "GET",

                    headers: {
                        "Accept": "application/json",
                        "X-Requested-With":
                            "XMLHttpRequest"
                    }
                }

            );


            console.log(
                "Search HTTP status:",
                response.status
            );


            const data =
                await response.json();


            console.log(
                "Search response:",
                data
            );


            if (
                !response.ok ||
                !data.success
            ) {

                alert(
                    data.message ||
                    "Patient not found."
                );

                return;

            }


            // =================================================
            // ALREADY ADMITTED
            // =================================================

            if (
                data.patient.already_admitted
            ) {

                alert(

                    "This patient is already admitted.\n\n" +

                    "Admission No: " +
                    data.patient.admission_no

                );

                return;

            }


            const patient =
                data.patient;


            patientIdInput.value =
                patient.id;


            const selectedPatientNo =
                q(root, "selectedPatientNo");

            const selectedPatientName =
                q(root, "selectedPatientName");

            const selectedPatientAge =
                q(root, "selectedPatientAge");

            const selectedPatientGender =
                q(root, "selectedPatientGender");

            const selectedPatientDepartment =
                q(root, "selectedPatientDepartment");

            const selectedPatientDoctor =
                q(root, "selectedPatientDoctor");


            if (selectedPatientNo) {

                selectedPatientNo.textContent =
                    patient.patient_no || "—";

            }


            if (selectedPatientName) {

                selectedPatientName.textContent =
                    patient.full_name || "—";

            }


            if (selectedPatientAge) {

                selectedPatientAge.textContent =
                    patient.age || "—";

            }


            if (selectedPatientGender) {

                selectedPatientGender.textContent =
                    patient.gender || "—";

            }


            if (selectedPatientDepartment) {

                selectedPatientDepartment.textContent =
                    patient.department || "—";

            }


            if (selectedPatientDoctor) {

                selectedPatientDoctor.textContent =
                    patient.doctor || "—";

            }


            selectedPatientCardWrap.style.display =
                "block";


            admissionDetailsCard.style.display =
                "block";


            // =================================================
            // AUTO SELECT DEPARTMENT
            // =================================================

            if (
                patient.department &&
                departmentSelect
            ) {

                const departmentOptions =
                    Array.from(
                        departmentSelect.options
                    );


                const matchingDepartment =
                    departmentOptions.find(
                        option =>
                            option.textContent
                                .trim()
                                .toLowerCase()
                                .includes(
                                    patient.department
                                        .trim()
                                        .toLowerCase()
                                )
                    );


                if (matchingDepartment) {

                    departmentSelect.value =
                        matchingDepartment.value;

                }

            }


            checkAdmissionReady(root);


            admissionDetailsCard.scrollIntoView({

                behavior: "smooth",

                block: "start"

            });


        } catch (error) {

            console.error(
                "SEARCH PATIENT ERROR:",
                error
            );

            alert(
                "Unable to connect to server."
            );

        } finally {

            searchPatientBtn.disabled =
                false;

            searchPatientBtn.textContent =
                originalText;

        }

    }


    // =====================================================
    // LOAD ROOMS
    // =====================================================

    async function loadRooms(
        wardId,
        root
    ) {

        const roomSelect =
            q(root, "room");

        const bedSelect =
            q(root, "bed");


        if (
            !roomSelect ||
            !bedSelect
        ) {
            return;
        }


        roomSelect.innerHTML =
            '<option value="">Loading rooms...</option>';

        roomSelect.disabled =
            true;


        bedSelect.innerHTML =
            '<option value="">Select Room First</option>';

        bedSelect.disabled =
            true;


        checkAdmissionReady(root);


        if (!wardId) {

            roomSelect.innerHTML =
                '<option value="">Select Ward First</option>';

            return;

        }


        try {

            const response =
                await fetch(
                    `/admission/rooms/${wardId}`,
                    {
                        headers: {
                            "Accept":
                                "application/json"
                        }
                    }
                );


            const data =
                await response.json();


            console.log(
                "Rooms response:",
                data
            );


            roomSelect.innerHTML =
                '<option value="" selected disabled>Select Room</option>';


            if (
                data.success &&
                data.rooms &&
                data.rooms.length > 0
            ) {

                data.rooms.forEach(
                    function (room) {

                        const option =
                            document.createElement(
                                "option"
                            );


                        option.value =
                            room.id;


                        option.textContent =
                            `${room.room_name} (${room.room_code})`;


                        roomSelect.appendChild(
                            option
                        );

                    }
                );


                roomSelect.disabled =
                    false;

            } else {

                roomSelect.innerHTML =
                    '<option value="">No rooms available</option>';

            }


        } catch (error) {

            console.error(
                "ROOM LOAD ERROR:",
                error
            );


            roomSelect.innerHTML =
                '<option value="">Unable to load rooms</option>';

        }


        checkAdmissionReady(root);

    }


    // =====================================================
    // LOAD BEDS
    // =====================================================

    async function loadBeds(
        roomId,
        root
    ) {

        const bedSelect =
            q(root, "bed");


        if (!bedSelect) {
            return;
        }


        bedSelect.innerHTML =
            '<option value="">Loading beds...</option>';

        bedSelect.disabled =
            true;


        checkAdmissionReady(root);


        if (!roomId) {

            bedSelect.innerHTML =
                '<option value="">Select Room First</option>';

            return;

        }


        try {

            const response =
                await fetch(
                    `/admission/beds/${roomId}`,
                    {
                        headers: {
                            "Accept":
                                "application/json"
                        }
                    }
                );


            const data =
                await response.json();


            console.log(
                "Beds response:",
                data
            );


            bedSelect.innerHTML =
                '<option value="" selected disabled>Select Available Bed</option>';


            if (
                data.success &&
                data.beds &&
                data.beds.length > 0
            ) {

                data.beds.forEach(
                    function (bed) {

                        const option =
                            document.createElement(
                                "option"
                            );


                        option.value =
                            bed.id;


                        let text =
                            `${bed.bed_name} (${bed.bed_code})`;


                        if (bed.bed_type) {

                            text +=
                                ` - ${bed.bed_type}`;

                        }


                        if (
                            bed.bed_price !== null &&
                            bed.bed_price !== undefined
                        ) {

                            text +=
                                ` - Rs. ${Number(
                                    bed.bed_price
                                ).toFixed(2)}`;

                        }


                        option.textContent =
                            text;


                        bedSelect.appendChild(
                            option
                        );

                    }
                );


                bedSelect.disabled =
                    false;

            } else {

                bedSelect.innerHTML =
                    '<option value="">No available beds</option>';

            }


        } catch (error) {

            console.error(
                "BED LOAD ERROR:",
                error
            );


            bedSelect.innerHTML =
                '<option value="">Unable to load beds</option>';

        }


        checkAdmissionReady(root);

    }


    // =====================================================
    // SUBMIT ADMISSION
    // =====================================================

    async function submitAdmission(
        event,
        root
    ) {

        event.preventDefault();


        const patientIdInput =
            q(root, "patientId");

        const departmentSelect =
            q(root, "department");

        const wardSelect =
            q(root, "ward");

        const roomSelect =
            q(root, "room");

        const bedSelect =
            q(root, "bed");

        const admitPatientBtn =
            q(root, "admitPatientBtn");


        if (
            !admitPatientBtn ||
            admitPatientBtn.disabled
        ) {

            return;

        }


        admitPatientBtn.disabled =
            true;

        admitPatientBtn.textContent =
            "Admitting...";


        const payload = {

            patient_id:
                patientIdInput.value,

            department_id:
                departmentSelect.value,

            ward_id:
                wardSelect.value,

            room_id:
                roomSelect.value,

            bed_id:
                bedSelect.value,

            admission_type:
                q(root, "admissionType")?.value ||
                "IPD",

            reason:
                q(root, "reason")?.value ||
                "",

            remarks:
                q(root, "remarks")?.value.trim() ||
                ""

        };


        console.log(
            "ADMISSION PAYLOAD:",
            payload
        );


        try {

            // =================================================
            // IMPORTANT:
            // Flask route is:
            // /admission/admit
            // =================================================

            const response =
                await fetch(
                    "/admission/admit",
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


            // =================================================
            // SAFELY HANDLE JSON
            // =================================================

            const contentType =
                response.headers.get(
                    "content-type"
                ) || "";


            let data;


            if (
                contentType.includes(
                    "application/json"
                )
            ) {

                data =
                    await response.json();

            } else {

                const text =
                    await response.text();


                console.error(
                    "SERVER RETURNED NON-JSON:",
                    text
                );


                throw new Error(
                    `Server returned ${response.status} instead of JSON.`
                );

            }


            console.log(
                "ADMISSION RESPONSE:",
                data
            );


            if (
                !response.ok ||
                !data.success
            ) {

                throw new Error(
                    data.message ||
                    "Unable to admit patient."
                );

            }


            // =================================================
            // PROFESSIONAL SUCCESS MODAL
            // =================================================

            showAdmissionSuccess(
                data.admission.admission_no
            );


        } catch (error) {

            console.error(
                "ADMISSION ERROR:",
                error
            );


            alert(
                error.message ||
                "Unable to connect to server."
            );


            admitPatientBtn.disabled =
                false;


            admitPatientBtn.textContent =
                "Admit Patient";

        }

    }


    // =====================================================
    // RESET ADMISSION FORM
    // =====================================================

    function resetAdmissionForm(root) {

        const patientIdInput =
            q(root, "patientId");

        const patientNoInput =
            q(root, "patientNo");

        const selectedPatientCardWrap =
            q(root, "selectedPatientCardWrap");

        const admissionDetailsCard =
            q(root, "admissionDetailsCard");

        const departmentSelect =
            q(root, "department");

        const wardSelect =
            q(root, "ward");

        const roomSelect =
            q(root, "room");

        const bedSelect =
            q(root, "bed");

        const admitPatientBtn =
            q(root, "admitPatientBtn");


        if (patientIdInput) {

            patientIdInput.value =
                "";

        }


        if (patientNoInput) {

            patientNoInput.value =
                "";

        }


        if (selectedPatientCardWrap) {

            selectedPatientCardWrap.style.display =
                "none";

        }


        if (admissionDetailsCard) {

            admissionDetailsCard.style.display =
                "none";

        }


        if (departmentSelect) {

            departmentSelect.value =
                "";

        }


        if (wardSelect) {

            wardSelect.value =
                "";

        }


        if (roomSelect) {

            roomSelect.innerHTML =
                '<option value="">Select Ward First</option>';

            roomSelect.disabled =
                true;

        }


        if (bedSelect) {

            bedSelect.innerHTML =
                '<option value="">Select Room First</option>';

            bedSelect.disabled =
                true;

        }


        if (admitPatientBtn) {

            admitPatientBtn.disabled =
                true;

            admitPatientBtn.textContent =
                "Admit Patient";

        }

    }


    // =====================================================
    // DELEGATED CLICK EVENTS
    // =====================================================

    document.addEventListener(
        "click",
        function (event) {

            const searchBtn =
                event.target.closest &&
                event.target.closest(
                    "#searchPatientBtn"
                );


            if (searchBtn) {

                searchPatient(
                    getRoot(searchBtn)
                );

                return;

            }


            const resetBtn =
                event.target.closest &&
                event.target.closest(
                    "#resetAdmissionBtn"
                );


            if (resetBtn) {

                resetAdmissionForm(
                    getRoot(resetBtn)
                );

                return;

            }

        }
    );


    // =====================================================
    // ENTER KEY
    // =====================================================

    document.addEventListener(
        "keydown",
        function (event) {

            if (
                event.target &&
                event.target.id === "patientNo" &&
                event.key === "Enter"
            ) {

                event.preventDefault();

                searchPatient(
                    getRoot(event.target)
                );

            }

        }
    );


    // =====================================================
    // CHANGE EVENTS
    // =====================================================

    document.addEventListener(
        "change",
        function (event) {

            if (
                !event.target ||
                !event.target.id
            ) {

                return;

            }


            const root =
                getRoot(event.target);


            if (
                event.target.id === "ward"
            ) {

                loadRooms(
                    event.target.value,
                    root
                );

                return;

            }


            if (
                event.target.id === "room"
            ) {

                loadBeds(
                    event.target.value,
                    root
                );

                return;

            }


            if (
                event.target.id === "department" ||
                event.target.id === "bed"
            ) {

                checkAdmissionReady(
                    root
                );

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

            if (
                event.target &&
                event.target.id === "admissionForm"
            ) {

                submitAdmission(
                    event,
                    getRoot(event.target)
                );

            }

        }
    );


    console.log(
        "ADMIT PATIENT DELEGATED + SCOPED LISTENERS READY"
    );

})();