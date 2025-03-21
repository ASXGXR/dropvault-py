// script.js

/**
 * Initialize Variables
 */

const cachedData = {};
let countedUp = false;


/**
 * Initialize Dashboard Elements & Fetch Data
 */


// DOC LOAD:
document.addEventListener("DOMContentLoaded", () => {
  const dashboard = document.getElementById("dashboard");
  defaultDashboardContent = dashboard.innerHTML;
  initDashboard();
});


function initDashboard() {
    loadEbayListings();
    loadHomeShippedOrders();
    initializeChart();
    loadSeparatePages();
    focusOnEnter();
    adjustScrollSpeed();
    updateVariantValues();
    logFailedOrdersCount();
}


/**
 * Load eBay Listings for the Home Page
 */
function loadEbayListings() {
    if (document.getElementById("home-ebay-listings")) {
        fetchData("ebay-listings", "home-ebay-listings", formatHomeEbayListings);
        setTimeout(focusOnEnter, 100);
    }
}
function loadHomeShippedOrders() {
  if (document.getElementById("home-shipped-orders")) {
      fetchData("shipped-orders", "home-shipped-orders", formatHomeShippedOrders);
  }
}


/**
 * Load Content for Separate Pages
 */
function loadSeparatePages() {
  if (document.getElementById("ebay-listings")) {
      fetchData("ebay-listings", "ebay-listings", formatEbayListings);
  }
  if (document.getElementById("shipped-orders")) {
      fetchData("shipped-orders", "shipped-orders", formatShippedOrders);
  }
  if (document.getElementById("server-logs")) {
      fetchData("failed-shipments", "server-logs", formatServerLogs);
  }
}
// Shipping Errors / Failed Orders
function logFailedOrdersCount() {
  fetch('http://82.42.112.27:5000/api/failed-shipments')
    .then(res => res.json())
    .then(data => {
      console.log(`Failed Orders Count: ${data.length}`);
      const el = document.getElementById('failed_shipments');
      const errorNav = document.getElementById('error-nav');
      const shippingErrors = document.getElementById('shipping-errors');
      const errorWrapper = document.querySelector('.title-error-wrapper'); // ✅ Grab error-wrapper


      if (errorWrapper) errorWrapper.style.visibility = data.length ? 'visible' : 'hidden'; // ✅ Hide if none
      
      if (el) el.innerHTML = data.length ? `<span class="notif">${data.length}</span>` : '';
      if (errorNav) errorNav.style.display = data.length ? 'block' : 'none';
      if (shippingErrors) shippingErrors.innerText = data.length; // Update shipping errors count
    })
    .catch(console.error);
}


/**
 * Format eBay Listings
 */


