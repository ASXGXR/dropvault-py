document.addEventListener("DOMContentLoaded", function () {
  const ctx = document.getElementById('weeklySalesChart').getContext('2d');
  new Chart(ctx, {
      type: 'line',
      data: {
          labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
          datasets: [{
              label: 'Sales (£)',
              data: [120, 200, 150, 300, 250, 400, 500], // Replace with actual sales data
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
        aspectRatio: 3, // Adjust this to make the chart shorter (higher number = shorter)
        scales: {
            y: { beginAtZero: true }
        }
      }
  });
});