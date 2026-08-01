document.addEventListener('DOMContentLoaded', function () {

  // ---------- Sample test catalog (replace with a real API call) ----------
  // In production, look this up via fetch(`/api/tests?q=...`) instead.
  const TEST_CATALOG = {
    'CBC001': { name: 'Complete Blood Count', price: 450 },
    'LFT002': { name: 'Liver Function Test', price: 800 },
    'RFT003': { name: 'Renal Function Test', price: 750 },
    'XRAY01': { name: 'Chest X-Ray', price: 600 },
    'USG001': { name: 'Abdominal Ultrasound', price: 1200 },
  };

  // Reverse lookup: test name -> { code, price }
  const NAME_TO_TEST = {};
  Object.entries(TEST_CATALOG).forEach(([code, test]) => {
    NAME_TO_TEST[test.name] = { code, price: test.price };
  });

  // Populate the <datalist> so typing in Test Name filters/searches live
  const nameOptionsList = document.getElementById('testNameOptions');
  Object.values(TEST_CATALOG).forEach((test) => {
    const opt = document.createElement('option');
    opt.value = test.name;
    nameOptionsList.appendChild(opt);
  });

  const tableBody = document.getElementById('testTableBody');
  const emptyState = document.getElementById('emptyState');
  let rowCounter = 0;

  // ---------- Row creation (always creates an editable "entry" row) ----------
  function createEntryRow() {
    rowCounter += 1;
    const tr = document.createElement('tr');
    tr.dataset.rowId = rowCounter;
    tr.dataset.state = 'entry';

    tr.innerHTML = `
      <td class="row-index">${rowCounter}</td>
      <td><input type="text" class="cell-input cell-input--code" placeholder="Code" data-field="code"></td>
      <td>
        <input type="text" class="cell-input cell-input--name" placeholder="Search test name..."
               list="testNameOptions" data-field="name">
      </td>
      <td class="col-num"><input type="number" class="cell-input" value="0.00" step="0.01" min="0" data-field="price" readonly></td>
      <td class="col-num"><input type="number" class="cell-input" value="1" min="1" data-field="qty"></td>
      <td class="col-num cell-right" data-field="total">0.00</td>
      <td class="col-num"><input type="number" class="cell-input" value="0" min="0" max="100" data-field="discPct"></td>
      <td class="col-num cell-right" data-field="disc">0.00</td>
      <td class="col-num cell-right" data-field="netTotal">0.00</td>
      <td class="col-action"><button type="button" class="btn-add-row" title="Add this test">+</button></td>
    `;

    tableBody.appendChild(tr);
    bindEntryRowEvents(tr);
    return tr;
  }

  // ---------- Entry row behavior ----------
  function bindEntryRowEvents(tr) {
    const codeInput = tr.querySelector('[data-field="code"]');
    const nameInput = tr.querySelector('[data-field="name"]');
    const priceInput = tr.querySelector('[data-field="price"]');
    const qtyInput = tr.querySelector('[data-field="qty"]');
    const discInput = tr.querySelector('[data-field="discPct"]');
    const addBtn = tr.querySelector('.btn-add-row');

    // Lookup by code
    codeInput.addEventListener('change', function () {
      const code = codeInput.value.trim().toUpperCase();
      const test = TEST_CATALOG[code];
      if (test) {
        nameInput.value = test.name;
        priceInput.value = test.price.toFixed(2);
      } else {
        priceInput.value = '0.00';
      }
      recalcRow(tr);
    });

    // Lookup by name (search box, via datalist suggestions)
    nameInput.addEventListener('change', function () {
      const match = NAME_TO_TEST[nameInput.value.trim()];
      if (match) {
        codeInput.value = match.code;
        priceInput.value = match.price.toFixed(2);
      } else {
        priceInput.value = '0.00';
      }
      recalcRow(tr);
    });

    [qtyInput, discInput].forEach((el) => el.addEventListener('input', () => recalcRow(tr)));

    addBtn.addEventListener('click', function () {
      if (!codeInput.value.trim() || !nameInput.value.trim()) {
        alert('Search and select a test before adding.');
        return;
      }
      confirmRow(tr);
      createEntryRow(); // fresh empty entry row for the next test
      updateEmptyState();
      recalcFooter();
    });
  }

  // ---------- Convert an entry row into a locked, confirmed row ----------
  function confirmRow(tr) {
    tr.dataset.state = 'confirmed';

    tr.querySelectorAll('input').forEach((input) => {
      if (input.dataset.field === 'qty' || input.dataset.field === 'discPct') {
        // keep qty/discount editable even after confirming, so totals can still be adjusted
        input.addEventListener('input', () => recalcRow(tr));
      } else {
        input.readOnly = true;
        input.tabIndex = -1;
      }
    });

    // Swap the "+" button for a remove "×" button
    const actionCell = tr.querySelector('.col-action');
    actionCell.innerHTML = `<button type="button" class="btn-remove-row" title="Remove test">&times;</button>`;
    actionCell.querySelector('.btn-remove-row').addEventListener('click', function () {
      tr.remove();
      recalcFooter();
      updateEmptyState();
    });
  }

  // ---------- Calculations ----------
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

  function recalcFooter() {
    let sumQty = 0, sumTotal = 0, sumDisc = 0, sumNet = 0;

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

  function recalcReturnAmount() {
    const grandTotal = parseFloat(document.getElementById('grandTotal').textContent) || 0;
    const tender = parseFloat(document.getElementById('tender_amt').value) || 0;
    const returnAmt = Math.max(tender - grandTotal, 0);
    document.getElementById('returnAmt').textContent = returnAmt.toFixed(2);
  }

  function updateEmptyState() {
    const hasConfirmedRow = tableBody.querySelector('tr[data-state="confirmed"]') !== null;
    emptyState.classList.toggle('hidden', hasConfirmedRow);
  }

  document.getElementById('tender_amt').addEventListener('input', recalcReturnAmount);

  // ---------- Patient fetch ----------
  document.getElementById('fetchBtn').addEventListener('click', function () {
    const patientId = document.getElementById('patient_id').value.trim();
    if (!patientId) return;

    fetch(`/api/patient/${encodeURIComponent(patientId)}`)
      .then((res) => {
        if (!res.ok) throw new Error('Patient not found');
        return res.json();
      })
      .then(populatePatient)
      .catch(() => {
        alert('Patient not found for ID: ' + patientId);
      });
  });

  function populatePatient(data) {
    document.getElementById('patient_name').value = data.name || '';
    document.getElementById('patient_age_sex').value = `${data.age || '-'} / ${data.sex || '-'}`;
    document.getElementById('department').value = data.department || '';
    document.getElementById('credit_due').textContent = (data.credit_due || 0).toFixed(2);
  }

  // ---------- Save ----------
  document.getElementById('saveBillBtn').addEventListener('click', function () {
    const items = [];

    tableBody.querySelectorAll('tr[data-state="confirmed"]').forEach((tr) => {
      items.push({
        code: tr.querySelector('[data-field="code"]').value.trim(),
        name: tr.querySelector('[data-field="name"]').value.trim(),
        price: parseFloat(tr.querySelector('[data-field="price"]').value) || 0,
        qty: parseFloat(tr.querySelector('[data-field="qty"]').value) || 0,
        discPct: parseFloat(tr.querySelector('[data-field="discPct"]').value) || 0,
        netTotal: parseFloat(tr.querySelector('[data-field="netTotal"]').textContent) || 0,
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
      return_amt: parseFloat(document.getElementById('returnAmt').textContent) || 0,
    };

    const saveBtn = document.getElementById('saveBillBtn');
    saveBtn.disabled = true;
    saveBtn.textContent = 'Saving...';

    fetch('/patient/billing/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
      .then((res) => {
        if (!res.ok) throw new Error('Save failed');
        return res.json();
      })
      .then((data) => {
        // data.bill_id comes back from the Flask save route
        window.location.href = `/generate_bill/${data.bill_id}`;
      })
      .catch(() => {
        alert('Failed to save the bill. Please try again.');
        saveBtn.disabled = false;
        saveBtn.textContent = 'Save (F12)';
      });
  });

  // F12 keyboard shortcut for Save, matching the button label
  document.addEventListener('keydown', function (e) {
    if (e.key === 'F12') {
      e.preventDefault();
      document.getElementById('saveBillBtn').click();
    }
  });

  // Start with one empty entry row
  createEntryRow();
  updateEmptyState();
});