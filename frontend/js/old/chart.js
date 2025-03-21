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