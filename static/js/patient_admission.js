document.addEventListener("DOMContentLoaded", function () {

    const patientNoInput = document.getElementById("patientNo");
    const searchPatientBtn = document.getElementById("searchPatientBtn");
    const patientNoAdminInput = document.getElementById("patientNoAdmit");
    const searchPatientBtnAdmit = document.getElementById("searchPatientBtnAdmit");
    const selectedPatientCardWrap = document.getElementById("selectedPatientCardWrap");
    const admissionDetailsCard = document.getElementById("admissionDetailsCard");
    const admitEmptyState = document.getElementById("admitEmptyState");
    const patientIdInput = document.getElementById("patientId");
    const departmentSelect = document.getElementById("department");
    const wardSelect = document.getElementById("ward");
    const roomSelect = document.getElementById("room");
    const bedSelect = document.getElementById("bed");
    const admissionForm = document.getElementById("admissionForm");
    const admitPatientBtn = document.getElementById("admitPatientBtn");

    // =====================================================
    // TABS: PATIENT LIST / ADMIT PATIENT
    // =====================================================

    const admPage = document.getElementById("admPage");
    const navButtons = document.querySelectorAll("[data-nav-tab]");
    const tabPanels = {
        list: document.getElementById("listTab"),
        admit: document.getElementById("admitTab")
    };

    function activateTab(tabName) {

        if (!tabPanels[tabName]) tabName = "list";

        navButtons.forEach(function (btn) {
            btn.classList.toggle("is-active", btn.dataset.navTab === tabName);
        });

        Object.keys(tabPanels).forEach(function (key) {
            tabPanels[key].classList.toggle("is-active", key === tabName);
        });

        const url = new URL(window.location.href);
        url.searchParams.set("tab", tabName);
        window.history.replaceState({}, "", url);
    }

    navButtons.forEach(function (btn) {
        btn.addEventListener("click", function () {
            activateTab(btn.dataset.navTab);
        });
    });

    document.getElementById("goToListBtn").addEventListener("click", function () {
        activateTab("list");
    });

    activateTab(admPage.dataset.initialTab === "admit" ? "admit" : "list");

    // =====================================================
    // SELECT PATIENT FROM LIST
    // =====================================================

    document.querySelectorAll(".adm-admit-btn").forEach(function (button) {
        button.addEventListener("click", function () {
            selectPatient({
                id: this.dataset.patientId,
                patient_no: this.dataset.patientNo,
                full_name: this.dataset.patientName,
                age: this.dataset.patientAge,
                gender: this.dataset.patientGender,
                department: this.dataset.patientDepartment,
                doctor: this.dataset.patientDoctor
            });
            activateTab("admit");
        });
    });

    // =====================================================
    // SEARCH PATIENT (shared by List tab and Admit tab)
    // =====================================================

    async function searchPatient(inputEl, buttonEl) {

        const number = inputEl.value.trim();

        if (!number) {
            alert("Please enter hospital number.");
            return;
        }

        const originalText = buttonEl.textContent;
        buttonEl.disabled = true;
        buttonEl.textContent = "Searching...";

        try {

            const response = await fetch(`/admission/search_patient/${encodeURIComponent(number)}`);
            const data = await response.json();

            if (!data.success) {
                alert(data.message || "Patient not found.");
                return;
            }

            if (data.patient.already_admitted) {
                alert(`This patient is already admitted (Admission No: ${data.patient.admission_no}).`);
                return;
            }

            selectPatient(data.patient);
            activateTab("admit");

        } catch (error) {
            console.error(error);
            alert("Unable to connect to server.");
        } finally {
            buttonEl.disabled = false;
            buttonEl.textContent = originalText;
        }
    }

    searchPatientBtn.addEventListener("click", function () {
        searchPatient(patientNoInput, searchPatientBtn);
    });

    searchPatientBtnAdmit.addEventListener("click", function () {
        searchPatient(patientNoAdminInput, searchPatientBtnAdmit);
    });

    patientNoInput.addEventListener("keydown", function (event) {
        if (event.key === "Enter") searchPatient(patientNoInput, searchPatientBtn);
    });

    patientNoAdminInput.addEventListener("keydown", function (event) {
        if (event.key === "Enter") searchPatient(patientNoAdminInput, searchPatientBtnAdmit);
    });

    // =====================================================
    // SELECT PATIENT
    // =====================================================

    function selectPatient(patient) {

        patientIdInput.value = patient.id;
        patientNoInput.value = patient.patient_no || "";
        patientNoAdminInput.value = patient.patient_no || "";

        document.getElementById("selectedPatientNo").textContent = patient.patient_no || "—";
        document.getElementById("selectedPatientName").textContent = patient.full_name || "—";
        document.getElementById("selectedPatientAge").textContent = patient.age || "—";
        document.getElementById("selectedPatientGender").textContent = patient.gender || "—";
        document.getElementById("selectedPatientDepartment").textContent = patient.department || "—";
        document.getElementById("selectedPatientDoctor").textContent = patient.doctor || "—";

        admitEmptyState.style.display = "none";
        selectedPatientCardWrap.style.display = "block";
        admissionDetailsCard.style.display = "block";

        checkAdmissionReady();
    }

    // =====================================================
    // WARD -> ROOM
    // =====================================================

    wardSelect.addEventListener("change", async function () {

        const wardId = this.value;

        roomSelect.innerHTML = '<option value="">Loading rooms...</option>';
        roomSelect.disabled = true;

        bedSelect.innerHTML = '<option value="">Select Room First</option>';
        bedSelect.disabled = true;
        checkAdmissionReady();

        if (!wardId) {
            roomSelect.innerHTML = '<option value="">Select Ward First</option>';
            return;
        }

        try {

            const response = await fetch(`/admission/rooms/${wardId}`);
            const data = await response.json();

            roomSelect.innerHTML = '<option value="" selected disabled>Select Room</option>';

            if (data.success && data.rooms.length) {
                data.rooms.forEach(function (room) {
                    const option = document.createElement("option");
                    option.value = room.id;
                    option.textContent = `${room.room_name} (${room.room_code})`;
                    roomSelect.appendChild(option);
                });
                roomSelect.disabled = false;
            } else {
                roomSelect.innerHTML = '<option value="">No rooms available</option>';
            }

        } catch (error) {
            console.error(error);
            roomSelect.innerHTML = '<option value="">Unable to load rooms</option>';
        }
    });

    // =====================================================
    // ROOM -> BED
    // =====================================================

    roomSelect.addEventListener("change", async function () {

        const roomId = this.value;

        bedSelect.innerHTML = '<option value="">Loading beds...</option>';
        bedSelect.disabled = true;
        checkAdmissionReady();

        if (!roomId) {
            bedSelect.innerHTML = '<option value="">Select Room First</option>';
            return;
        }

        try {

            const response = await fetch(`/admission/beds/${roomId}`);
            const data = await response.json();

            bedSelect.innerHTML = '<option value="" selected disabled>Select Available Bed</option>';

            if (data.success && data.beds.length) {
                data.beds.forEach(function (bed) {
                    const option = document.createElement("option");
                    option.value = bed.id;
                    let text = `${bed.bed_name} (${bed.bed_code})`;
                    if (bed.bed_type) text += ` - ${bed.bed_type}`;
                    if (bed.bed_price !== null && bed.bed_price !== undefined) {
                        text += ` - Rs. ${Number(bed.bed_price).toFixed(2)}`;
                    }
                    option.textContent = text;
                    bedSelect.appendChild(option);
                });
                bedSelect.disabled = false;
            } else {
                bedSelect.innerHTML = '<option value="">No available beds</option>';
            }

        } catch (error) {
            console.error(error);
            bedSelect.innerHTML = '<option value="">Unable to load beds</option>';
        } finally {
            checkAdmissionReady();
        }
    });

    // =====================================================
    // FORM READINESS
    // =====================================================

    function checkAdmissionReady() {
        admitPatientBtn.disabled =
            !patientIdInput.value ||
            !departmentSelect.value ||
            !wardSelect.value ||
            !roomSelect.value ||
            !bedSelect.value;
    }

    departmentSelect.addEventListener("change", checkAdmissionReady);
    bedSelect.addEventListener("change", checkAdmissionReady);

    // =====================================================
    // SUBMIT ADMISSION
    // =====================================================

    admissionForm.addEventListener("submit", async function (event) {

        event.preventDefault();

        if (admitPatientBtn.disabled) return;

        admitPatientBtn.disabled = true;
        admitPatientBtn.textContent = "Admitting...";

        const payload = {
            patient_id: patientIdInput.value,
            department_id: departmentSelect.value,
            ward_id: wardSelect.value,
            room_id: roomSelect.value,
            bed_id: bedSelect.value,
            admission_type: document.getElementById("admissionType").value,
            remarks: document.getElementById("remarks").value.trim()
        };

        try {

            const response = await fetch("/admission/admit", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            const data = await response.json();

            if (!response.ok || !data.success) {
                throw new Error(data.message || "Unable to admit patient.");
            }

            alert(`Patient admitted successfully. Admission No: ${data.admission.admission_no}`);
            window.location.href = window.location.pathname + "?tab=list";

        } catch (error) {
            console.error(error);
            alert(error.message);
            admitPatientBtn.disabled = false;
            admitPatientBtn.textContent = "Admit Patient";
        }
    });

    // =====================================================
    // RESET
    // =====================================================

    document.getElementById("resetAdmissionBtn").addEventListener("click", function () {

        patientIdInput.value = "";
        patientNoInput.value = "";
        patientNoAdminInput.value = "";

        selectedPatientCardWrap.style.display = "none";
        admissionDetailsCard.style.display = "none";
        admitEmptyState.style.display = "block";

        departmentSelect.value = "";
        wardSelect.value = "";

        roomSelect.innerHTML = '<option value="">Select Ward First</option>';
        roomSelect.disabled = true;

        bedSelect.innerHTML = '<option value="">Select Room First</option>';
        bedSelect.disabled = true;

        admitPatientBtn.disabled = true;
        admitPatientBtn.textContent = "Admit Patient";
    });

});