// Home Page
function formatHomeEbayListings(listings) {
  let noLinkCount = listings.filter(listing => !listing.aliexpress_url).length; // Count all items without links


  const formattedListings = listings.slice(0, 2).map(listing => {
      const aliUrl = listing.aliexpress_url || "";
      const isLinked = listing.aliexpress_url ? " linked" : "";


      return `
          <div class="listing-item" data-title="${listing.title}" data-item-id="${listing.item_id}">
              <a href="${listing.item_url}" class="img-and-title" target="_blank">
                  <img src="${listing.image_url}" alt="Product">
                  <p>${listing.title}</p>
                  <span class="price">£${listing.price}</span>
              </a>
              <div class="vert-line"></div>
              <div class="link-wrapper${isLinked}">
                  <input class="url-input" type="text" placeholder="Aliexpress URL..." data-item-id="${listing.item_id}" value="${aliUrl}">
              </div>
          </div>`;
  }).join("");


  const linkWrapper = document.querySelector(".title-link-wrapper");
  document.getElementById("new-items").textContent = noLinkCount; // Update the count in the UI
  if (linkWrapper) {
    linkWrapper.style.visibility = noLinkCount === 0 ? "hidden" : "visible"; // Show if items need linking
  }
  return formattedListings;
}


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
      ${listings.map(({ title, item_id, item_url, image_url, price, aliexpress_url, variations, ["ali-value"]: aliValue }) => {
        const aliUrl = aliexpress_url || '';
        const isLinked = aliUrl ? ' linked' : '';

        let variationList = Object.entries(variations || {})
          .filter(([key]) => key.toLowerCase() !== 'size')
          .flatMap(([, values]) => values || []);

        const unlinkedCount = variationList.filter(v => !v["ali-value"]).length;
        const variationsHTML = variationList.length
          ? variationList.map(v => `
            <span class="variation-circle${!v["ali-value"] ? ' unlinked-circle' : ''}" 
              title="${v.value}" 
              data-item-id="${item_id}" 
              data-ali-value="${v['ali-value'] || 'None'}">
              ${v.value}
            </span>`).join('')
          : `<span class="variation-circle${!aliUrl ? ' unlinked-circle' : ''}" 
              title="Default" 
              data-item-id="${item_id}" 
              data-ali-value="${aliValue || 'None'}">
              Default
            </span>`;

        return `
        <div class="listing-item ebay-item" data-title="${title}" data-item-id="${item_id}">
          <img src="${image_url}" alt="Product">
          <a href="${item_url}" target="_blank">${title}</a>
          <span class="price">£${price}</span>
          <span class="link-wrapper${isLinked}">
            <input class="url-input" type="text" placeholder="Aliexpress URL..." data-item-id="${item_id}" value="${aliUrl}">
            <a href="${aliUrl}" class="auto-link fas fa-external-link-alt" target="_blank"></a>
          </span>

          ${aliUrl ? ` 
            <div class="variants-wrapper">
              <span class="variation-icons">${variationsHTML}</span>
              ${unlinkedCount > 0 ? `<a href="${aliUrl}" class="unlinked-count" target="_blank">${unlinkedCount} variants unlinked</a>` : ''}
              ${unlinkedCount === 0 ? `<div class="linked-tick">✔</div>` : ''}
            </div>` : ''}
        </div>`;
      }).join('')}
    </div>
  </div>`;
}

// Click listeners on all variant circles
let variantListenerAttached = false;

function updateVariantValues() {
  if (variantListenerAttached) return; // Prevent multiple bindings
  variantListenerAttached = true;

  document.addEventListener('click', async (e) => {
    if (!e.target.classList.contains('variation-circle')) return;

    const variantTitle = e.target.title;
    const listingId = e.target.dataset.itemId; // Now grabbed directly from circle
    const currentValue = e.target.dataset.aliValue || 'None'; // Get current value if available

    let value = prompt(`Enter "Color:" value for "${variantTitle}" (Current: ${currentValue}) (Use 'default' if only one listing on ali):`);

    if (value !== null) { // Check not cancelled
      value = value.trim();
      if (value) { // Check not empty
        try {
          const res = await fetch('http://82.42.112.27:5000/api/update-variant', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ value, listingId, variantTitle })
          });
          if (!res.ok) throw new Error('Failed to update variant');
          console.log('Variant updated:', await res.json());
          // Remove unlinked-circle
          e.target.classList.remove('unlinked-circle');
        } catch (err) {
          console.error(err);
        }
      }
    }
  });
}


// Shipped Orders Page
function formatShippedOrders(orders) {
  return `
    <div class="card">
      <div class="listings">
        <div class="listing-item shipped-item header-row">
          <span>Shipped Item</span>
          <span></span>
          <span>Customer</span>
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
              <p class="item-title">${itemTitle}</p>
              <p class="customer-name">${fullName}</p>
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


// Modal to display screenshot
function showScreenshot(url) {
  const m = document.createElement('div');
  m.id = 'screenshot-modal';
  m.innerHTML = `
    <span class="close-btn">&times;</span>
    <div class="modal-content">
      <img src="${url}" alt="Shipping Screenshot">
    </div>`;
  m.querySelector('.close-btn').onclick = () => m.remove();
  document.addEventListener('keydown', function esc(e) {
    if (e.key === 'Escape') {
      m.remove();
      document.removeEventListener('keydown', esc);
    }
  });
  document.body.appendChild(m);
}


