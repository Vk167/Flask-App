$(document).ready(function(){

window.onload = function() {
    var graphContainer = document.querySelector('.run_chart');
    var graph = graphContainer.querySelector('.js-plotly-plot');

    var windowHeight = window.innerHeight;
    var containerHeight = graphContainer.clientHeight;
    var offsetTop = graphContainer.offsetTop;

    // Calculate the available height for the graph
    var availableHeight = windowHeight - offsetTop;

    // Set the height of the graph
    graph.style.height = availableHeight + 'px';


//   Expanded Icon

    var chartCards = document.querySelectorAll(".run_chart");
    var expandIcons = document.querySelectorAll(".barchartIcon");
    var canvases = document.querySelectorAll(".js-plotly-plot");

    var myBarCharts = [];

      function createOrUpdateChart(index) {
        // Destroy the existing chart if it exists
        if (myBarCharts[index]) {
          myBarCharts[index].destroy();
        }

        // Create a new chart
        myBarCharts[index] = new Chart(canvases[index].getContext("2d"), {
          // Your chart configuration goes here
        });
      }

      // Add click event listener to all expand icons
      expandIcons.forEach(function (expandIcon, index) {
        expandIcon.addEventListener("click", function () {
          // Toggle between full size and normal size for the corresponding chart card
          chartCards[index].classList.toggle("expanded");

          // Redraw the chart after expanding/collapsing to adjust its size
          createOrUpdateChart(index);
        });
      });

};
    function setChartHeight() {
    var runChart = document.getElementById('run-chart'); // Replace 'run-chart' with the actual ID of your chart
     var bellChart = document.getElementById('bell-curve');
     var runChartTwo = document.getElementById('run-chart-two'); // Replace 'run-chart' with the actual ID of your chart
     var bellChartTwo = document.getElementById('bell-curve-two');
    var viewportHeight = window.innerHeight;
    var chartHeight = 0.6 * viewportHeight; // Set the height to 60% of the viewport height

    // Set the height of the chart
   runChart.style.height = chartHeight + 'px';
   bellChart.style.height = chartHeight + 'px';
   runChartTwo.style.height = chartHeight + 'px';
   bellChartTwo.style.height = chartHeight + 'px';

}

// Call the function when the page loads and when the window is resized
window.onload = setChartHeight;
window.onresize = setChartHeight;



// Add this JavaScript code to your Dash app in the HTML layout file or in an external JavaScript file

 const settingsIcon = $("#settings-icon");
  const body = $("body");
  const dashboardContent = document.getElementById("main-content");


  let isDarkMode = false;

  settingsIcon.on("click", function () {
    isDarkMode = !isDarkMode;
    alert("Toogle");
    if (isDarkMode) {
      body.css({
        "background-color": "black",
        color: "white",
        "border-color": "white",
      });

      dashboardContent.css({
        "background-color": "black",
        color: "white",
      });

      navModify.css({
        "background-color": "white",
        color: "black",
      });


    } else {
      body.css({
        "background-color": "white",
        color: "black",
        "border-color": "black",
      });

      dashboardContent.css({
        "background-color": "white",
        color: "black",
      });

      navModify.css({
        "background-color": "black",
        color: "white",
      });


    }
  });








})
