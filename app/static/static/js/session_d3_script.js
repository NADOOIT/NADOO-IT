// Sample data
let data = [1, 2, 3, 4, 5];

// Create SVG container
let svg = d3.select("body")
    .append("svg")
    .attr("width", 500)
    .attr("height", 500);

// Create bars
svg.selectAll("rect")
    .data(data)
    .enter()
    .append("rect")
    .attr("x", (d, i) => i * 50)
    .attr("y", d => 500 - d * 50)
    .attr("width", 50)
    .attr("height", d => d * 50);