// Home shipped orders
function formatHomeShippedOrders(orders) {
  const header = `
    <div class="listing-item home-shipped-item header-row">
      <span>Listing</span>
      <span></span>
      <span>Date</span>
      <span>Price</span>
    </div>
  `;
  const items = orders.slice(0, 5).map(order => {
      return `
          <div class="listing-item home-shipped-item">
              <img src="${order.ebay_img}" alt="Product">
              <p class="item-title">${order.item_title}</p>
              <span class="date">${order.shipped}</span>
              <span class="price">
                <span id="revenue">£${parseFloat(order.ebay_price).toFixed(2)}</span>
                <span id="profit" class="profit xsmall">£${(order.ebay_price - order.ali_price).toFixed(2)}</span>
              </span>
          </div>
      `;
  }).join('');
  return header + items;
}




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


/**
 * URL Input Focus
 */
function focusOnEnter() {
  let focusOnHover = false; // whether to focus on hover


  document.querySelectorAll(".listing-item").forEach(item => {
      const input = item.querySelector(".url-input");
      const linkWrapper = item.querySelector(".link-wrapper");
      if (input && linkWrapper) {
        if (!linkWrapper.classList.contains("linked") && focusOnHover) { // ignores linked inputs
          item.addEventListener("mouseenter", () => setTimeout(() => input.focus({ preventScroll: true }), 50));
        }
        input.addEventListener("change", () => {
            const aliUrl = input.value.trim();
            const itemId = input.dataset.itemId;
            const isValidAliUrl = aliUrl.includes("https://www.aliexpress.com/item/");
            // Immediate UI update
            linkWrapper.classList.toggle("linked", isValidAliUrl);
            // Send API update
            updateAliLink(itemId, aliUrl);
        });
      }
  });
}


function updateAliLink(itemId, aliUrl) {
    fetch("http://82.42.112.27:5000/api/update-aliexpress", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ item_id: itemId, aliexpress_url: aliUrl })
    }).catch(err => console.error(err));
}


/**
 * Change Page Content Dynamically
 */
function openPage(page) {
    const dashboard = document.getElementById("dashboard");
    document.querySelectorAll(".nav-btn").forEach(btn => btn.classList.remove("active-nav"));
    const activeButton = [...document.querySelectorAll(".nav-btn")].find(btn => btn.getAttribute("onclick").includes(page));
    if (activeButton) activeButton.classList.add("active-nav");
    if (page === "main") {
        dashboard.innerHTML = defaultDashboardContent;
        initDashboard();
        return;
    }
    fetch(page)
        .then(res => res.ok ? res.text() : Promise.reject("Error loading page"))
        .then(html => {
            dashboard.innerHTML = html;
            initDashboard();
        })
        .catch(err => {
            console.error(err);
            dashboard.innerHTML = "<p>Error loading page.</p>";
        });
}


/**
 * Fetch Data from API
 */
function fetchData(endpoint, elementId, formatter = JSON.stringify) {
    if (cachedData[endpoint]) {
        document.getElementById(elementId).innerHTML = formatter(cachedData[endpoint]);
        if (elementId === "ebay-listings") focusOnEnter();
        return;
    }
    
    fetch(`http://82.42.112.27:5000/api/${endpoint}`)
        .then(res => res.json())
        .then(data => {
            cachedData[endpoint] = data;
            document.getElementById(elementId).innerHTML = formatter(data);
            if (elementId === "ebay-listings") focusOnEnter();
        })
        .catch(err => console.error(`Error fetching ${endpoint}:`, err));
}


/**
 * Count Up Animation
 */
function countUp() {
  if (countedUp) return; // Prevent running more than once
  countedUp = true;
  const salesElement = document.getElementById("total-profit");
  if (!salesElement) return;
  const targetValue = parseFloat(salesElement.innerText.replace(/[^0-9.]/g, ""));
  let currentValue = 0;
  const increment = targetValue / 75; // Smaller values = quicker
  const counter = setInterval(() => {
    currentValue += increment;
    if (currentValue >= targetValue) {
      currentValue = targetValue;
      clearInterval(counter);
    }
    salesElement.innerText = `£${currentValue.toFixed(2)}`;
  }, 16);
}


