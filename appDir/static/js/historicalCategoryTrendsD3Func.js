export function drawHistoricalCategoryTrendsD3(gData) {
    var months = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ];

    //Set dimensions of svg
    var margin = { top: 20, right: 20, bottom: 50, left: 50 };
    var svgWidth = 500;
    var svgHeight = 300;
    var graphWidth = svgWidth - margin.left - margin.right;
    var graphHeight = svgHeight - margin.top - margin.bottom;

    //Create domains & ranges of x & y axes
    var xExtent = d3.extent(gData, function (d, i) {
        return i;
    });
    var xRange = xExtent[1] - xExtent[0];

    var xScale = d3
        .scaleLinear()
        .domain([xExtent[0], xExtent[1]])
        .range([0, graphWidth]);

    var yScale = d3
        .scaleLinear()
        .domain([
            d3.min(gData, function (d) {
                return Math.min(d.Amount) * 0.8;
            }),
            d3.max(gData, function (d) {
                return Math.max(d.Amount * 1.05);
            }),
        ])
        .range([graphHeight, 0]);

    //Defining line function for category historical data
    var catHistLine = d3
        .line()
        .x(function (d, i) {
            return xScale(i);
        })
        .y(function (d) {
            return yScale(d.Amount);
        })
        .curve(d3.curveMonotoneX);

    //Clearing the canvas
    document.getElementById("graphDiv2").innerHTML = "";

    //Creating SVG canvas
    var svg = d3
        .select("#graphDiv2")
        .append("svg")
        .attr("width", svgWidth)
        .attr("height", svgHeight)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    //Creating tooltip
    var ttip = d3
        .select("body")
        .append("div")
        .attr("class", "tooltip")
        .attr("id", "ttip2")
        .style("opacity", 0);
    //Adding x, y axes and their titles
    svg.append("g")
        .attr("class", "x-axis")
        .attr("transform", "translate(0," + graphHeight + ")")
        .call(
            d3
                .axisBottom()
                .scale(xScale)
                .ticks(gData.length)
                .tickFormat(function (d, i) {
                    if (i % 3 !== 0) {
                        return "";
                    } else {
                        return (
                            months[gData[i].Month - 1] +
                            "'" +
                            gData[i].Year.toString().slice(2)
                        );
                    }
                })
        )
        .style("font-size", "11px");

    svg.append("text")
        .attr("class", "x-axis-label")
        .attr("fill", "black")
        .attr("x", graphWidth / 2)
        .attr("y", graphHeight + 0.8 * margin.bottom)
        .style("text-anchor", "middle")
        .text("Month");

    svg.append("text")
        .attr("class", "y-axis-label")
        .attr("transform", "rotate(-90)")
        .attr("fill", "black")
        .attr("x", -graphHeight / 2)
        .attr("y", -margin.left + 10)
        .attr("dy", "1em")
        .style("text-anchor", "middle")
        .text("Amount (in ₹)");

    //Adding line plot for category historical trends
    svg.append("path")
        .style("stroke", "black")
        .style("fill", "none")
        .attr("class", "line")
        .style("stroke-dasharray", "3, 3")
        .attr("d", catHistLine(gData));

    //Function to add circles at data points
    function drawCircle(param, color) {
        svg.selectAll("dataCircle")
            .data(gData)
            .enter()
            .append("circle")
            .attr("class", function (d, i) {
                return "c2-" + i;
            })
            .attr("fill", color)
            .attr("r", 4)
            .attr("cx", function (d, i) {
                return xScale(i);
            })
            .attr("cy", function (d, i) {
                return yScale(d[param]);
            })
            .on("mouseover", function (d, i) {
                d3.selectAll(".c2-" + i)
                    .transition()
                    .duration("100")
                    .attr("r", 6);
                ttip.transition().duration("100").style("opacity", 1);
                ttip.html(function () {
                    return (
                        "Spent: ₹ " +
                        Math.trunc(d.Amount) +
                        " <br /># of txns: " +
                        d.Number +
                        " <br />" +
                        months[gData[i].Month - 1] +
                        "'" +
                        gData[i].Year.toString().slice(2)
                    );
                })
                    .style("left", d3.event.pageX + 10 + "px")
                    .style("top", d3.event.pageY - 15 + "px");
            })
            .on("mouseout", function (d, i) {
                d3.selectAll(".c2-" + i)
                    .transition()
                    .duration("200")
                    .attr("r", 4);
                ttip.transition().duration("200").style("opacity", 0);
            });
    }

    //Adding circles to data points
    drawCircle("Amount", "black");
}
