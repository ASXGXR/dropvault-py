/**
 * Dashboard Script
 * Cleaned and Optimized for Readability & Maintainability
 */

const cachedData = {};

document.addEventListener("DOMContentLoaded", () => {
    const dashboard = document.getElementById("dashboard");
    defaultDashboardContent = dashboard.innerHTML;
    initDashboard();
    countUp();
});

/**
 * Initialize Dashboard Elements & Fetch Data
 */
function initDashboard() {
    loadEbayListings();
    initializeChart();
    loadSeparatePages();
    focusOnEnter();
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
                  <span class="variation-icons"></span>
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
  let html = '<div class="card"><div class="listings">';
  listings.forEach(listing => {
    const searchUrl = `https://www.aliexpress.com/wholesale?SearchText=${encodeURIComponent(listing.title)}`;
    const isLinked = listing.aliexpress_url ? ' linked' : '';
    const aliUrl = listing.aliexpress_url || '';
    let variationCircles = '';
    // listing.variations.forEach(variation => {
    //   variationCircles += <span class="variation-circle" style="background-color: ${variation.type.toLowerCase()};" title="${variation.type}"></span>;
    // });
    html += `
      <div class="listing-item" data-title="${listing.title}" data-item-id="${listing.item_id}">
        <a href="${listing.item_url}" class="img-and-title" target="_blank">
          <img src="${listing.image_url}" alt="Product">
          <p>${listing.title}</p>
          <span class="variation-icons">${variationCircles}</span>
          <span class="price">£${listing.price}</span>
        </a>
        <div class="vert-line"></div>
        <div class="link-wrapper${isLinked}">
          <input class="url-input" 
                 type="text" 
                 placeholder="Aliexpress URL..." 
                 data-item-id="${listing.item_id}"
                 value="${aliUrl}">
          <a href="${searchUrl}" class="auto-link" target="_blank">Search on Ali <i class="fas fa-external-link-alt"></i></a>
        </div>
      </div> `
    ;
  });
  html += '</div></div>';
  return html;
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
 * Count Up Animation for Sales
 */
function countUp() {
  const salesElement = document.querySelector(".card-title .green");
  if (!salesElement) return;

  const targetValue = parseInt(salesElement.innerText.replace(/[^0-9]/g, ""), 10);
  let currentValue = 0;
  const increment = targetValue / 125; // Approximate duration of 2s at 16ms per frame

  const counter = setInterval(() => {
      currentValue += increment;
      if (currentValue >= targetValue) {
          currentValue = targetValue;
          clearInterval(counter);
      }
      salesElement.innerText = `£${Math.floor(currentValue).toLocaleString()}`;
  }, 16);
}

/**
 * Handle URL Input Focus and Updates
 */
function focusOnEnter() {
  document.querySelectorAll(".listing-item").forEach(item => {
      const input = item.querySelector(".url-input");
      const linkWrapper = item.querySelector(".link-wrapper");
      if (!input || linkWrapper.classList.contains("linked")) return;
      item.addEventListener("mouseenter", () => setTimeout(() => input.focus({ preventScroll: true }), 50));

      input.addEventListener("change", () => {
          const aliUrl = input.value.trim();
          const itemId = input.dataset.itemId;
          const isValidAliUrl = aliUrl.includes("https://www.aliexpress.com/item/");
          // Immediate UI update
          linkWrapper.classList.toggle("linked", isValidAliUrl);
          // Fire & forget API update
          updateAliLink(itemId, aliUrl);
      });
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
 * Weekly Sales Chart
 */
async function initializeChart() { 
  const canvas = document.getElementById("weeklySalesChart");
  if (!canvas) return;

  let salesByDay = { "Mon": 0, "Tue": 0, "Wed": 0, "Thu": 0, "Fri": 0, "Sat": 0, "Sun": 0 };
  let totalRevenue = 0, weeklyItems = 0, oneWeekAgo = new Date();
  oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);

  try {
      const res = await fetch("http://82.42.112.27:5000/api/shipped-orders");
      const salesData = await res.json();

      salesData?.forEach(({ shipped, total_price = 0, quantity = 1 }) => {
          const day = new Date(shipped).toLocaleString("en-GB", { weekday: "short" });
          totalRevenue += parseFloat(total_price);
          if (new Date(shipped) >= oneWeekAgo) weeklyItems += quantity;
          if (salesByDay[day] !== undefined) salesByDay[day] += parseFloat(total_price);
      });

      document.getElementById("total-revenue").textContent = ` £${totalRevenue.toFixed(2)}`;
      document.getElementById("weekly-items").textContent = weeklyItems;
  } catch (error) {
      console.error("Error fetching sales data:", error);
  }

  new Chart(canvas.getContext("2d"), {
      type: "line",
      data: { labels: Object.keys(salesByDay), datasets: [{ label: "Revenue (£)", data: Object.values(salesByDay), borderColor: "rgba(54, 162, 235, 1)", backgroundColor: "rgba(54, 162, 235, 0.2)", borderWidth: 2, pointRadius: 4, pointBackgroundColor: "rgba(54, 162, 235, 1)", fill: true }] },
      options: { responsive: true, maintainAspectRatio: false, aspectRatio: 2.9, scales: { y: { beginAtZero: true } } }
  });
}