// Shipped Orders Page
function formatShippedOrders(orders) {
  return `
    <div class="card">
      <div class="listings">
        <div class="listing-item shipped-item header-row">
          <span>Image</span>
          <span>Customer</span>
          <span>Item</span>
          <span>Variant</span>
          <span>Date</span>
          <span>Qty</span>
          <span>Price / Profit</span>
          <span>SS</span>
        </div>
        ${orders.map(order => {
          const screenshot = order.shipping_screenshot
            ? `http://82.42.112.27:5000/api/shipping-screenshot/${order.shipping_screenshot}`
            : null;
          const variations = (order.variation_aspects && order.variation_aspects.length)
            ? order.variation_aspects.map(v => v.value).join(', ')
            : 'Default';
          const ebayImg = order.ebay_img || 'default-image-url';
          const fullName = order.full_name || 'Unknown Customer';
          const itemTitle = order.item_title || 'Unknown Item';
          const shippedDate = order.shipped || 'Unknown Date';
          const quantity = order.quantity || 1;
          const ebayPrice = order.ebay_price || 0;
          const aliPrice = order.ali_price || 0;

          return `
            <div class="listing-item shipped-item">
              <img src="${ebayImg}" alt="Product">
              <p class="customer-name">${fullName}</p>
              <p class="item-title">${itemTitle}</p>
              <p class="variation-aspects">${variations}</p>
              <span class="date">${shippedDate}</span>
              <span class="quantity">${quantity}</span>
              <span class="price">
                <span id="revenue">£${(ebayPrice).toFixed(2)}</span>
                <span id="profit" class="profit">£${(ebayPrice - aliPrice).toFixed(2)}</span>
              </span>
              ${screenshot ? `
              <span class="view-img" onclick="showScreenshot('${screenshot}')">
                <i class="fas fa-camera"></i>
              </span>` : '<span></span>'}
            </div>
          `;
        }).join('')}
      </div>
    </div>
  `;
}