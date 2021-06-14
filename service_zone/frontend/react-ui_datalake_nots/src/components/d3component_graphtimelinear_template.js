import React, {useEffect, useRef, useState} from 'react';
import * as d3 from "d3";
import * as axios from "axios";







export default function D3Test(props){
    const d3Container = useRef(null);

    const width = 900
    const height = 300
    const marging = {top:10, left:30, right:10,bottom:20}
    console.log(width + marging.top)
    const svg_width = width + marging.left + marging.right
    const svg_height = height + marging.bottom + marging.top

    useEffect(()=>{
        async function get_data() {
            var data = await axios.get("http://localhost:5000/sensors_data").then(response => response.data)




            var values = []
            var values_list = []
            var date = []
            var size = 0
            for (var device in data){
                // console.log(device)
                for (var uri in data[device]){
                    // console.log(uri)
                    for (var sample in data[device][uri]){
                        // console.log(sample)
                        // console.log(data[device][uri][sample])
                        size = values.push(data[device][uri][sample])
                        values_list.push(data[device][uri][sample][0])
                        date.push(data[device][uri][sample][2])
                    }
                }
            }

            var date_extr = d3.extent(date)
            var date_deb = new Date(date_extr[0]*1000)
            var date_fin = new Date(date_extr[1]*1000)
            var val_extr = d3.extent(values_list)
            // var val_min = val_extr[0]
            // var val_max = val_extr[1]
            console.log(val_extr)
            const svg = d3.select(d3Container.current).attr("viewbox",[0, 0, width- (marging.right + marging.left), height-(marging.bottom + marging.top)]).attr("width",width).attr("height",height)

            var y_scale = d3.scaleLinear().domain(val_extr).nice().range([marging["top"],height-(marging.bottom + marging.top)])

            var y_axis = d3.axisRight().scale(y_scale).ticks(15).tickSize(width)

            var x_scale = d3.scaleTime().domain([date_deb,date_fin]).nice().range([marging["left"], width-marging["right"]])

            var x_axis = d3.axisBottom().scale(x_scale)

            // svg.selectAll("circle").data(y_scale.ticks())
            //     .join("line")
            //     .attr("x1",150)
            //     .attr("x2",250)
            //     .attr("y1",d=>y_scale(d))
            //     .attr("y2",d=>y_scale(d))
            //     .attr("stroke","black")

            svg.append("g")
                .attr("class","y_axis")
                .attr("stroke-opacity",0.5)
                .attr("stroke-dasharray","2,2")
                .attr("transform",`translate(${marging.left},${marging.top})`).call(y_axis)
            svg.append("g")
                .attr("transform", `translate(${marging.left},${height - marging.bottom})`)
                .attr("class","x_axis")
                .call(x_axis)
            svg.selectAll(".tick text")
                .attr("x", 4).attr("dy", -4);
            svg.selectAll(".y_axis .tick text").attr("transform",`translate(-25,10)`)
            svg.selectAll(".x_axis .tick text").attr("transform",`translate(0,10)`)
        }
        get_data()
    }, [])

    return <svg width={svg_width} height={svg_height}
                className="d3_test"

                ref={d3Container}
    />
}