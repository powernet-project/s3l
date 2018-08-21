function ts_zoomable_demo() {
    data = [10, 40, 35, 50, 75, 80, 70, 75, 90, 60, 70, 100];
    ts_zoomable_init("#viz", data);
}

function ts_zoomable_init(div, data) {

dimensions = [],
h = 300,
w = 600, 
chartH = 250,
chartW = 550,
chartX = 50,
chartY = 50;

/******************************** 
* Data
*********************************/
dimensions[0] = {"name": "year", "len": 12};
dimensions[1] = {"name": "quarter", "len": 3};
dimensions[2] = {"name": "month", "len": 1};

/******************************** 
* Icicle selector
*********************************/
var rootSVG = d3.select(div)
    .append("svg:svg")
    .attr("width", w)
    .attr("height", h);
    
rootSVG.selectAll("g.level")
    .data(dimensions)
    .enter().append("svg:g")
    .attr("class", "level")
    
    .each(function(parentD, parentI){
        d3.select(this)
            .selectAll("rect.member")
            .data(function(d, i){return d3.range(data.length/d.len)})
            .enter().append("svg:rect")
            .attr("class", "member")
            .attr("width", function(){return ~~(parentD.len/data.length*chartW)})
            .attr("height", function(){return~~(chartH/dimensions.length)})
            .attr("x", function(d, i){return ~~(i*parentD.len/data.length*chartW)+chartX})
            .attr("y", ~~(parentI*chartH/dimensions.length))
            .attr("fill", "white")
            .attr("stroke", "#eee")
           .on("mouseover", myMouseOver(div)) 
           .on("mouseout", function(d, i){
                d3.selectAll("rect.zone")
                    .remove();
            })
            .on("mousedown", function(d, i){
                rescale(i, i+dimensions[parentI].len);
            });
    });


/******************************** 
* Chart
*********************************/
var y = d3.scale.linear().domain([0, d3.max(data)+10]).range([chartH, 0]);
var x = d3.scale.linear().domain([0, data.length]).range([chartX+15, chartW+chartX+15]);
var yAxis = d3.svg.axis().scale(y).ticks(3).orient("left"); 
var xAxis = d3.svg.axis().scale(x);
    
var chart = rootSVG.append("svg:g")
    .attr("pointer-events", "none")
    .attr("clip-path", "url(#clip)");

chart.append("svg:rect")
    .attr("width", chartW)
    .attr("height", chartH)
    .attr("x", chartX)
    .attr("stroke", "black")
    .attr("stroke-width", "1")
    .attr("fill", "none");

chart.selectAll("circle.dot")
    .data(data)
    .enter().append("svg:circle")
    .attr("class", "dot")
    .attr("cx", function(d, i){return x(i)})
    .attr("cy", y)
    .attr("r", 3);

var line = d3.svg.line()
    .interpolate("monotone")
    .x(function(d, i) { return x(i); })
    .y(function(d, i) { return y(d); });
    
chart.append("svg:path")
    .attr("class", "line")
    .attr("d", line(data))
    .attr("fill", "none")
    .attr("stroke", "black");

rootSVG.append("svg:clipPath")
    .attr("id", "clip")
    .append("svg:rect")
    .attr("width", chartW)
    .attr("height", chartH)
    .attr("x", chartX);

rootSVG.append("svg:g")
    .attr("class", "x axis")
    .attr("transform", "translate(0," + chartH + ")")
    .call(xAxis);

rootSVG.append("svg:g")
      .attr("class", "y axis")
      .attr("transform", "translate(" + chartX + ",0)")
      .call(yAxis);

rootSVG.append("svg:text")
      .attr("x", w/2)
      .attr("y", h - 6)
      .attr("text-anchor", "start")
      .text("Time");

rootSVG.append("svg:text")
      .attr("x", 50)
      .attr("y", h/2)
      .attr("text-anchor", "start")
      .text("Value");

function rescale(start, end) {
    x.domain([start, end]);
    var t = rootSVG.transition().duration(500);
    t.select(".x.axis").call(xAxis);
    t.select(".line").attr("d", line(data));
    chart.selectAll("circle.dot")
        .transition().duration(500)
        .attr("cx", function(d, i){return x(i)});
}

function myMouseOver(div) {
  return function(d, i) {
    var thisRect = d3.select(this);
    d3.select(div).select("svg")
	.append("svg:rect")
        .attr("class", "zone")
        .attr("fill", "dodgerblue")
        .attr("x", thisRect.attr("x"))
        .attr("y", 0)
        .attr("width", thisRect.attr("width"))
        .attr("height", chartH)
        .attr("opacity", 0.3)
        .attr("pointer-events", "none");
  }
}

}
