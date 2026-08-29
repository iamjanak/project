// ==========================================
// REGISTRATION JAVASCRIPT
// ==========================================

(function () {

    // ==========================================
    // INITIALIZE REGISTRATION PAGE
    // ==========================================

    function initRegistrationPage() {

        const dobInput =
            document.getElementById("dob");

        const ageInput =
            document.getElementById("age");

        const departmentSelect =
            document.getElementById("department");

        const doctorSelect =
            document.getElementById("doctor");


        // ==========================================
        // MAKE SURE REGISTRATION PAGE EXISTS
        // ==========================================

        if (!dobInput || !ageInput) {
            return;
        }


        // ==========================================
        // PREVENT DUPLICATE EVENT LISTENERS
        // ==========================================

        if (dobInput.dataset.registrationInitialized === "true") {
            return;
        }

        dobInput.dataset.registrationInitialized = "true";


        // ==========================================
        // CALCULATE AGE
        // ==========================================

        function calculateAge() {

            const dob =
                dobInput.value.trim();


            // Empty DOB
            if (!dob) {

                ageInput.value = "";

                return;
            }


            // ==========================================
            // CHECK DD/MM/YYYY FORMAT
            // ==========================================

            if (
                !/^\d{2}\/\d{2}\/\d{4}$/.test(dob)
            ) {

                ageInput.value = "";

                return;
            }


            // ==========================================
            // SPLIT DOB
            // ==========================================

            const parts =
                dob.split("/");


            const day =
                parseInt(parts[0], 10);

            const month =
                parseInt(parts[1], 10);

            const year =
                parseInt(parts[2], 10);


            // ==========================================
            // CHECK BASIC DATE VALUES
            // ==========================================

            if (
                day < 1 ||
                day > 31 ||
                month < 1 ||
                month > 12
            ) {

                ageInput.value = "";

                return;
            }


            // ==========================================
            // CHECK YEAR
            // ==========================================

            const currentYear =
                new Date().getFullYear();


            if (
                year < 1900 ||
                year > currentYear
            ) {

                ageInput.value = "";

                return;
            }


            // ==========================================
            // CREATE BIRTH DATE
            // ==========================================

            const birthDate =
                new Date(
                    year,
                    month - 1,
                    day
                );


            // ==========================================
            // INVALID DATE CHECK
            // ==========================================

            if (
                birthDate.getFullYear() !== year ||
                birthDate.getMonth() !== month - 1 ||
                birthDate.getDate() !== day
            ) {

                ageInput.value = "";

                return;
            }


            // ==========================================
            // TODAY
            // ==========================================

            const today =
                new Date();


            // Remove time
            today.setHours(0, 0, 0, 0);


            // ==========================================
            // FUTURE DATE CHECK
            // ==========================================

            if (birthDate > today) {

                ageInput.value = "";

                return;
            }


            // ==========================================
            // AGE CALCULATION
            // ==========================================

            let age =
                today.getFullYear() -
                birthDate.getFullYear();


            // Birthday has not happened yet
            // this year

            if (
                today.getMonth() <
                birthDate.getMonth()
                ||
                (
                    today.getMonth() ===
                    birthDate.getMonth()
                    &&
                    today.getDate() <
                    birthDate.getDate()
                )
            ) {

                age--;
            }


            // ==========================================
            // SHOW AGE
            // ==========================================

            ageInput.value = age;
        }


        // ==========================================
        // DOB INPUT
        // ==========================================

        dobInput.addEventListener(
            "input",
            function () {

                // Keep numbers only

                let value =
                    this.value.replace(/\D/g, "");


                // Maximum 8 digits

                value =
                    value.substring(0, 8);


                // ==========================================
                // FORMAT DD
                // ==========================================

                if (value.length <= 2) {

                    this.value = value;
                }


                // ==========================================
                // FORMAT DD/MM
                // ==========================================

                else if (value.length <= 4) {

                    this.value =
                        value.substring(0, 2) +
                        "/" +
                        value.substring(2, 4);
                }


                // ==========================================
                // FORMAT DD/MM/YYYY
                // ==========================================

                else {

                    this.value =
                        value.substring(0, 2) +
                        "/" +
                        value.substring(2, 4) +
                        "/" +
                        value.substring(4, 8);
                }


                // ==========================================
                // CALCULATE AGE
                // ==========================================

                if (this.value.length === 10) {

                    calculateAge();

                } else {

                    ageInput.value = "";
                }

            }
        );


        // ==========================================
        // CALCULATE AGE IF DOB ALREADY EXISTS
        // ==========================================

        if (
            dobInput.value.trim() !== ""
        ) {

            calculateAge();
        }


        // ==========================================
        // DEPARTMENT → DOCTOR FILTER
        // ==========================================

        if (
            departmentSelect &&
            doctorSelect
        ) {

            // Store original doctor options

            const doctorOptions =
                Array.from(
                    doctorSelect.querySelectorAll(
                        "option[data-department]"
                    )
                );


            // Prevent duplicate listener

            if (
                departmentSelect.dataset.doctorFilterInitialized !==
                "true"
            ) {

                departmentSelect.dataset.doctorFilterInitialized =
                    "true";


                departmentSelect.addEventListener(
                    "change",
                    function () {

                        const selectedDepartment =
                            this.value;


                        // Clear doctor dropdown

                        doctorSelect.innerHTML = "";


                        // Default option

                        const defaultOption =
                            document.createElement("option");


                        defaultOption.value = "";

                        defaultOption.textContent =
                            "Select doctor";

                        defaultOption.disabled = true;

                        defaultOption.selected = true;


                        doctorSelect.appendChild(
                            defaultOption
                        );


                        // Add matching doctors

                        doctorOptions.forEach(
                            function (option) {

                                if (
                                    option.dataset.department ===
                                    selectedDepartment
                                ) {

                                    doctorSelect.appendChild(
                                        option.cloneNode(true)
                                    );

                                }

                            }
                        );

                    }
                );
            }
        }

    }


    // ==========================================
    // NORMAL PAGE LOAD
    // ==========================================

    if (
        document.readyState === "loading"
    ) {

        document.addEventListener(
            "DOMContentLoaded",
            initRegistrationPage
        );

    } else {

        // Important for AJAX navigation

        initRegistrationPage();
    }


    // ==========================================
    // AJAX NAVIGATION SUPPORT
    // ==========================================
    //
    // Your base.html replaces #page-content.
    // The registration script can therefore be
    // loaded after DOMContentLoaded.
    //
    // initRegistrationPage() is also safe to
    // call multiple times because duplicate
    // listeners are prevented above.
    // ==========================================

    window.initRegistrationPage =
        initRegistrationPage;

})();