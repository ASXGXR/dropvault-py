
// DOM Fully Loaded

const cachedData = {};


document.addEventListener("DOMContentLoaded", function () {
    const dashboard = document.getElementById("dashboard");
    defaultDashboardContent = dashboard.innerHTML; // Save original content
    initDashboard(); // Load scripts
    countUp(); // Count Up Money
});


// On Page Load / Switch

function initDashboard() {

  // Fetch Ebay Data
  // ebay Orders
  if (document.getElementById("orders")) {
    fetchData(endpoint="orders", elementId="orders", data => `<pre>${JSON.stringify(data, null, 2)}</pre>`);
  }
  // ebay Listings
  if (document.getElementById("ebay-listings")) {
    fetchData(endpoint="ebay-listings", elementId="ebay-listings", formatEbayListings);
  }

  // Reinitialize your chart here if needed
  const canvas = document.getElementById('weeklySalesChart');
  if (canvas) {
    const ctx = canvas.getContext('2d');
    new Chart(ctx, {
      type: 'line',
      data: {
        labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        datasets: [{
          label: 'Sales (£)',
          data: [12, 20, 15, 30, 25, 40, 50],
          borderColor: 'rgba(54, 162, 235, 1)',
          backgroundColor: 'rgba(54, 162, 235, 0.2)',
          borderWidth: 2,
          pointRadius: 4,
          pointBackgroundColor: 'rgba(54, 162, 235, 1)',
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

  focusOnEnter(); // URL Input Focus

  autoLinkSearch(); // Auto link search

}



// (NAV) Changing page content

function openPage(page) {
  const dashboard = document.getElementById("dashboard");

  // add 'active-nav' class
  document.querySelectorAll(".nav-btn").forEach(btn => btn.classList.remove("active-nav"));
  const activeButton = [...document.querySelectorAll(".nav-btn")].find(btn => 
    btn.getAttribute("onclick").includes(page)
  );
  if (activeButton) activeButton.classList.add("active-nav");

  // switch page content
  if (page === "main") {
    dashboard.innerHTML = defaultDashboardContent;
    initDashboard(); // Re-run API calls and chart initialization
    return;
  }
  fetch(page)
    .then(response => {
      if (!response.ok) throw new Error("Network response was not ok");
      return response.text();
    })
    .then(html => {
      dashboard.innerHTML = html;
      initDashboard(); // Initialize the content on the newly loaded page
    })
    .catch(error => {
      console.error("Error loading page:", error);
      dashboard.innerHTML = "<p>Error loading page.</p>";
    });
}


// Fetch Data from Server

function fetchData(endpoint, elementId, formatter = JSON.stringify) {
  if (cachedData[endpoint]) {
    document.getElementById(elementId).innerHTML = formatter(cachedData[endpoint]);
    if (elementId === "ebay-listings") focusOnEnter();
    return;
  }
  fetch(`http://localhost:5000/api/${endpoint}`)
    .then(response => response.json())
    .then(data => {
      cachedData[endpoint] = data;
      document.getElementById(elementId).innerHTML = formatter(data);
      if (elementId === "ebay-listings") focusOnEnter();
    })    
    .catch(error => console.error(`Error fetching ${endpoint}:`, error));
}



// Count Up Money

function countUp() {
  const salesElement = document.querySelector(".card-title .green");
  if (salesElement) {
    animateCount(salesElement, "£");
  }
}
function animateCount(element, prefix) {
  const targetValue = parseInt(element.innerText.replace(/[^0-9]/g, ""), 10);
  let currentValue = 0;
  const duration = 2000; // Animation time in ms
  const increment = targetValue / (duration / 16); // Increment per frame
  const counter = setInterval(() => {
    currentValue += increment;
    if (currentValue >= targetValue) {
      currentValue = targetValue;
      clearInterval(counter);
    }
    element.innerText = `${prefix}${Math.floor(currentValue).toLocaleString()}`;
  }, 16);
}

// Focus URL Input on Hover
function focusOnEnter() {
  document.querySelectorAll(".listing-item").forEach(item => {
    const input = item.querySelector(".url-input");
    const hasMovingSibling = item.querySelector('.moving-input') !== null;
    item.addEventListener("mouseenter", () => {
      if (hasMovingSibling) {
        setTimeout(() => input.focus({ preventScroll: true }), 280);
      } else {
        setTimeout(() => input.focus({ preventScroll: true }), 36);
      }
    });
    item.addEventListener("mouseleave", () => input.blur());
  });
}


// Format eBay Listings

function formatEbayListings(listings) {
  let html = '<div class="card"><div class="listings">';

  listings.forEach(listing => {
    html += `
      <div class="listing-item" data-title="${listing.title}">
        <a href="${listing.item_url}" class="img-and-title" target="_blank">
          <img src="${listing.image_url}" alt="Product">
          <p>${listing.title}</p>
          <span class="price">£${listing.price}</span>
        </a>
        <div class="link-wrapper">
          <div class="auto-link">Auto-link <i class="fas fa-external-link-alt"></i></div>
          <input class="url-input" type="text" placeholder="https://www.aliexpress.com/item/...">
        </div>
      </div>
    `;
  });

  html += '</div></div>';
  return html;
}


// Auto link

function autoLinkSearch() {
  document.addEventListener("click", e => {
    const autoLink = e.target.closest(".auto-link");
    if (!autoLink) return;
    const listingItem = autoLink.closest(".listing-item");
    const title = listingItem.getAttribute("data-title");
    fetch("http://localhost:5000/api/search-web", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title })
    })
    .then(response => response.json())
    .then(data => console.log("Result:", data))
    .catch(err => console.error("Error:", err));
  });
  
}
