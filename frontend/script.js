
// DOM Fully Loaded

const cachedData = {};


document.addEventListener("DOMContentLoaded", function () {
    const dashboard = document.getElementById("dashboard");
    defaultDashboardContent = dashboard.innerHTML; // Save original content
    initDashboard(); // Loads scripts
    countUp(); // Counts Up Money
});


// On Page Load / Switch

function initDashboard() {

  // FETCH EBAY DATA
  // ebay Orders
  if (document.getElementById("orders")) {
    fetchData(endpoint="orders", elementId="orders", data => `<pre>${JSON.stringify(data, null, 2)}</pre>`);
  }
  // ebay Listings
  if (document.getElementById("ebay-listings")) {
    fetchData(endpoint="ebay-listings", elementId="ebay-listings", formatEbayListings);
  }

  // Initialises Chart
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

// Focus url-input on Hover
function focusOnEnter() {
  document.querySelectorAll(".listing-item").forEach(item => {
    const input = item.querySelector(".url-input");
    const linkWrapper = item.querySelector(".link-wrapper");
    const hasMovingSibling = item.querySelector('.moving-input') !== null;

    if (input) {
      let focusInput = !(item.classList.contains('linked') || linkWrapper?.classList.contains('linked'));
      if (focusInput) {
        item.addEventListener("mouseenter", () => {
          console.log(1);
          setTimeout(() => input.focus({ preventScroll: true }), hasMovingSibling ? 280 : 36);
        });
      }
    
      input.addEventListener("change", () => {
        const aliUrl = input.value.trim();
        const itemId = input.getAttribute("data-item-id");
        if (itemId && aliUrl.includes("https://www.aliexpress.com/item/") || aliUrl == '') {
          input.classList.add('linked');
          // Send to API (updates listings)
          fetch("http://localhost:5000/api/update-aliexpress", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ item_id: itemId, aliexpress_url: input.value })
          })
          .then(res => res.json())
          .then(data => console.log("Update response:", data))
          .catch(err => console.error(err));
        }
        if (input.value.trim() == '') {
          linkWrapper.classList.remove("linked");
        }
      });
    }
  });
}


// Format eBay Listings

function formatEbayListings(listings) {
  let html = '<div class="card"><div class="listings">';

  listings.forEach(listing => {
    const searchUrl = `https://www.aliexpress.com/wholesale?SearchText=${encodeURIComponent(listing.title)}`;
    const isLinked = listing.aliexpress_url ? ' linked' : '';
    const aliUrl = listing.aliexpress_url || '';
    html += `
      <div class="listing-item" data-title="${listing.title}" data-item-id="${listing.item_id}">
        <a href="${listing.item_url}" class="img-and-title" target="_blank">
          <img src="${listing.image_url}" alt="Product">
          <p>${listing.title}</p>
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
      </div>
    `;
  });

  html += '</div></div>';
  return html;
}