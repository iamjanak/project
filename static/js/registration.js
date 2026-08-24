// ==========================================
// REGISTRATION JAVASCRIPT
// ==========================================

document.addEventListener(
    "DOMContentLoaded",
    function () {


        // ==========================================
        // GET DOB AND AGE ELEMENTS
        // ==========================================

        const dobInput =
            document.getElementById("dob");

        const ageInput =
            document.getElementById("age");


        if (!dobInput || !ageInput) {
            return;
        }



        // ==========================================
        // DATE OF BIRTH INPUT
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

                if (
                    this.value.length === 10
                ) {

                    calculateAge();

                }

                else {

                    ageInput.value = "";

                }

            }
        );



        // ==========================================
        // CALCULATE AGE
        // ==========================================

        function calculateAge() {

            const dob =
                dobInput.value.trim();


            // Make sure DOB is DD/MM/YYYY
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
            // CHECK YEAR
            // ==========================================

            if (
                year < 1900 ||
                year > new Date().getFullYear()
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



            // ==========================================
            // FUTURE DATE CHECK
            // ==========================================

            if (
                birthDate > today
            ) {

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
        // CALCULATE AGE IF DOB ALREADY EXISTS
        // ==========================================

        if (
            dobInput.value.trim() !== ""
        ) {

            calculateAge();

        }

    }
);