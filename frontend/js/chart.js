/**
 * Weekly Sales Chart
 */
async function initializeChart() {  
  const canvas = document.getElementById("weeklySalesChart");
  if (!canvas) return;

  let profitByDay = { "Mon": 0, "Tue": 0, "Wed": 0, "Thu": 0, "Fri": 0, "Sat": 0, "Sun": 0 };
  let totalProfit = 0, weeklyItems = 0, past7DaysItems = 0;

  const now = new Date();
  const startOfWeek = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate() - ((now.getUTCDay() + 6) % 7)));
  startOfWeek.setUTCHours(0, 0, 0, 0);

  const today = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate()));
  today.setUTCHours(23, 59, 59, 999);

  const oneWeekAgo = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate() - 7));
  oneWeekAgo.setUTCHours(0, 0, 0, 0);

  try {
      const res = await fetch("http://82.42.112.27:5000/api/shipped-orders");
      const salesData = await res.json();

      if (!Array.isArray(salesData) || salesData.length === 0) return;

      salesData.forEach(order => {
          const shipped = order.shipped || "01-01-1970 00:00:00";
          const ebay_price = parseFloat(order.ebay_price) || 0;
          const ali_price = parseFloat(order.ali_price) || 0;
          const quantity = parseInt(order.quantity) || 1;
          const profit = (ebay_price - ali_price).toFixed(2);

          const [datePart, timePart] = shipped.split(" ");
          const [day, month, year] = datePart.split("-");
          const [hours, minutes, seconds] = timePart ? timePart.split(":") : [0, 0, 0];
          const shippedDate = new Date(Date.UTC(year, month - 1, day, hours, minutes, seconds));

          if (isNaN(shippedDate.getTime())) return;

          totalProfit += parseFloat(profit);

          if (shippedDate >= oneWeekAgo && shippedDate <= today) past7DaysItems += quantity;
          if (shippedDate >= startOfWeek && shippedDate <= today) {
              const dayName = shippedDate.toLocaleDateString("en-GB", { weekday: "short" }).charAt(0).toUpperCase() + 
                              shippedDate.toLocaleDateString("en-GB", { weekday: "short" }).slice(1).toLowerCase();
              if (profitByDay[dayName] !== undefined) profitByDay[dayName] += parseFloat(profit);
              weeklyItems += quantity;
          }
      });

      document.getElementById("total-profit").textContent = `£${totalProfit.toFixed(2)}`;
      document.getElementById("weekly-items").textContent = `${past7DaysItems} items`;

      countUp();
  } catch (error) {
      console.error("Error fetching sales data:", error);
  }

  new Chart(canvas.getContext("2d"), {
      type: "line",
      data: { 
          labels: Object.keys(profitByDay), 
          datasets: [{ 
              label: "Profit (£)", 
              data: Object.values(profitByDay).map(val => val || 0), 
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