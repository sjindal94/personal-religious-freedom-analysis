let compute_boxplot = function (data, iqr_k, value) {
    iqr_k = iqr_k || 1.5;
    value = value || Number;

    let seriev = data.map(functorkey(value)).sort(d3.ascending);

    let quartiles = [
        d3.quantile(seriev, 0.25),
        d3.quantile(seriev, 0.5),
        d3.quantile(seriev, 0.75)
    ];

    let iqr = (quartiles[2] - quartiles[0]) * iqr_k;

    //group by outlier or not
    let max = Number.MIN_VALUE;
    let min = Number.MAX_VALUE;
    let box_data = d3.nest()
        .key(function (d) {
            d = functorkey(value)(d);
            let type = (d < quartiles[0] - iqr || d > quartiles[2] + iqr) ? 'outlier' : 'normal';
            if (type === 'normal' && (d < min || d > max)) {
                max = Math.max(max, d);
                min = Math.min(min, d);
            }
            return type
        })
        .map(data);

    if (!box_data.outlier)
        box_data.outlier = [];
    box_data.quartiles = quartiles;
    box_data.iqr = iqr;
    box_data.max = max;
    box_data.min = min;


    return box_data
};

function constant(x) {
    return function () {
        return x;
    };
}

let exploding_boxplot = function (data, aes, width, height, margin) {
    //defaults
    let iqr = 1.5;
    let boxpadding = 0.2;
    let rotateXLabels = false;

    aes.color = aes.color || aes.group;
    aes.radius = aes.radius || constant(3);
    aes.label = aes.label || constant('aes.label undefined');

    let ylab = typeof aes.y === "string" ? aes.y : "";
    let xlab = typeof aes.group === "string" ? aes.group : "";

    let yscale = d3.scaleLinear()
        .domain([-10, 25])
        .nice()
        .range([height - margin.top - margin.bottom, 0]);


    let groups;
    if (aes.group) {
        groups = d3.nest()
            .key(functorkey(aes.group))
            .entries(data)
    } else {
        groups = [{key: '', values: data}]
    }


    let xscale = d3.scaleBand()
        .domain(groups.map(function (d) {
            return d.key
        }))
        .range([0, width - margin.left - margin.right], boxpadding)
        .padding(0.2);


    let colorscale = d3.scaleOrdinal()
        .domain(d3.set(data.map(functorkey(aes.color))).values())
        .range(d3.set(data.map(functorkey(aes.color))).values());

    //create boxplot data
    groups = groups.map(function (g) {
        let o = compute_boxplot(g.values, iqr, aes.y);
        o['group'] = g.key;
        return o
    });


    let tickFormat = function (n) {
        return n.toLocaleString()
    };

    //default tool tip function
    let _tipFunction = function (d) {
        return ' <span style="color: whitesmoke">' +
            functorkey(aes.label)(d) + '</span><span style="color:#DDDDDD;" > ' + '</span>';
    };


    let svg, container, tip;
    let chart = function (elem) {
        svg = d3.select(elem).append('svg')
            .attr('width', width)
            .attr('height', height);

        svg.append('g').append('rect')
            .attr('width', width)
            .attr('height', height)
            .style('color', 'white')
            .style('opacity', 0)
            .on('dblclick', implode_boxplot);

        svg.append("text")
            .attr("transform", "translate(400,0)")
            .attr("x", -150)
            .attr("y", 20)
            .attr("font-size", "16px")
            .text(`Growth % across religions`);


        container = svg.append('g')
            .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');


        let xAxis = d3.axisBottom(xscale);
        let yAxis = d3.axisLeft(yscale).tickFormat(tickFormat);


        let xaxisG = container.append('g')
            .attr('class', 'd3-exploding-boxplot x axis')
            .attr("transform", "translate(0," + (height - margin.top - margin.bottom) + ")")
            .call(xAxis);

        if (rotateXLabels) {
            xaxisG.selectAll('text')
                .attr("transform", "rotate(90)")
                .attr("dy", ".35em")
                .attr("x", "9").attr("y", "0")
                .style("text-anchor", "start");
        }

        // xaxisG.append("text")
        //     .attr("x", (width - margin.left - margin.right) / 2)
        //     .attr("dy", ".71em")
        //     .attr('y', margin.bottom - 14)
        //     .style("text-anchor", "middle")
        //     .text(xlab);

        container.append('g')
            .call(yAxis)
            .append("text")
            .attr("x", -margin.top - d3.mean(yscale.range()))
            .attr("dy", ".71em")
            .attr('y', 0)
            .style("background", "black")
            .style("font-size", "12px")
            .style("text-anchor", "middle")
            .text("growth");

        container = container.insert('g', '.axis');

        draw()
    };
    let create_jitter = function (g, i) {
        d3.select(this).append('g')
            .attr('class', 'd3-exploding-boxplot outliers-points')
            .selectAll('.point')
            .data(g.outlier)
            .enter()
            .append('circle')
            .call(init_jitter)
            .call(draw_jitter);
        d3.select(this).append('g')
            .attr('class', 'd3-exploding-boxplot normal-points')
    };

    let init_jitter = function (s) {
        s.attr('class', 'd3-exploding-boxplot point')
            .attr('r', functorkey(aes.radius))
            .attr('fill', function (d) {
                return colorscale(functorkey(aes.color)(d))
            })
            .call(function (s) {
                if (!s.empty())
                    tip(s)
            })
            .on('mouseover', tip.show)
            .on('mouseout', tip.hide)
    };
    let draw_jitter = function (s) {
        s.attr('cx', function (d) {
            let w = xscale.bandwidth();
            return Math.floor(Math.random() * w)
        })
            .attr('cy', function (d) {
                return yscale((functorkey(aes.y))(d))
            })
    };

    let create_boxplot = function (g, i) {
        let s = d3.select(this).append('g')
            .attr('class', 'd3-exploding-boxplot box')
            .on('click', function (d) {
                explode_boxplot(this.parentNode, g)
            })
            .selectAll('.box')
            .data([g])
            .enter();
        //box
        s.append('rect')
            .attr('class', 'd3-exploding-boxplot box')
            .attr('fill', function (d) {
                return colorscale(functorkey(aes.color)(d['$normal'][0]))
            });
        //median line
        s.append('line').attr('class', 'd3-exploding-boxplot median line');
        //min line
        s.append('line').attr('class', 'd3-exploding-boxplot min line hline');
        //min vline
        s.append('line').attr('class', 'd3-exploding-boxplot line min vline');
        //max line
        s.append('line').attr('class', 'd3-exploding-boxplot max line hline');
        //max vline
        s.append('line').attr('class', 'd3-exploding-boxplot line max vline')
    };
    let draw_boxplot = function (s) {
        //box
        s.select('rect.box')
            .attr('x', 0)
            .attr('width', xscale.bandwidth())
            .attr('y', function (d) {
                return yscale(d.quartiles[2])
            })
            .attr('height', function (d) {
                return yscale(d.quartiles[0]) - yscale(d.quartiles[2])
            });
        //median line
        s.select('line.median')
            .attr('x1', 0).attr('x2', xscale.bandwidth())
            .attr('y1', function (d) {
                return yscale(d.quartiles[1])
            })
            .attr('y2', function (d) {
                return yscale(d.quartiles[1])
            });
        //min line
        s.select('line.min.hline')
            .attr('x1', xscale.bandwidth() * 0.25)
            .attr('x2', xscale.bandwidth() * 0.75)
            .attr('y1', function (d) {
                return yscale(Math.min(d.min, d.quartiles[0]))
            })
            .attr('y2', function (d) {
                return yscale(Math.min(d.min, d.quartiles[0]))
            });
        //min vline
        s.select('line.min.vline')
            .attr('x1', xscale.bandwidth() * 0.5)
            .attr('x2', xscale.bandwidth() * 0.5)
            .attr('y1', function (d) {
                return yscale(Math.min(d.min, d.quartiles[0]))
            })
            .attr('y2', function (d) {
                return yscale(d.quartiles[0])
            });
        //max line
        s.select('line.max.hline')
            .attr('x1', xscale.bandwidth() * 0.25)
            .attr('x2', xscale.bandwidth() * 0.75)
            .attr('y1', function (d) {
                return yscale(Math.max(d.max, d.quartiles[2]))
            })
            .attr('y2', function (d) {
                return yscale(Math.max(d.max, d.quartiles[2]))
            });
        //max vline
        s.select('line.max.vline')
            .attr('x1', xscale.bandwidth() * 0.5)
            .attr('x2', xscale.bandwidth() * 0.5)
            .attr('y1', function (d) {
                return yscale(d.quartiles[2])
            })
            .attr('y2', function (d) {
                return yscale(Math.max(d.max, d.quartiles[2]))
            })
    };
    let hide_boxplot = function (g, i) {
        g.select('rect.box')
            .attr('x', xscale.bandwidth() * 0.5)
            .attr('width', 0)
            .attr('y', function (d) {
                return yscale(d.quartiles[1])
            })
            .attr('height', 0);
        //median line
        g.selectAll('line')
            .attr('x1', xscale.bandwidth() * 0.5)
            .attr('x2', xscale.bandwidth() * 0.5)
            .attr('y1', function (d) {
                return yscale(d.quartiles[1])
            })
            .attr('y2', function (d) {
                return yscale(d.quartiles[1])
            })
    };
    let explode_boxplot = function (elem, g) {
        d3.select(elem).select('g.box').transition()
            .ease(d3.easeBackIn)
            .duration(300)
            .call(g => hide_boxplot(g));

        d3.select(elem)
            .selectAll('.normal-points')
            .selectAll('.point')
            .data(g['$normal'])
            .enter()
            .append('circle')
            .attr('cx', xscale.bandwidth() * 0.5)
            .attr('cy', yscale(g.quartiles[1]))
            .call(init_jitter)
            .transition()
            .ease(d3.easeBackOut)
            .delay(function () {
                return 300 + 100 * Math.random()
            })
            .duration(function () {
                return 300 + 300 * Math.random()
            })
            .call(draw_jitter)
    };
    let implode_boxplot = function (elem, g) {
        container.selectAll('.normal-points')
            .each(function (g) {
                d3.select(this)
                    .selectAll('circle')
                    .transition()
                    .ease(d3.easeBackOut)
                    .duration(function () {
                        return 300 + 300 * Math.random()
                    })
                    .attr('cx', xscale.bandwidth() * 0.5)
                    .attr('cy', yscale(g.quartiles[1]))
                    .remove()
            });


        container.selectAll('.boxcontent')
            .transition()
            .ease(d3.easeBackOut)
            .duration(300)
            .delay(200)
            .call(draw_boxplot)
    };
    let create_tip = function () {
        tip = d3.tip().attr('class', 'd3-exploding-boxplot tip')
            .direction('n')
            .html(_tipFunction);
        return tip
    };

    function draw() {
        tip = tip || create_tip();
        chart.tip = tip;
        let boxContent = container.selectAll('.boxcontent')
            .data(groups)
            .enter().append('g')
            .attr('class', 'd3-exploding-boxplot boxcontent')
            .attr('transform', function (d) {
                return 'translate(' + xscale(d.group) + ',0)'
            })
            .each(create_jitter)
            .each(create_boxplot)
            .call(draw_boxplot)

    }

    chart.iqr = function (_) {
        if (!arguments.length) return iqr;
        iqr = _;
        return chart;
    };

    chart.width = function (_) {
        if (!arguments.length) return width;
        width = _;
        xscale.rangeRoundBands([0, width - margin.left - margin.right], boxpadding).padding(0.2);
        return chart;
    };

    chart.height = function (_) {
        if (!arguments.length) return height;
        height = _;
        yscale.range([height - margin.top - margin.bottom, 0]);
        return chart;
    };

    chart.margin = function (_) {
        if (!arguments.length) return margin;
        margin = _;
        //update scales
        xscale.rangeRoundBands([0, width - margin.left - margin.right], boxpadding).padding(0.2);
        yscale.range([height - margin.top - margin.bottom, 0]);
        return chart;
    };

    chart.xlab = function (_) {
        if (!arguments.length) return xlab;
        xlab = _;
        return chart;
    };
    chart.ylab = function (_) {
        if (!arguments.length) return ylab;
        ylab = _;
        return chart;
    };
    chart.ylimit = function (_) {
        if (!arguments.length) return yscale.domain();
        yscale.domain(_.sort(d3.ascending));
        return chart
    };
    chart.yscale = function (_) {
        if (!arguments.length) return yscale;
        yscale = _;
        return chart
    };
    chart.xscale = function (_) {
        if (!arguments.length) return xscale;
        xscale = _;
        return chart
    };
    chart.tickFormat = function (_) {
        if (!arguments.length) return tickFormat;
        tickFormat = _;
        return chart
    };
    chart.colors = function (_) {
        if (!arguments.length) return colorscale.range();
        colorscale.range(_);
        return chart;
    };
    chart.rotateXLabels = function (_) {
        if (!arguments.length) return rotateXLabels;
        rotateXLabels = _;
        return chart;
    };


    return chart;

};

function functorkey(v) {
    return typeof v === "function" ? v : function (d) {
        return d[v];
    };
}


//i want arrows function...
function fk(v) {
    return function (d) {
        return d[v]
    };
}

exploding_boxplot.compute_boxplot = compute_boxplot;