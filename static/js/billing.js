// =====================================================
// LAB BILLING MODULE
//
// FIX: The original code only ran inside
// document.addEventListener('DOMContentLoaded', ...),
// which fires ONCE per full page load. If your app swaps
// module content in/out without a full page reload
// (e.g. clicking between sidebar tabs), the billing
// table's HTML gets replaced with fresh elements, but
// this script never re-runs -> no listeners, no test
// catalog loaded, no first row created.
//
// FIX APPLIED: We use a MutationObserver to watch the
// page. Whenever a NEW #testTableBody element shows up
// (i.e. this module's HTML was (re)inserted), we
// automatically re-run setup on it. This works regardless
// of how your navigation/module-switching is implemented.
// =====================================================

(function () {

    // Track which tableBody element we last initialized,
    // so we don't re-init the same one twice.
    let lastInitializedTableBody = null;


    // =====================================================
    // ENTRY POINT: tries to (re)initialize the billing page
    // if a fresh #testTableBody is present.
    // =====================================================

    function trySetupBillingPage() {

        const tableBody = document.getElementById('testTableBody');

        if (!tableBody) {
            return; // Billing module not currently on screen.
        }

        if (tableBody === lastInitializedTableBody) {
            return; // Already initialized this exact element.
        }

        lastInitializedTableBody = tableBody;

        setupBillingPage(tableBody);
    }


    // =====================================================
    // FULL SETUP (equivalent to the old DOMContentLoaded body)
    // Runs fresh every time the billing module's HTML appears.
    // =====================================================

    function setupBillingPage(tableBody) {

        console.log("=================================");
        console.log("BILLING MODULE INITIALIZED");
        console.log("=================================");

        let TEST_CATALOG = {};
        const NAME_TO_TEST = {};

        const nameOptionsList = document.getElementById('testNameOptions');
        const emptyState = document.getElementById('emptyState');

        let rowCounter = 0;


        // -------------------------------------------------
        // LOAD TESTS FROM DATABASE
        // -------------------------------------------------

        async function loadTests() {

            try {

                const response = await fetch('/api/tests');

                if (!response.ok) {
                    throw new Error('Failed to load tests');
                }

                const tests = await response.json();

                TEST_CATALOG = {};

                if (nameOptionsList) {
                    nameOptionsList.innerHTML = '';
                }

                tests.forEach((test) => {

                    TEST_CATALOG[test.test_code] = {
                        id: test.id,
                        name: test.test_name,
                        price: parseFloat(test.price) || 0
                    };

                    NAME_TO_TEST[test.test_name] = {
                        code: test.test_code,
                        price: parseFloat(test.price) || 0,
                        id: test.id
                    };

                    if (nameOptionsList) {
                        const opt = document.createElement('option');
                        opt.value = test.test_name;
                        nameOptionsList.appendChild(opt);
                    }
                });

                console.log('Tests loaded from database:', tests);

            } catch (error) {

                console.error('Error loading tests:', error);
                alert('Unable to load laboratory tests.');
            }
        }


        // -------------------------------------------------
        // CREATE ENTRY ROW
        // -------------------------------------------------

        function createEntryRow() {

            rowCounter += 1;

            const tr = document.createElement('tr');

            tr.dataset.rowId = rowCounter;
            tr.dataset.state = 'entry';

            tr.innerHTML = `
              <td class="row-index">${rowCounter}</td>

              <td>
                <input
                  type="text"
                  class="cell-input cell-input--code"
                  placeholder="Code"
                  data-field="code"
                >
              </td>

              <td>

                <input
                  type="text"
                  class="cell-input cell-input--name"
                  placeholder="Search test name..."
                  list="testNameOptions"
                  data-field="name"
                >

              </td>

              <td class="col-num">

                <input
                  type="number"
                  class="cell-input"
                  value="0.00"
                  step="0.01"
                  min="0"
                  data-field="price"
                  readonly
                >

              </td>

              <td class="col-num">

                <input
                  type="number"
                  class="cell-input"
                  value="1"
                  min="1"
                  data-field="qty"
                >

              </td>

              <td
                class="col-num cell-right"
                data-field="total"
              >
                0.00
              </td>

              <td class="col-num">

                <input
                  type="number"
                  class="cell-input"
                  value="0"
                  min="0"
                  max="100"
                  data-field="discPct"
                >

              </td>

              <td
                class="col-num cell-right"
                data-field="disc"
              >
                0.00
              </td>

              <td
                class="col-num cell-right"
                data-field="netTotal"
              >
                0.00
              </td>

              <td class="col-action">

                <button
                  type="button"
                  class="btn-add-row"
                  title="Add this test"
                >
                  +
                </button>

              </td>
            `;

            tableBody.appendChild(tr);

            bindEntryRowEvents(tr);

            return tr;
        }


        // -------------------------------------------------
        // ENTRY ROW EVENTS
        // -------------------------------------------------

        function bindEntryRowEvents(tr) {

            const codeInput = tr.querySelector('[data-field="code"]');
            const nameInput = tr.querySelector('[data-field="name"]');
            const priceInput = tr.querySelector('[data-field="price"]');
            const qtyInput = tr.querySelector('[data-field="qty"]');
            const discInput = tr.querySelector('[data-field="discPct"]');
            const addBtn = tr.querySelector('.btn-add-row');

            codeInput.addEventListener('change', function () {

                const code = codeInput.value.trim().toUpperCase();
                const test = TEST_CATALOG[code];

                if (test) {
                    nameInput.value = test.name;
                    priceInput.value = test.price.toFixed(2);
                } else {
                    nameInput.value = '';
                    priceInput.value = '0.00';
                }

                recalcRow(tr);
            });

            nameInput.addEventListener('change', function () {

                const name = nameInput.value.trim();
                const match = NAME_TO_TEST[name];

                if (match) {
                    codeInput.value = match.code;
                    priceInput.value = Number(match.price).toFixed(2);
                    tr.dataset.testId = match.id;
                } else {
                    codeInput.value = '';
                    priceInput.value = '0.00';
                    delete tr.dataset.testId;
                }

                recalcRow(tr);
            });

            qtyInput.addEventListener('input', () => recalcRow(tr));
            discInput.addEventListener('input', () => recalcRow(tr));

            addBtn.addEventListener('click', function () {

                if (!codeInput.value.trim() || !nameInput.value.trim()) {
                    alert('Search and select a test before adding.');
                    return;
                }

                const selectedTestId = tr.dataset.testId;

                if (!selectedTestId) {
                    alert('Please select a valid laboratory test.');
                    return;
                }

                confirmRow(tr);
                createEntryRow();
                updateEmptyState();
                recalcFooter();
            });
        }


        // -------------------------------------------------
        // CONFIRM ROW
        // -------------------------------------------------

        function confirmRow(tr) {

            tr.dataset.state = 'confirmed';

            tr.querySelectorAll('input').forEach((input) => {

                if (input.dataset.field === 'qty' || input.dataset.field === 'discPct') {
                    input.addEventListener('input', () => recalcRow(tr));
                } else {
                    input.readOnly = true;
                    input.tabIndex = -1;
                }
            });

            const actionCell = tr.querySelector('.col-action');

            actionCell.innerHTML = `
              <button
                type="button"
                class="btn-remove-row"
                title="Remove test"
              >
                &times;
              </button>
            `;

            actionCell
                .querySelector('.btn-remove-row')
                .addEventListener('click', function () {

                    tr.remove();
                    recalcFooter();
                    updateEmptyState();
                });
        }


        // -------------------------------------------------
        // CALCULATE ROW
        // -------------------------------------------------

        function recalcRow(tr) {

            const price = parseFloat(tr.querySelector('[data-field="price"]').value) || 0;
            const qty = parseFloat(tr.querySelector('[data-field="qty"]').value) || 0;
            const discPct = parseFloat(tr.querySelector('[data-field="discPct"]').value) || 0;

            const total = price * qty;
            const disc = total * (discPct / 100);
            const netTotal = total - disc;

            tr.querySelector('[data-field="total"]').textContent = total.toFixed(2);
            tr.querySelector('[data-field="disc"]').textContent = disc.toFixed(2);
            tr.querySelector('[data-field="netTotal"]').textContent = netTotal.toFixed(2);

            recalcFooter();
        }


        // -------------------------------------------------
        // FOOTER CALCULATION
        // -------------------------------------------------

        function recalcFooter() {

            let sumQty = 0;
            let sumTotal = 0;
            let sumDisc = 0;
            let sumNet = 0;

            tableBody.querySelectorAll('tr[data-state="confirmed"]').forEach((tr) => {

                sumQty += parseFloat(tr.querySelector('[data-field="qty"]').value) || 0;
                sumTotal += parseFloat(tr.querySelector('[data-field="total"]').textContent) || 0;
                sumDisc += parseFloat(tr.querySelector('[data-field="disc"]').textContent) || 0;
                sumNet += parseFloat(tr.querySelector('[data-field="netTotal"]').textContent) || 0;
            });

            document.getElementById('footerQty').textContent = sumQty;
            document.getElementById('footerTotal').textContent = sumTotal.toFixed(2);
            document.getElementById('footerDisc').textContent = sumDisc.toFixed(2);
            document.getElementById('footerNetTotal').textContent = sumNet.toFixed(2);
            document.getElementById('grandTotal').textContent = sumNet.toFixed(2);

            recalcReturnAmount();
        }


        // -------------------------------------------------
        // RETURN AMOUNT
        // -------------------------------------------------

        function recalcReturnAmount() {

            const grandTotal = parseFloat(document.getElementById('grandTotal').textContent) || 0;
            const tenderInput = document.getElementById('tender_amt');
            const tender = parseFloat(tenderInput ? tenderInput.value : 0) || 0;

            const returnAmt = Math.max(tender - grandTotal, 0);

            document.getElementById('returnAmt').textContent = returnAmt.toFixed(2);
        }


        // -------------------------------------------------
        // EMPTY STATE
        // -------------------------------------------------

        function updateEmptyState() {

            const hasConfirmedRow = tableBody.querySelector('tr[data-state="confirmed"]') !== null;

            if (emptyState) {
                emptyState.classList.toggle('hidden', hasConfirmedRow);
            }
        }


        // -------------------------------------------------
        // TENDER AMOUNT
        // -------------------------------------------------

        const tenderAmtInput = document.getElementById('tender_amt');

        if (tenderAmtInput) {
            tenderAmtInput.addEventListener('input', recalcReturnAmount);
        }


        // -------------------------------------------------
        // PATIENT FETCH
        // -------------------------------------------------

        function fetchPatientData() {

            const patientIdField = document.getElementById('patient_id');
            const patientNo = patientIdField ? patientIdField.value.trim() : '';

            if (!patientNo) {
                return;
            }

            fetch(`/fetch_patient/${encodeURIComponent(patientNo)}`)

                .then(response => {

                    if (!response.ok) {
                        throw new Error("Patient not found");
                    }

                    return response.json();
                })

                .then(patient => {

                    document.getElementById('patient_name').value = patient.name || "";

                    document.getElementById('patient_age_sex').value =
                        `${patient.age || "-"} / ${patient.gender || "-"}`;

                    document.getElementById('department').value = patient.department || "";
                    document.getElementById('referring_doctor').value = patient.doctor || "";
                    document.getElementById('credit_due').textContent = "0.00";
                })

                .catch(error => {

                    alert("Patient not found");
                    console.log(error);
                });
        }


        // -------------------------------------------------
        // FETCH BUTTON
        // -------------------------------------------------

        const fetchBtn = document.getElementById('fetchBtn');

        if (fetchBtn) {
            fetchBtn.addEventListener('click', fetchPatientData);
        }


        // -------------------------------------------------
        // ENTER KEY - PATIENT ID
        // -------------------------------------------------

        const patientIdField = document.getElementById('patient_id');

        if (patientIdField) {

            patientIdField.addEventListener('keypress', function (event) {

                if (event.key === "Enter") {
                    event.preventDefault();
                    fetchPatientData();
                }
            });
        }


        // -------------------------------------------------
        // SAVE BILL
        // -------------------------------------------------

        const saveBillBtn = document.getElementById('saveBillBtn');

        if (saveBillBtn) {

            saveBillBtn.addEventListener('click', function () {

                const items = [];

                tableBody.querySelectorAll('tr[data-state="confirmed"]').forEach((tr) => {

                    items.push({
                        code: tr.querySelector('[data-field="code"]').value.trim(),
                        name: tr.querySelector('[data-field="name"]').value.trim(),
                        price: parseFloat(tr.querySelector('[data-field="price"]').value) || 0,
                        qty: parseFloat(tr.querySelector('[data-field="qty"]').value) || 0,
                        discPct: parseFloat(tr.querySelector('[data-field="discPct"]').value) || 0,
                        netTotal: parseFloat(tr.querySelector('[data-field="netTotal"]').textContent) || 0
                    });
                });

                if (items.length === 0) {
                    alert('Add at least one test before saving.');
                    return;
                }

                const payload = {
                    patient_id: document.getElementById('patient_id').value.trim(),
                    patient_name: document.getElementById('patient_name').value.trim(),
                    age_sex: document.getElementById('patient_age_sex').value.trim(),
                    department: document.getElementById('department').value.trim(),
                    rate_type: document.getElementById('rate_type').value,
                    referring_doctor: document.getElementById('referring_doctor').value.trim(),
                    remarks: document.getElementById('remarks').value.trim(),
                    items,
                    grand_total: parseFloat(document.getElementById('grandTotal').textContent) || 0,
                    pay_type: document.getElementById('pay_type').value,
                    tender_amt: parseFloat(document.getElementById('tender_amt').value) || 0,
                    return_amt: parseFloat(document.getElementById('returnAmt').textContent) || 0
                };

                saveBillBtn.disabled = true;
                saveBillBtn.textContent = 'Saving...';

                fetch('/patient/billing/save', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                })

                    .then((res) => {

                        if (!res.ok) {
                            throw new Error('Save failed');
                        }

                        return res.json();
                    })

                    .then((data) => {
                        window.location.href = `/generate_bill/${data.bill_id}`;
                    })

                    .catch(() => {

                        alert('Failed to save the bill. Please try again.');
                        saveBillBtn.disabled = false;
                        saveBillBtn.textContent = 'Save (F12)';
                    });
            });
        }


        // -------------------------------------------------
        // INITIALIZE THIS INSTANCE
        // -------------------------------------------------

        (async function initializeBilling() {

            await loadTests();
            createEntryRow();
            updateEmptyState();
        })();
    }


    // =====================================================
    // GLOBAL, PAGE-INDEPENDENT LISTENERS (attached ONCE)
    // These live on `document`, which never gets destroyed,
    // so they're safe to attach a single time.
    // =====================================================

    if (!window.__billingGlobalListenersAttached) {

        window.__billingGlobalListenersAttached = true;

        document.addEventListener('keydown', function (e) {

            if (e.key === 'F12') {

                e.preventDefault();

                const saveBtn = document.getElementById('saveBillBtn');

                if (saveBtn) {
                    saveBtn.click();
                }
            }
        });
    }


    // =====================================================
    // WATCH FOR THE BILLING MODULE APPEARING / REAPPEARING
    // =====================================================

    const observer = new MutationObserver(function () {
        trySetupBillingPage();
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true
    });


    // Run once immediately in case the billing table is
    // already on the page when this script executes
    // (normal first page load).

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', trySetupBillingPage);
    } else {
        trySetupBillingPage();
    }

})();