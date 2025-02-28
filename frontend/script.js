
// Trigger Aliexpress Order
async function triggerAliOrder() {
  try {
      const response = await fetch("http://127.0.0.1:5000/trigger-script", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
              productUrl: "https://www.aliexpress.com/item/xyz",
              quantity: 2
          })
      });

      const data = await response.json();
      alert(data.message || data.error);
  } catch (error) {
      console.error("Error:", error);
  }
}



// DOM Fully Loaded

document.addEventListener("DOMContentLoaded", function () {


  // Weekly Profit Graph
  const ctx = document.getElementById('weeklySalesChart').getContext('2d');
  new Chart(ctx, {
      type: 'line',
      data: {
          labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
          datasets: [{
              label: 'Sales (£)',
              data: [12, 20, 15, 30, 25, 40, 50], // Replace with actual sales data
              borderColor: 'rgba(54, 162, 235, 1)',
              backgroundColor: 'rgba(54, 162, 235, 0.2)',
              borderWidth: 2,
              pointRadius: 4,
              pointBackgroundColor: 'rgba(54, 162, 235, 1)',
              fill: true // Set to false if you don't want the area under the line filled
          }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false, // Allows height adjustment
        aspectRatio: 2.9, // Adjust this to make the chart shorter (higher number = shorter)
        scales: {
            y: { beginAtZero: true }
        }
      }
  });


  // Link URL Box
  document.querySelectorAll('.listing-item input[type="text"]').forEach(input => {
    input.addEventListener('mouseenter', () => input.focus());
  });


  // Count Up
  const salesElement = document.querySelector(".card-title .green");
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

});