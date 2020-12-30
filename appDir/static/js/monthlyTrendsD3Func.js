export function drawMonthlyTrendsD3(gData) {
    //Set dimensions of svg
    var margin1 = { top: 20, right: 20, bottom: 50, left: 50 };
    var svgWidth1 = 500;
    var el = d3.select('#graphDiv1')['_groups'][0][0];
    var svgWidth1 = el.offsetWidth;
    var svgHeight1 = 300;
    var graphWidth1 = svgWidth1 - margin1.left - margin1.right;
    var graphHeight1 = svgHeight1 - margin1.top - margin1.bottom;

    //Create domains & ranges of x & y axes
    var xExtent1 = d3.extent(gData, function (d, i) {
        return i;
    });
    var xRange1 = xExtent1[1] - xExtent1[0];

    var xScale1 = d3.scaleLinear()
                    .domain([xExtent1[0] - xRange1*0.05, xExtent1[1] + xRange1*0.05])
                    .range([0, graphWidth1]);

    var yScale1 = d3.scaleLinear()
        .domain([
            d3.min(gData, function (d) {
                return Math.min(d.Amount) * 0.8;
            }),
            d3.max(gData, function (d) {
                return Math.max(d.Amount * 1.05);
            }),
        ])
        .range([graphHeight1, 0]);

    //Clearing the canvas
    document.getElementById("graphDiv1").innerHTML = "";

    //Creating SVG canvas
    var svg1 = d3.select("#graphDiv1")
                .append("svg")
                .attr("width", svgWidth1)
                .attr("height", svgHeight1);

    var g1 = svg1.append("g")
                .attr(
                    "transform",
                    "translate(" + margin1.left + "," + margin1.top + ")"
                );

    //Creating tooltip
    var ttip1 = d3
        .select("body")
        .append("div")
        .attr("class", "tooltip")
        .attr("id", "ttip1")
        .style("opacity", 0);

    //Adding x, y axes and their titles
    console.log(gData.length)
    g1.append("g")
        .attr("class", "x-axis")
        .attr("transform", "translate(0," + graphHeight1 + ")")
        .call(
            d3.axisBottom()
                .scale(xScale1)
                .tickValues(d3.range(0, gData.length, 1))
                .tickFormat(function (d, i) {
                    return gData[i].Name;
                })
        )
        .style("font-size", "12px");

    g1.append("text")
        .attr("class", "x-axis-label")
        .attr("fill", "black")
        .attr("x", graphWidth1 / 2)
        .attr("y", graphHeight1 + 0.9 * margin1.bottom)
        .style("text-anchor", "middle")
        .text("Category");

    g1.append("text")
        .attr("class", "y-axis-label")
        .attr("transform", "rotate(-90)")
        .attr("fill", "black")
        .attr("x", -graphHeight1 / 2)
        .attr("y", -margin1.left + 10)
        .attr("dy", "1em")
        .style("text-anchor", "middle")
        .text("Amount (in ₹)");

    //Creating images as xticks
    g1.select(".x-axis").selectAll("text").remove();
    g1.select(".y-axis").selectAll("text").remove();

    g1.select(".x-axis")
        .selectAll(".tick")
        .data(gData)
        .append("svg:image")
        .attr("class", function (d, i) {
            return "svg1XTickIm-" + i;
        })
        .attr("xlink:href", function (d, i) {
            return "/static/icons/" + d.Name + ".svg";
        })
        .attr("width", 20)
        .attr("height", 25)
        .attr("x", -10)
        .attr("y", 5);

    //Creating bars
    var barWidth1 = 15;
    g1.selectAll("bar")
        .data(gData)
        .enter()
        .append("rect")
        .attr("class", function (d, i) {
            return "svg1Bar-" + i;
        })
        .attr("fill", "#327FD7")
        .style("rx", "4px")
        .attr("x", function (d, i) {
            return xScale1(i) - barWidth1 * 0.5;
        })
        .attr("y", function (d, i) {
            return yScale1(d.Amount);
        })
        .attr("width", barWidth1.toString())
        .attr("height", function (d) {
            return graphHeight1 - yScale1(d.Amount);
        })
        .on("mouseover", function (d, i) {
            d3.selectAll(".svg1Bar-" + i)
                .transition()
                .duration("100")
                .attr("fill", "#1E9989");
            d3.selectAll(".svg1XTickIm-" + i)
                .transition()
                .duration("100")
                .attr("width", 24)
                .attr("height", 29)
                .attr("x", -12)
                .attr("y", 3);
            ttip1.transition().duration("100").style("opacity", 1);
            ttip1
                .html(function () {
                    return (
                        d.Name +
                        " <br />Spent: ₹ " +
                        Math.trunc(d.Amount) +
                        " <br /># of txns: " +
                        d.Number
                    );
                })
                .style("left", d3.event.pageX + 10 + "px")
                .style("top", d3.event.pageY - 15 + "px");
        })
        .on("mouseout", function (d, i) {
            d3.selectAll(".svg1Bar-" + i)
                .transition()
                .duration("200")
                .attr("fill", "#327FD7");
            d3.selectAll(".svg1XTickIm-" + i)
                .transition()
                .duration("100")
                .attr("width", 20)
                .attr("height", 25)
                .attr("x", -10)
                .attr("y", 5);
            ttip1.transition().duration("200").style("opacity", 0);
        });
}
