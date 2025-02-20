import React, { useEffect, useRef } from "react";
import * as d3 from "d3";

// Define the expected data structure
interface DataPoint {
    date: string; // ISO date string
    value: number;
}

interface TimeSeriesChartProps {
    data: DataPoint[];
    width?: number;
    height?: number;
}

const TimeSeriesChart: React.FC<TimeSeriesChartProps> = ({
    data,
    width = 800,
    height = 600,
}) => {
    const valuesToPredict: number = 5;
    const svgRef = useRef<SVGSVGElement>(null);

    useEffect(() => {
        if (!data || data.length === 0 || !svgRef.current) return;

        const margin = { top: 20, right: 30, bottom: 40, left: 70 };
        const innerWidth = width - margin.left - margin.right;
        const innerHeight = height - margin.top - margin.bottom;

        // Determine the last 30 data points
        const last30Index = Math.max(0, data.length - valuesToPredict);
        const normalData = data.slice(0, last30Index);
        const highlightedData = data.slice(last30Index);

        // Combine normalData and highlightedData
        const combinedData = [...normalData, ...highlightedData];

        // Console log the data
        console.log("Normal data:", normalData);
        console.log("Highlighted data:", highlightedData);
        console.log("Combined data:", combinedData);
        console.log("All data:", data);

        // Create scales
        const scales_x = d3.extent(data, d => new Date(d.date)) as [Date, Date];
        console.log("scales_x", scales_x);

        const xScale = d3
            .scaleTime()
            .domain(scales_x)
            .range([0, innerWidth]);

        const yScale = d3
            .scaleLinear()
            .domain([d3.min(data, d => d.value) ?? 0, d3.max(data, d => d.value) ?? 100])
            .nice()
            .range([innerHeight, 0]);

        // Line generator
        const lineGenerator = d3
            .line<DataPoint>()
            .x(d => xScale(new Date(d.date))!)
            .y(d => yScale(d.value)!)
            .curve(d3.curveLinear);

        // Select and clear SVG
        const svg = d3.select(svgRef.current);
        svg.selectAll("*").remove();

        // Append main group
        const g = svg
            .append("g")
            .attr("transform", `translate(${margin.left},${margin.top})`);

        // Gridlines
        const xAxisGrid = d3.axisBottom(xScale).tickSize(-innerHeight).tickFormat(() => "");
        const yAxisGrid = d3.axisLeft(yScale).tickSize(-innerWidth).tickFormat(() => "");

        g.append("g")
            .attr("class", "grid")
            .attr("transform", `translate(0,${innerHeight})`)
            .call(xAxisGrid)
            .selectAll("line")
            .attr("stroke", "#ddd"); // Light gray gridlines

        g.append("g")
            .attr("class", "grid")
            .call(yAxisGrid)
            .selectAll("line")
            .attr("stroke", "#ddd");

        // X Axis
        g.append("g")
            .attr("transform", `translate(0,${innerHeight})`)
            .call(d3.axisBottom(xScale).ticks(5))
            .selectAll("text")
            .attr("fill", "#333") // Dark text
            .style("font-size", "12px");

        // Y Axis
        g.append("g")
            .call(d3.axisLeft(yScale))
            .selectAll("text")
            .attr("fill", "#333") // Dark text
            .style("font-size", "12px");

        // X Axis label
        g.append("text")
            .attr("x", innerWidth / 2)
            .attr("y", innerHeight + margin.bottom - 10)
            .attr("fill", "#333")
            .attr("text-anchor", "middle")
            .style("font-size", "14px")
            .text("Time (weeks)");

        // Y Axis label
        g.append("text")
            .attr("transform", "rotate(-90)")
            .attr("x", -(innerHeight / 2))
            .attr("y", -margin.left + 15)
            .attr("fill", "#333")
            .attr("text-anchor", "middle")
            .style("font-size", "14px")
            .text("Prediction ($)");

        // Draw combined line
        if (combinedData.length > 0) {
            g.append("path")
                .datum(combinedData)
                .attr("fill", "none")
                .attr("stroke", "green")
                .attr("stroke-width", 2)
                .attr("d", lineGenerator);
        }

        // Draw highlighted line on top
        if (highlightedData.length > 0) {
            g.append("path")
                .datum(highlightedData)
                .attr("fill", "none")
                .attr("stroke", "red")
                .attr("stroke-width", 3)
                .attr("d", lineGenerator);
        }
    }, [data, width, height]);

    return <svg ref={svgRef} width={width} height={height}></svg>;
};

export default TimeSeriesChart;