// serverLogs.js

function formatServerLogs(logs) {
  return `
    <div class="card">
      <div class="listings">
        <div class="listing-item log-item header-row">
          <span>Image</span>
          <span>Customer</span>
          <span>Item</span>
          <span>Variant</span>
          <span>Qty</span>
          <span>Fail Reason</span>
          <span>Fix</span>
        </div>
        ${logs.map((log, index) => {
          const imageOrScreenshot = log.shipping_screenshot
            ? `http://82.42.112.27:5000/api/shipping-screenshot/${log.shipping_screenshot}`
            : log.ebay_img;
          const variations = (log.variation_aspects && log.variation_aspects.length)
            ? log.variation_aspects.map(v => v.value).join(', ')
            : 'Default';

          return `
            <div class="listing-item log-item" data-index="${index}" style="position: relative;">
              <img src="${imageOrScreenshot}" alt="Product">
              <p class="customer-name">${log.full_name}</p>
              <p class="item-title">${log.item_title}</p>
              <p class="variation-aspects">${variations}</p>
              <span class="quantity">${log.quantity}</span>
              <p class="fail-reason">${log.fail_reason}</p>
              <button class="fix-btn main-btn">Fix</button>

              <div class="fix-modal modal hidden card">
                <div class="modal-content">
                  <label>Full Name: <input class="fixFullName" value="${log.full_name}" /></label>
                  <label>Address Line 1: <input class="fixAddress1" value="${log.address_line1}" /></label>
                  <label>Address Line 2: <input class="fixAddress2" value="${log.address_line2}" /></label>
                  <label>City: <input class="fixCity" value="${log.city}" /></label>
                  <label>Postal Code: <input class="fixPostCode" value="${log.postal_code}" /></label>
                  <label>Country: <input class="fixCountry" value="${log.country}" /></label>
                  <label>Phone: <input class="fixPhone" value="${log.phone}" /></label>
                  <label>Item ID: <input class="fixItemId" value="${log.item_id}" disabled /></label>
                  <button class="sendFix main-btn">Retry Order</button>
                </div>
              </div>
            </div>
          `;
        }).join('')}
      </div>
    </div>
  `;
}

document.addEventListener("click", async (e) => {
  // Show modal
  if (e.target.classList.contains("fix-btn")) {
    const item = e.target.closest(".log-item");
    const modal = item.querySelector(".fix-modal");
    modal.classList.remove("hidden");
  }

  // Submit modal
  if (e.target.classList.contains("sendFix")) {
    const modal = e.target.closest(".fix-modal");

    const payload = {
      full_name: modal.querySelector(".fixFullName").value,
      address_line1: modal.querySelector(".fixAddress1").value,
      address_line2: modal.querySelector(".fixAddress2").value,
      city: modal.querySelector(".fixCity").value,
      postal_code: modal.querySelector(".fixPostCode").value,
      country: modal.querySelector(".fixCountry").value,
      phone: modal.querySelector(".fixPhone").value,
      item_id: modal.querySelector(".fixItemId").value,
    };

    await fetch("http://82.42.112.27:5000/api/retry-order", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });    

    modal.classList.add("hidden");
  }
});