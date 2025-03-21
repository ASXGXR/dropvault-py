/**
 * Ebay Listings Page
 */

// Ebay Page
function formatEbayListings(listings) {
  return `<div class="card ebay-listings">
    <div class="listings">
      <div class="listing-item ebay-item header-row">
        <span>Ebay Listing</span>
        <span></span>
        <span>Price</span>
        <span>Item Link (Aliexpress)</span>
        <span>Variants</span>
      </div>
      ${listings.map(({ title, item_id, item_url, image_url, price, aliexpress_url, variations }) => {
        const aliUrl = aliexpress_url || '';
        const isLinked = aliUrl ? ' linked' : '';

        let variationList = Object.entries(variations || {})
          .filter(([key]) => key.toLowerCase() !== 'size')
          .flatMap(([, values]) => values || []);

        const unlinkedCount = variationList.filter(v => !v["ali-value"]).length;
        const variationsHTML = variationList.length
          ? variationList.map(v => `<span class="variation-circle${!v["ali-value"] ? ' unlinked-circle' : ''}" title="${v.value}" data-item-id="${item_id}">${v.value}</span>`).join('')
          : `<span class="variation-circle${!aliUrl ? ' unlinked-circle' : ''}" title="Default" data-item-id="${item_id}">Default</span>`;

        return `
        <div class="listing-item ebay-item" data-title="${title}" data-item-id="${item_id}">
          <img src="${image_url}" alt="Product">
          <a href="${item_url}" target="_blank">${title}</a>
          <span class="price">£${price}</span>
          <span class="link-wrapper${isLinked}">
            <input class="url-input" type="text" placeholder="Aliexpress URL..." data-item-id="${item_id}" value="${aliUrl}">
            <a href="${aliUrl}" class="auto-link fas fa-external-link-alt" target="_blank"></a>
          </span>

          <span>
            ${aliUrl ? `
              <div class="variants-wrapper">
                <span class="variation-icons">${variationsHTML}</span>
                ${unlinkedCount > 0 ? `<a href="${aliUrl}" class="unlinked-count" target="_blank">${unlinkedCount} variants unlinked</a>` : ''}
                ${unlinkedCount === 0 ? `<div class="linked-tick">✔</div>` : ''}
              </div>` : ''}
          </span>
        </div>`;
      }).join('')}
    </div>
  </div>`;
}

// Update Aliexpress link on input change
function updateAliLink() {
  document.querySelectorAll(".listing-item").forEach(item => {
    const input = item.querySelector(".url-input");
    const linkWrapper = item.querySelector(".link-wrapper");
    const link = item.querySelector(".auto-link");

    if (input && linkWrapper && link) {
      console.log(1);
      input.addEventListener("input", () => {
        console.log(2);
        const aliUrl = input.value.trim();
        const itemId = input.dataset.itemId;
        
        // Check if aliUrl valid
        if (aliUrl === "" || aliUrl.startsWith("https://www.aliexpress.com/item/")) {
          console.log(3);
          if (aliUrl === "") {
            linkWrapper.classList.remove("linked"); // Remove "linked" styling
            link.href = "#"; // Prevents broken links
          } else {
            linkWrapper.classList.add("linked");
            link.href = aliUrl;
          }
    
          // Send API update
          fetch("http://82.42.112.27:5000/api/update-aliexpress", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ item_id: itemId, aliexpress_url: aliUrl }) // Send empty string if cleared
          })
          .then(response => {
            if (!response.ok) throw new Error("Update failed");
            console.log(`API updated successfully: ${aliUrl || "URL removed"}`);
            delete cachedData["ebay-listings"]; // Clear cache for fresh fetch
          })
          .catch(err => console.error("Error updating Aliexpress link:", err));
        }
      });
    }    
  });
}