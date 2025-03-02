
// DOM Fully Loaded


document.addEventListener("DOMContentLoaded", function () {
    const dashboard = document.getElementById("dashboard");
    defaultDashboardContent = dashboard.innerHTML; // Save original content
    initDashboard(); // Load scripts
    countUp(); // Count Up Money
});


// On New Page Load

function initDashboard() {

    const ordersEl = document.getElementById("orders");
    if (ordersEl) {
      fetch("http://localhost:5000/api/orders")
        .then(response => response.json())
        .then(data => {
          ordersEl.innerText = JSON.stringify(data, null, 2);
        })
        .catch(error => console.error("Error fetching orders:", error));
    }
  
    const ebayEl = document.getElementById("ebay-listings");
    if (ebayEl) {
      fetch("http://localhost:5000/api/ebay-listings")
        .then(response => response.json())
        .then(data => {
          ebayEl.innerHTML = formatEbayListings(data);
        })
        .catch(error => console.error("Error fetching eBay listings:", error));
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



// (NAV) Changing the page content

function openPage(page) {
    const dashboard = document.getElementById("dashboard");
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


function countUp() {
    // Count Up
    const salesElement = document.querySelector(".card-title .green");
    if (salesElement) {
        const targetValue = parseInt(salesElement.innerText.replace(/[^0-9]/g, ""), 10); 
        let currentValue = 0;
        const duration = 2000; // Animation time in ms
        const increment = targetValue / (duration / 16); // Increment per frame
    
        const counter = setInterval(() => {
        currentValue += increment;
        if (currentValue >= targetValue) {
            currentValue = targetValue;
            clearInterval(counter);
        }
        salesElement.innerText = `£${Math.floor(currentValue).toLocaleString()}`;
        }, 16);
    }
}


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
          <div class="gap16">
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