/**
 * Weekly Sales Chart
 */
async function initializeChart() {  
  const canvas = document.getElementById("weeklySalesChart");
  if (!canvas) return;

  let profitByDay = { "Mon": 0, "Tue": 0, "Wed": 0, "Thu": 0, "Fri": 0, "Sat": 0, "Sun": 0 };
  let totalProfit = 0, weeklyItems = 0, past7DaysItems = 0;

  let startOfWeek = new Date();
  startOfWeek.setDate(startOfWeek.getDate() - startOfWeek.getDay() + 1); // Start of this week (Monday)
  startOfWeek.setHours(0, 0, 0, 0);

  let today = new Date();
  today.setHours(0, 0, 0, 0);

  let oneWeekAgo = new Date();
  oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);
  oneWeekAgo.setHours(0, 0, 0, 0); // Keep previous 7 days check

  try {
      const res = await fetch("http://82.42.112.27:5000/api/shipped-orders");
      const salesData = await res.json();

      salesData?.forEach(order => {
          // Default values if missing
          const shipped = order.shipped || "01-01-1970"; // Default date to avoid NaN
          const ebay_price = parseFloat(order.ebay_price) || 0;
          const ali_price = parseFloat(order.ali_price) || 0;
          const quantity = parseInt(order.quantity) || 1;

          const profit = (ebay_price - ali_price).toFixed(2);

          // Parse date correctly
          const [day, month, year] = shipped.split(" ")[0].split("-");
          const shippedDate = new Date(`${year}-${month}-${day}`);

          if (isNaN(shippedDate.getTime())) {
              console.warn("Invalid date:", shipped);
              return;
          }

          // Ensure total profit includes all sales
          totalProfit += parseFloat(profit);

          if (shippedDate >= oneWeekAgo && shippedDate <= today) past7DaysItems += quantity;
          if (shippedDate >= startOfWeek && shippedDate <= today) {
              const dayName = shippedDate.toLocaleString("en-GB", { weekday: "short" });
              weeklyItems += quantity;

              if (profitByDay[dayName] !== undefined) profitByDay[dayName] += parseFloat(profit);
          }
      });

      // Default to zero if no valid data was found
      totalProfit = totalProfit || 0;
      past7DaysItems = past7DaysItems || 0;
      weeklyItems = weeklyItems || 0;

      document.getElementById("total-profit").textContent = `£${totalProfit.toFixed(2)}`;
      document.getElementById("weekly-items").textContent = `${past7DaysItems} items`;

      countUp();
  } catch (error) {
      console.error("Error fetching sales data:", error);
  }

  // Render profit chart
  new Chart(canvas.getContext("2d"), {
      type: "line",
      data: { 
          labels: Object.keys(profitByDay), 
          datasets: [{ 
              label: "Profit (£)", 
              data: Object.values(profitByDay).map(val => val || 0), // Ensure no NaNs
              borderColor: "rgba(54, 162, 235, 1)", 
              backgroundColor: "rgba(54, 162, 235, 0.2)", 
              borderWidth: 2, 
              pointRadius: 4, 
              pointBackgroundColor: "rgba(54, 162, 235, 1)", 
              fill: true 
          }] 
      },
      options: { 
          responsive: true, 
          maintainAspectRatio: false, 
          aspectRatio: 2.9, 
          scales: { y: { beginAtZero: true } } 
      }
  });
}


function adjustScrollSpeed() {
  document.querySelectorAll('.variation-icons').forEach(el => {
    el.addEventListener('wheel', function(e) {
      e.preventDefault(); // Stop default scroll
      el.scrollTop += e.deltaY * 0.2; // Adjust scroll speed (lower = slower)
    }, { passive: false });
  });
}