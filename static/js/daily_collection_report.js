document.addEventListener("DOMContentLoaded", function () {

    const dateInput = document.getElementById("reportDate");
    const loadButton = document.getElementById("loadReportBtn");
    const searchInput = document.getElementById("transactionSearch");
    const table = document.getElementById("transactionTable");


    // ---------------------------------------------------------
    // LOAD REPORT BY DATE
    // ---------------------------------------------------------

    if (loadButton) {

        loadButton.addEventListener("click", function () {

            const selectedDate = dateInput.value;

            if (!selectedDate) {
                alert("Please select a report date.");
                return;
            }

            const currentUrl = new URL(window.location.href);

            currentUrl.searchParams.set(
                "date",
                selectedDate
            );

            window.location.href = currentUrl.toString();

        });

    }


    // ---------------------------------------------------------
    // SEARCH TRANSACTIONS
    // ---------------------------------------------------------

    if (searchInput && table) {

        searchInput.addEventListener("input", function () {

            const searchValue =
                searchInput.value
                    .toLowerCase()
                    .trim();

            const rows =
                table.querySelectorAll("tbody tr");

            rows.forEach(function (row) {

                const rowText =
                    row.textContent.toLowerCase();

                if (rowText.includes(searchValue)) {

                    row.style.display = "";

                } else {

                    row.style.display = "none";

                }

            });

        });

    }

});