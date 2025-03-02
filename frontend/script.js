
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

  // Link URL Box
  document.querySelectorAll('.listing-item input[type="text"]').forEach(input => {
    input.addEventListener('mouseenter', () => input.focus());
  });

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
    return;
  }
  fetch(`http://localhost:5000/api/${endpoint}`)
    .then(response => response.json())
    .then(data => {
      cachedData[endpoint] = data;
      document.getElementById(elementId).innerHTML = formatter(data);
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


// Format eBay Listings

function formatEbayListings(listings) {
  let html = '<div class="card"><div class="listings">';

  listings.forEach(listing => {
    const hasVariations = listing.variations && listing.variations.length;
    
    // Show either the listing's main price or the first variation's price
    const firstVar = hasVariations ? listing.variations[0] : null;
    const displayPrice = hasVariations ? firstVar.price : listing.price;
    const displaySpecifics = hasVariations
      ? `${firstVar.variation_specifics.Name}: ${firstVar.variation_specifics.Value}`
      : "";

    html += `
      <div class="listing-item" data-variations='${hasVariations ? JSON.stringify(listing.variations) : "[]"}'>
        <div class="img-and-title">
          <img src="${listing.image_url}" alt="Product">
          <p>${listing.title}</p>
          </div>
        <span class="price">
          <span class="current-price">£${displayPrice}</span>
        </span>
        ${
          hasVariations
            ? `<select class="variation-dropdown">
                  ${listing.variations
                    .map((variation, idx) => `
                      <option value="${idx}">
                        ${variation.variation_specifics.Value} - £${variation.price}
                      </option>
                    `)
                    .join("")}
                </select>`
            : ""
        }
      </div>
    `;
  });

  html += '</div></div>';
  return html;
}  