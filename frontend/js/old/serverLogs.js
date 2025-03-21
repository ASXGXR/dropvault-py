// Server Logs Page
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
        </div>
        ${logs.map(log => {
          const imageOrScreenshot = log.shipping_screenshot
            ? `http://82.42.112.27:5000/api/shipping-screenshot/${log.shipping_screenshot}`
            : log.ebay_img;
          const variations = (log.variation_aspects && log.variation_aspects.length)
            ? log.variation_aspects.map(v => v.value).join(', ')
            : 'Default';


          return `
            <div class="listing-item log-item">
              <img src="${imageOrScreenshot}" alt="Product">
              <p class="customer-name">${log.full_name}</p>
              <p class="item-title">${log.item_title}</p>
              <p class="variation-aspects">${variations}</p>
              <span class="quantity">${log.quantity}</span>
              <p class="fail-reason">${log.fail_reason}</p>
            </div>
          `;
        }).join('')}
      </div>
    </div>
  `;
}