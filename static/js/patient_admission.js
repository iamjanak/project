document.addEventListener("DOMContentLoaded", function () {

    const patientNoInput =
        document.getElementById("patientNo");

    const searchPatientBtn =
        document.getElementById("searchPatientBtn");

    const patientInfoCard =
        document.getElementById("patientInfoCard");

    const admissionFormCard =
        document.getElementById("admissionFormCard");

    const admissionForm =
        document.getElementById("admissionForm");

    const patientId =
        document.getElementById("patientId");

    const department =
        document.getElementById("department");

    const ward =
        document.getElementById("ward");

    const room =
        document.getElementById("room");

    const bed =
        document.getElementById("bed");

    const admissionDate =
        document.getElementById("admissionDate");

    const admissionTime =
        document.getElementById("admissionTime");

    const cancelBtn =
        document.getElementById("cancelAdmissionBtn");


    // =====================================================
    // SET CURRENT DATE & TIME
    // =====================================================

    function setCurrentDateTime() {

        const now = new Date();

        const year =
            now.getFullYear();

        const month =
            String(
                now.getMonth() + 1
            ).padStart(2, "0");

        const day =
            String(
                now.getDate()
            ).padStart(2, "0");

        const hours =
            String(
                now.getHours()
            ).padStart(2, "0");

        const minutes =
            String(
                now.getMinutes()
            ).padStart(2, "0");


        admissionDate.value =
            `${year}-${month}-${day}`;

        admissionTime.value =
            `${hours}:${minutes}`;
    }


    setCurrentDateTime();


    // =====================================================
    // POPUP
    // =====================================================

    function showPopup(
        popupId,
        message
    ) {

        const popup =
            document.getElementById(
                popupId
            );

        if (!popup) {
            return;
        }


        const messageElement =
            popup.querySelector(
                "span"
            );


        if (messageElement) {

            messageElement.textContent =
                message;

        }


        popup.classList.add(
            "show"
        );


        setTimeout(
            function () {

                popup.classList.remove(
                    "show"
                );

            },
            4000
        );
    }


    // =====================================================
    // CLOSE POPUPS
    // =====================================================

    document
        .querySelectorAll(
            ".admission-popup-close"
        )
        .forEach(
            function (button) {

                button.addEventListener(
                    "click",
                    function () {

                        const popupId =
                            button.dataset.popup;

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

            }
        );


    // =====================================================
    // SEARCH PATIENT
    // =====================================================

    searchPatientBtn.addEventListener(
        "click",
        async function () {

            const patientNo =
                patientNoInput.value.trim();


            if (!patientNo) {

                showPopup(
                    "admissionErrorPopup",
                    "Please enter the hospital number."
                );

                return;
            }


            searchPatientBtn.disabled =
                true;

            searchPatientBtn.textContent =
                "Searching...";


            try {

                const response =
                    await fetch(
                        `/admission/search_patient/${encodeURIComponent(patientNo)}`
                    );


                const data =
                    await response.json();


                if (!response.ok || !data.success) {

                    throw new Error(
                        data.message ||
                        "Patient not found."
                    );

                }


                const patient =
                    data.patient;


                // -------------------------------------------------
                // DISPLAY PATIENT
                // -------------------------------------------------

                patientId.value =
                    patient.id;


                document.getElementById(
                    "displayPatientNo"
                ).textContent =
                    patient.patient_no || "—";


                document.getElementById(
                    "displayPatientName"
                ).textContent =
                    patient.full_name || "—";


                document.getElementById(
                    "displayPatientAge"
                ).textContent =
                    patient.age !== null &&
                    patient.age !== undefined
                        ? patient.age
                        : "—";


                document.getElementById(
                    "displayPatientGender"
                ).textContent =
                    patient.gender || "—";


                document.getElementById(
                    "displayPatientPhone"
                ).textContent =
                    patient.phone || "—";


                document.getElementById(
                    "displayPatientDepartment"
                ).textContent =
                    patient.department || "—";


                document.getElementById(
                    "displayPatientDoctor"
                ).textContent =
                    patient.doctor || "—";


                patientInfoCard.style.display =
                    "block";


                // -------------------------------------------------
                // ALREADY ADMITTED
                // -------------------------------------------------

                if (patient.already_admitted) {

                    admissionFormCard.style.display =
                        "none";


                    showPopup(
                        "admissionErrorPopup",
                        "This patient is already admitted."
                    );


                    return;
                }


                // -------------------------------------------------
                // SHOW FORM
                // -------------------------------------------------

                admissionFormCard.style.display =
                    "block";


                admissionFormCard.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });

            }


            catch (error) {

                patientInfoCard.style.display =
                    "none";

                admissionFormCard.style.display =
                    "none";


                showPopup(
                    "admissionErrorPopup",
                    error.message
                );

            }


            finally {

                searchPatientBtn.disabled =
                    false;

                searchPatientBtn.textContent =
                    "Search Patient";

            }

        }
    );


    // =====================================================
    // WARD CHANGE
    // =====================================================

    ward.addEventListener(
        "change",
        async function () {

            const wardId =
                ward.value;


            room.innerHTML =
                `
                <option value="">
                    Loading rooms...
                </option>
                `;

            room.disabled =
                true;


            bed.innerHTML =
                `
                <option value="">
                    Select Room First
                </option>
                `;

            bed.disabled =
                true;


            if (!wardId) {

                room.innerHTML =
                    `
                    <option value="">
                        Select Ward First
                    </option>
                    `;

                return;
            }


            try {

                const response =
                    await fetch(
                        `/admission/rooms/${wardId}`
                    );


                const data =
                    await response.json();


                if (
                    !response.ok ||
                    !data.success
                ) {

                    throw new Error(
                        data.message ||
                        "Unable to load rooms."
                    );

                }


                room.innerHTML =
                    `
                    <option value="" disabled selected>
                        Select Room
                    </option>
                    `;


                if (
                    data.rooms.length === 0
                ) {

                    room.innerHTML =
                        `
                        <option value="">
                            No active rooms available
                        </option>
                        `;

                    return;
                }


                data.rooms.forEach(
                    function (item) {

                        const option =
                            document.createElement(
                                "option"
                            );

                        option.value =
                            item.id;

                        option.textContent =
                            `${item.room_name} (${item.room_code})`;

                        room.appendChild(
                            option
                        );

                    }
                );


                room.disabled =
                    false;

            }


            catch (error) {

                room.innerHTML =
                    `
                    <option value="">
                        Unable to load rooms
                    </option>
                    `;


                showPopup(
                    "admissionErrorPopup",
                    error.message
                );

            }

        }
    );


    // =====================================================
    // ROOM CHANGE
    // =====================================================

    room.addEventListener(
        "change",
        async function () {

            const roomId =
                room.value;


            bed.innerHTML =
                `
                <option value="">
                    Loading available beds...
                </option>
                `;

            bed.disabled =
                true;


            if (!roomId) {

                bed.innerHTML =
                    `
                    <option value="">
                        Select Room First
                    </option>
                    `;

                return;
            }


            try {

                const response =
                    await fetch(
                        `/admission/beds/${roomId}`
                    );


                const data =
                    await response.json();


                if (
                    !response.ok ||
                    !data.success
                ) {

                    throw new Error(
                        data.message ||
                        "Unable to load beds."
                    );

                }


                bed.innerHTML =
                    `
                    <option value="" disabled selected>
                        Select Available Bed
                    </option>
                    `;


                if (
                    data.beds.length === 0
                ) {

                    bed.innerHTML =
                        `
                        <option value="">
                            No available beds
                        </option>
                        `;

                    return;
                }


                data.beds.forEach(
                    function (item) {

                        const option =
                            document.createElement(
                                "option"
                            );

                        option.value =
                            item.id;


                        let text =
                            `${item.bed_name} (${item.bed_code})`;


                        if (
                            item.bed_type
                        ) {

                            text +=
                                ` - ${item.bed_type}`;

                        }


                        if (
                            item.bed_price !== null &&
                            item.bed_price !== undefined
                        ) {

                            text +=
                                ` - Rs. ${Number(
                                    item.bed_price
                                ).toFixed(2)}`;

                        }


                        option.textContent =
                            text;


                        bed.appendChild(
                            option
                        );

                    }
                );


                bed.disabled =
                    false;

            }


            catch (error) {

                bed.innerHTML =
                    `
                    <option value="">
                        Unable to load beds
                    </option>
                    `;


                showPopup(
                    "admissionErrorPopup",
                    error.message
                );

            }

        }
    );


    // =====================================================
    // SUBMIT ADMISSION
    // =====================================================

    admissionForm.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();


            if (!patientId.value) {

                showPopup(
                    "admissionErrorPopup",
                    "Please search and select a patient."
                );

                return;
            }


            if (!department.value) {

                showPopup(
                    "admissionErrorPopup",
                    "Please select a department."
                );

                return;
            }


            if (!ward.value) {

                showPopup(
                    "admissionErrorPopup",
                    "Please select a ward."
                );

                return;
            }


            if (!room.value) {

                showPopup(
                    "admissionErrorPopup",
                    "Please select a room."
                );

                return;
            }


            if (!bed.value) {

                showPopup(
                    "admissionErrorPopup",
                    "Please select an available bed."
                );

                return;
            }


            const admitButton =
                document.getElementById(
                    "admitPatientBtn"
                );


            admitButton.disabled =
                true;

            admitButton.textContent =
                "Admitting...";


            const payload = {

                patient_id:
                    patientId.value,

                department_id:
                    department.value,

                ward_id:
                    ward.value,

                room_id:
                    room.value,

                bed_id:
                    bed.value,

                admission_type:
                    document.getElementById(
                        "admissionType"
                    ).value,

                admission_date:
                    admissionDate.value,

                admission_time:
                    admissionTime.value,

                admission_reason:
                    document.getElementById(
                        "admissionReason"
                    ).value.trim(),

                remarks:
                    document.getElementById(
                        "remarks"
                    ).value.trim()

            };


            try {

                const response =
                    await fetch(
                        "/admission/admit",
                        {

                            method:
                                "POST",

                            headers: {
                                "Content-Type":
                                    "application/json"
                            },

                            body:
                                JSON.stringify(
                                    payload
                                )

                        }
                    );


                const data =
                    await response.json();


                if (
                    !response.ok ||
                    !data.success
                ) {

                    throw new Error(
                        data.message ||
                        "Unable to admit patient."
                    );

                }


                showPopup(
                    "admissionSuccessPopup",
                    data.message
                );


                // -------------------------------------------------
                // RESET FORM
                // -------------------------------------------------

                admissionForm.reset();

                patientId.value =
                    "";

                patientInfoCard.style.display =
                    "none";

                admissionFormCard.style.display =
                    "none";

                room.innerHTML =
                    `
                    <option value="">
                        Select Ward First
                    </option>
                    `;

                room.disabled =
                    true;

                bed.innerHTML =
                    `
                    <option value="">
                        Select Room First
                    </option>
                    `;

                bed.disabled =
                    true;

                setCurrentDateTime();


                window.scrollTo({
                    top: 0,
                    behavior: "smooth"
                });

            }


            catch (error) {

                showPopup(
                    "admissionErrorPopup",
                    error.message
                );

            }


            finally {

                admitButton.disabled =
                    false;

                admitButton.textContent =
                    "Admit Patient";

            }

        }
    );


    // =====================================================
    // CANCEL
    // =====================================================

    cancelBtn.addEventListener(
        "click",
        function () {

            admissionForm.reset();

            patientId.value =
                "";

            patientInfoCard.style.display =
                "none";

            admissionFormCard.style.display =
                "none";


            room.innerHTML =
                `
                <option value="">
                    Select Ward First
                </option>
                `;

            room.disabled =
                true;


            bed.innerHTML =
                `
                <option value="">
                    Select Room First
                </option>
                `;

            bed.disabled =
                true;


            setCurrentDateTime();

        }
    );

});