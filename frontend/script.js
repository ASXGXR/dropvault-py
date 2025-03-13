// script.js

const cachedData = {};
let countedUp = false;

document.addEventListener("DOMContentLoaded", () => {
    const dashboard = document.getElementById("dashboard");
    defaultDashboardContent = dashboard.innerHTML;
    initDashboard();
});

/**
 * Initialize Dashboard Elements & Fetch Data
 */
function initDashboard() {
    loadEbayListings();
    initializeChart();
    loadSeparatePages();
    focusOnEnter();
    adjustScrollSpeed();
    updateVariantValues();
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

/**
 * Format eBay Listings
 */

// Home Page
function formatHomeEbayListings(listings) {
  let noLinkCount = listings.filter(listing => !listing.aliexpress_url).length; // Count all items without links

  const formattedListings = listings.slice(0, 2).map(listing => {
      const searchUrl = `https://www.aliexpress.com/wholesale?SearchText=${encodeURIComponent(listing.title)}`;
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
                  <a href="${searchUrl}" class="auto-link" target="_blank">Search on Ali <i class="fas fa-external-link-alt"></i></a>
              </div>
          </div>`;
  }).join("");

  const listWrapper = document.querySelector(".list-wrapper");
  document.getElementById("new-items").textContent = noLinkCount; // Update the count in the UI
  if (noLinkCount === 0 && listWrapper) {
      listWrapper.style.display = "none"; // Hide if no items need linking
  }

  return formattedListings;
}

// Ebay Page
function formatEbayListings(listings) {
  return `<div class="card"><div class="listings">${
    listings.map(listing => {
      const searchUrl = `https://www.aliexpress.com/wholesale?SearchText=${encodeURIComponent(listing.title)}`;
      const isLinked = listing.aliexpress_url ? ' linked' : '';
      const aliUrl = listing.aliexpress_url || '';

      let variationsArr = [];
      if (listing.variations && typeof listing.variations === 'object') {
        variationsArr = Object.entries(listing.variations)
          .filter(([key]) => key.toLowerCase() !== 'size')
          .map(([, value]) => value)
          .flat();
      }

      let variations = '';
      if (variationsArr.length > 0) { // Variations exist
        variations = variationsArr.map(v => {
          const unlinkedClass = !v["ali-value"] ? ' unlinked-circle' : '';
          return `<span class="variation-circle${unlinkedClass}" title="${v.value}" data-item-id="${listing.item_id}">${v.value}</span>`;
        }).join('');
      } else { // No variations, show Default
        const aliValue = listing["ali-value"] || '';
        const unlinkedClass = !aliValue ? ' unlinked-circle' : '';
        variations = `<span class="variation-circle${unlinkedClass}" title="Default" data-item-id="${listing.item_id}">Default</span>`;
      }      

      const unlinkedCount = variationsArr.length > 0
        ? variationsArr.filter(v => !v["ali-value"]).length
        : (!listing["ali-value"] ? 1 : 0);    

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
          <a href="${searchUrl}" class="auto-link" target="_blank">Search on Ali <i class="fas fa-external-link-alt"></i></a>
        </div>
        ${aliUrl ? `<div class="variants-wrapper">
          <span class="variation-icons">${variations}</span>
          ${unlinkedCount > 0 ? `<a href="${aliUrl}" class="unlinked-count" target="_blank">${unlinkedCount} variants unlinked</a>` : ''}
          ${unlinkedCount === 0 ? `<div class="linked-tick">✔</div>` : ''}
        </div>` : ''}
      </div>`;
    }).join('')
  }</div></div>`;
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
    let value = prompt(`Enter "Color:" value for "${variantTitle}":`);

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
        <div class="listing-item header-row">
          <span>Image</span>
          <span>Customer</span>
          <span>SS</span>
          <span>Title</span>
          <span>Variation</span>
          <span>Date</span>
          <span>Qty</span>
          <span>Price / Profit</span>
        </div>
        ${orders.map(order => {
          const profitClass = parseFloat(order.profit) >= 0 ? 'green' : 'red';
          const screenshot = order.shipping_screenshot
            ? `http://82.42.112.27:5000/api/shipping-screenshot/${order.shipping_screenshot}`
            : null;
          const variations = (order.variation_aspects && order.variation_aspects.length)
            ? order.variation_aspects.map(v => v.value).join(', ')
            : 'Default';

          return `
            <div class="listing-item">
              <img src="${order.ebay_img}" alt="Product">
              <p class="customer-name">${order.full_name}</p>
              ${screenshot ? `
              <span class="view-img" onclick="showScreenshot('${screenshot}')">
                <i class="fas fa-camera"></i>
              </span>` : '<span></span>'}
              <p class="item-title">${order.item_title}</p>
              <p class="variation-aspects">${variations}</p>
              <span class="date">${order.shipped}</span>
              <span class="quantity">${order.quantity}</span>
              <span class="price">
                <span id="revenue">£${parseFloat(order.ebay_price).toFixed(2)}</span>
                <span id="profit" class="${profitClass}">${order.profit >= 0 ? '+' : ''}£${parseFloat(order.profit).toFixed(2)}</span>
              </span>
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

// Server Logs Page
function formatServerLogs(logs) {
  return `
    <div class="card">
      <div class="listings">
        <div class="listing-item header-row">
          <span>Order ID</span>
          <span>Customer</span>
          <span>Item Title</span>
          <span>Quantity</span>
          <span>Cost</span>
          <span>Shipped</span>
          <span>Profit</span>
        </div>
        ${logs.map(log => `
          <div class="listing-item">
            <span>${log.order_id}</span>
            <span>${log.full_name}</span>
            <span>${log.item_title}</span>
            <span>${log.quantity}</span>
            <span>£${parseFloat(log.item_cost).toFixed(2)}</span>
            <span>${log.shipped}</span>
            <span>£${parseFloat(log.profit).toFixed(2)}</span>
          </div>
        `).join('')}
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
  console.log(page);
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
        console.log(html); // Debug: log fetched HTML
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
  const increment = targetValue / 100; // Smaller values = quicker
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
  let totalProfit = 0, weeklyItems = 0;
  let oneWeekAgo = new Date();
  oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);
  oneWeekAgo.setHours(0, 0, 0, 0); // Normalize to start of day
  try {
      const res = await fetch("http://82.42.112.27:5000/api/shipped-orders");
      const salesData = await res.json();
      salesData?.forEach(({ shipped, profit = 0, quantity = 1 }) => {
          // Parse date correctly
          const [day, month, year] = shipped.split(" ")[0].split("-");
          const shippedDate = new Date(`${year}-${month}-${day}`);
          if (isNaN(shippedDate)) {
              console.warn("Invalid date:", shipped);
              return;
          }
          const dayName = shippedDate.toLocaleString("en-GB", { weekday: "short" });
          // Sum profits and items
          totalProfit += parseFloat(profit);
          if (shippedDate >= oneWeekAgo) weeklyItems += quantity;
          // Add profit to day
          if (profitByDay[dayName] !== undefined) profitByDay[dayName] += parseFloat(profit);
      });
      document.getElementById("total-profit").textContent = ` £${totalProfit.toFixed(2)}`;
      document.getElementById("weekly-items").textContent = weeklyItems;

      // ✅ Now that total-revenue is set, run count up
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
            data: Object.values(profitByDay), 
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
