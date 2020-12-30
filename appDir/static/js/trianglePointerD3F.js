export function drawTrianglePointerD3(pointerColor, side, id) {
    var svgWidth = 24;
    var svgHeight = svgWidth;
    if (side === "up") {
        var tianglePointerVertices = "1,18 9,8 17,18";
    }
    else {
        var tianglePointerVertices = "17,8 9,18 1,8";
    }


    //Adding svg element
    document.getElementById(id).innerHTML = "";
    var svg = d3.select("#" + id)
        .append("svg")
        .attr("width", svgWidth)
        .attr("height", svgHeight);

    var g1 = svg.append("g");

    g1.append("polygon")
        .attr("fill", pointerColor)
        .attr("points", tianglePointerVertices)
}