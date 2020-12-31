export function drawMFTrendsD3(gData){
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
    var el = d3.select('#graphDiv2')['_groups'][0][0];
    var svgWidth = el.offsetWidth;
    var svgHeight = 300;
    var graphWidth = svgWidth - margin.left - margin.right;
    var graphHeight = svgHeight - margin.top - margin.bottom;

    //Create domains & ranges of x & y axes
    var xExtent = d3.extent(gData, function (d, i) {
        return i;
    });
    var xRange = xExtent[1] - xExtent[0];

    var xTickMap = gData.map(function(value){return new Date(value.Date)});
    var xTickMin = new Date(Math.min.apply(null, xTickMap))
    var xTickMax = new Date(Math.max.apply(null, xTickMap))
    //[xExtent[0] - xRange*0.05, xExtent[1] + xRange*0.05]
    var xScale = d3.scaleLinear()
                    .domain([xTickMin, xTickMax])
                    .range([0, graphWidth]);

    var yScale = d3.scaleLinear()
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
    var catHistLine = d3.line()
                        .x(function (d, i) {
                            return xScale(xTickMap[i]);
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
        .attr("class", "tooltip hide-unhide")
        .attr("id", "ttip3")
        .style("opacity", 0);
    
    var bisectDate = d3.bisector(function(d) { return new Date(d.Date); }).left;

    var focus = svg.append("g")
        .style("display", "none");
    
    //Adding x, y axes and their titles
    svg.append("g")
        .attr("class", "x-axis")
        .attr("transform", "translate(0," + graphHeight + ")")
        .call(
            d3.axisBottom()
                .scale(xScale)
                .tickFormat(function (d, i) {
                    var tickDate = new Date(d);
                    return months[(tickDate.getMonth() + 1)] + "'" + tickDate.getFullYear().toString().substring(2,4)})
        )
        .style("font-size", "11px");

    svg.append("text")
        .attr("class", "x-axis-label")
        .attr("fill", "black")
        .attr("x", graphWidth / 2)
        .attr("y", graphHeight + 0.8 * margin.bottom)
        .style("text-anchor", "middle")
        .text("Date");

    svg.append("text")
        .attr("class", "y-axis-label")
        .attr("transform", "rotate(-90)")
        .attr("fill", "black")
        .attr("x", -graphHeight / 2)
        .attr("y", -margin.left + 10)
        .attr("dy", "1em")
        .style("text-anchor", "middle")
        .text("Amount (in ₹)");
    
    //Adding line plot for mutual fund total investment data
    svg.append("path")
        .style("stroke", "black")
        .style("fill", "none")
        .attr("class", "line")
        .attr("d", catHistLine(gData));
    
    //Adding circle on the hover data point
    focus.append("circle") 
        .attr("class", "y")
        .style("fill", "green") 
        .style("stroke", "green")
        .attr("r", 4);
    
    //Set the area to capture the mouse movements
    svg.append("rect")
        .attr("width", graphWidth)
        .attr("height", graphHeight)
        .style("fill", "none")
        .style("pointer-events", "all")
        .on("mouseover", function() { focus.style("display", null); })
        .on("mouseout", function() { 
            focus.style("display", "none");
            ttip.transition().duration("100").style("opacity", 0);
        })
        .on("mousemove", mousemove);
    
    function mousemove() {
        var x0 = xScale.invert(d3.mouse(this)[0]),
            i = bisectDate(gData, x0, 1),
            d0 = gData[i - 1],
            d1 = gData[i],
            d = (x0 - new Date(d0.Date)) > (new Date(d1.Date) - x0) ? d1 : d0;
        
        focus.select("circle.y")
            .attr("transform", "translate(" + xScale(new Date(d.Date)) + "," + yScale(d.Amount) + ")");
        
        ttip.transition().duration("50").style("opacity", 1);
        let pos = d3.select(this).node().getBoundingClientRect();
        ttip.html(function () {
            var tickDate = new Date(d.Date);
            return tickDate.getDate() + ' ' + months[tickDate.getMonth()] + "'" + tickDate.getFullYear().toString().substring(2,4) + "<br /> Invested: ₹ " + parseInt(d.Amount) 
        })
            .style("left", window.pageXOffset + pos['x'] + xScale(new Date(d.Date)) + 10 + "px")
            .style("top", window.pageYOffset  + pos['y'] + yScale(d.Amount) - 15 + "px");
    }

}