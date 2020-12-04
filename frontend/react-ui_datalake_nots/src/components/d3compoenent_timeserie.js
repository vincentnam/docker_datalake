import React, {useEffect, useRef, useState} from 'react';
import * as d3 from "d3";
import * as axios from "axios";
import log from "d3-scale/src/log";






export default function D3TimeSerie(props){
    const d3Container = useRef(null);

    const width = 900
    const height = 300
    const marging = {top:10, left:30, right:10,bottom:20}
    console.log(width + marging.top)
    const svg_width = width + marging.left + marging.right
    const svg_height = height + marging.bottom + marging.top

    useEffect(()=>{
        /* implementation heavily influenced by http://bl.ocks.org/1166403 */
        async function get_data() {
            var data = await axios.get("http://localhost:5002/sensors_data").then(response => response.data)
            console.log(data)

            var values = []
            var values_list = []
            var date = []
            var size = 0

            // console.log(data)
            // for (var device in data) {
            //     // console.log(device)
            //     for (var uri in data[device]) {
            //         // console.log(uri)
            //         values.push({id:uri, values:[]})
            //         for (var sample in data[device][uri]) {
            //             values[0]["values"].append({
            //
            //                 value :data[device][uri][sample][0],
            //                 value_unit : data[device][uri][sample][1],
            //                 date: new Date(data[device][uri][sample][2])
            //
            //             })
            //             size = values.push(data[device][uri][sample])
            //             values_list.push(data[device][uri][sample][0])
            //             date.push(data[device][uri][sample][2])
            //
            //         }
            //     }
            // }
            //
            //             for (var device in data){
            //     // console.log(device)
            //     for (var uri in data[device]){
            //         // console.log(uri)
            //         for (var sample in data[device][uri]){
            //             // console.log(sample)
            //             // console.log(data[device][uri][sample])
            //             size = values.push(data[device][uri][sample])
            //             values_list.push(data[device][uri][sample][0])
            //             date.push(data[device][uri][sample][2])
            //         }
            //     }
            // }

            // var val_min = val_extr[0]
            // var data = [{val_min:50, val_max:51},{ date: 1514764887.237, value: 51, value_unit: "%r.H." },{ date: 1514778837.129, value: 50.1, value_unit: "%r.H." },{ date: 1514788837.129, value: 50, value_unit: "%r.H." }]
            var values = data[Object.keys(data)[0]].values
            // var date = [1514764887.237,1514788837.129]
            console.log(data)

            var date = [data[Object.keys(data)[0]].values[0].date , data[Object.keys(data)[0]].values[data[Object.keys(data)[0]].values.length-1].date ]

            var date_extr = d3.extent(date)

            // const first_key = Object.keys(data)[0]
            // var val_extr_dict = data[first_key]["values"].shift()
            var val_extr_dict = values.shift()
            console.log(val_extr_dict)
            var val_extr = [val_extr_dict.val_max, val_extr_dict.val_min]
            // console.log("coucou")
            // console.log(new Date(data[first_key]["values"][data[first_key]["values"].length - 1][2] * 1000))
            // var date_deb = new Date(data[first_key]["values"][0]["date"] * 1000)
            // var date_fin = new Date(data[first_key]["values"][data[first_key]["values"].length - 1]["date"] * 1000)
            var date_deb = new Date( (values[0].date)* 1000)
            var date_fin = new Date( (values[values.length -1 ].date) * 1000)
            console.log(date_fin, date_deb)
            // console.log(val_extr)
            console.log(values[values.length -1 ].date)
            // console.log(data)
            // var val_max = val_extr[1]
            // console.log(val_extr)
            // define dimensions of graph
            // create a simple data array that we'll plot with a line (this array represents only the Y values, X will just be the index location)

            var m = [0, 0, 0, 80]; // margins
            // var w = 1000 - m[1] - m[3]; // width
            // var h = 400 - m[0] - m[2]; // height
            // var data = [3, 6, 2, 7, 5, 2, 0, 3, 8, 9, 2, 5, 9, 3, 6, 3, 6, 2, 7, 5, 2, 1, 3, 8, 9, 2, 5, 9, 2, 7];

            // X scale will fit all values from data[] within pixels 0-w
            var x = d3.scaleLinear().domain([0, data.length]).range([0, width]);
            // Y scale will fit values from 0-10 within pixels h-0 (Note the inverted domain for the y-scale: bigger is up!)
            var y = d3.scaleLinear().domain([0, 10]).range([height, 0]);
            // automatically determining max range can work something like this
            // var y = d3.scale.linear().domain([0, d3.max(data)]).range([h, 0]);

            // create yAxis
            // var xAxis = d3.axisBottom().scale(x).tickSize(-h)
            var y_scale = d3.scaleLinear().domain(val_extr).nice().range([marging["top"], height - (marging.bottom + marging.top)])

            var y_axis = d3.axisRight().scale(y_scale).ticks().tickSize(width)

            var x_scale = d3.scaleTime().domain([date_deb, date_fin]).nice().range([marging["left"], width - marging["right"]])

            var x_axis = d3.axisBottom().scale(x_scale)
            // Add the x-axis.
            // create a line function that can convert data[] into x and y points
            var line = d3.line().curve(d3.curveCardinal)
                // assign the X function to plot our line as we wish
                .x(function (d, i) {
                    // verbose logging to show what's actually being done
                    // console.log('Plotting X value for data point: ' + new Date(d.date*1000) + ' using index: ' + i + ' to be at: ' + x_scale( new Date(d.date*1000)) + ' using our xScale.');
                    // return the X coordinate where we want to plot this datapoint
                    return x_scale(new Date(d.date *1000));
                })
                .y(function (d) {
                    // verbose logging to show what's actually being done
                    // console.log('Plotting Y value for data point: ' + d.value + ' to be at: ' + y_scale(d.value) + " using our yScale.");
                    // return the Y coordinate where we want to plot this datapoint
                    return y_scale(d.value);
                })
            const svg = d3.select(d3Container.current).append("svg")
                // Add an SVG element with the desired dimensions and margin.
                .attr("width", width + m[1] + m[3])
                .attr("height", height + m[0] + m[2])
                .append("svg:g")
                .attr("transform", "translate(" + m[3] + "," + m[0] + ")");



            svg.append("svg:g")
                .attr("transform", `translate(0,${height - marging.bottom})`)
                .attr("class", "x_axis")
                .call(x_axis);


            // create left yAxis
            // var yAxisLeft = d3.axisLeft().scale(y).ticks(4)
            // Add the y-axis to the left
            svg.append("svg:g")
                .attr("class", "y_axis")
                .attr("stroke-opacity", 0.5)
                .attr("stroke-dasharray", "2,2")
                // .attr("transform", `translate(${marging.left},${marging.top})`)
                .call(y_axis)
            svg.selectAll(".y_axis .tick text").attr("transform", `translate(-25,10)`)
            svg.selectAll(".x_axis .tick text").attr("transform", `translate(0,10)`)

            svg.selectAll(".tick text")
                .attr("x", 4).attr("dy", -4);

            // Add the line by appending an svg:path element with the data line we created above
            // do this AFTER the axes above so that the line is above the tick-lines
            svg.selectAll("circle").data(values).join("circle").attr("r",1).attr("cx",);
            svg.append("svg:path").attr("d", line(values)).attr("fill","none").attr("stroke","pink");
        }
        // get_data()
    }, [])

    return <svg width={svg_width} height={svg_height}
                className="d3_test"

                ref={d3Container}
    />
}
