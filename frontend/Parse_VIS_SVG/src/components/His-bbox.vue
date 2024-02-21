<template>
    <div ref="chartContainer"></div>
</template>

<script setup>
import { onMounted, ref, computed } from 'vue';
import * as d3 from 'd3';
import { useStore } from 'vuex';
const store = useStore();

const eleURL = "http://localhost:8000/bbox_num_data"
const chartContainer = ref(null);

const textThreshold = 12; // 设置文本显示的阈值

onMounted(async () => {
    if (!chartContainer.value) return;
    try {
        const response = await fetch(eleURL);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        // store.commit('GET_ELE_NUM_DATA', data);
        render(data)
    } catch (error) {
        console.error('There has been a problem with your fetch operation:', error);
    }
});

const render = (data) => {
    if (!chartContainer.value) return;

    const width = 245;
    const height = 190;
    const marginTop = 20;
    const marginRight = 10;
    const marginBottom = 40;
    const marginLeft = 30;

    const x = d3.scaleBand()
        .domain(data.map(d => d.point))
        .range([marginLeft, width - marginRight])
        .padding(0.1);

    const y = d3.scaleLinear()
        .domain([0, d3.max(data, d => d.count)]).nice()
        .range([height - marginBottom, marginTop]);

    const svg = d3.select(chartContainer.value)
        .append('svg')
        .attr('viewBox', `0 0 ${width} ${height}`)
        .attr('width', width)
        .attr('height', height)
        .attr('style', 'max-width: 100%; height: auto;');

    const zoom = (svg) => {
        const extent = [[marginLeft, marginTop], [width - marginRight, height - marginBottom]];
        svg.call(d3.zoom()
            .scaleExtent([1, 8])
            .translateExtent(extent)
            .extent(extent)
            .on('zoom', (event) => {
                x.range([marginLeft, width - marginRight].map(d => event.transform.applyX(d)));
                svg.selectAll('.bars')
                    .attr('d', d => roundedRectPath(d, x, y)); // 更新路径
                svg.selectAll('.bar-text')
                    .attr('x', d => x(d.point) + x.bandwidth() / 2)
                    .text(d => x.bandwidth() > textThreshold ? d.count : ''); // 更新文本显示状态
                svg.selectAll('.x-axis').call(d3.axisBottom(x))
                    .selectAll("text")
                    .text(d => x.bandwidth() > textThreshold ? d : ''); // 更新文本显示状态
            }));
    };

    svg.append('g')
        .selectAll('path')
        .data(data)
        .join('path')
        .attr('class', 'bars')
        .attr('fill', 'steelblue')
        .attr('d', d => roundedRectPath(d, x, y));

    svg.append('g')
        .attr('class', 'x-axis')
        .attr('transform', `translate(0,${height - marginBottom})`)
        .call(d3.axisBottom(x))
        .selectAll("text")
        .style("text-anchor", "end")
        .style("pointer-events", "none")
        .style("font-size", "10px")
        .attr("dx", "-.4em")
        .attr("dy", ".15em")
        .attr("transform", "rotate(-45)")
        .text(d => x.bandwidth() > textThreshold ? d : ''); // 根据条形的宽度决定是否显示文本

    svg.append('g')
        .attr('class', 'y-axis')
        .style("pointer-events", "none")
        .attr('transform', `translate(${marginLeft},0)`)
        .call(d3.axisLeft(y));

    svg.append('g')
        .selectAll('text')
        .data(data)
        .join('text')
        .attr('class', 'bar-text')
        .style("pointer-events", "none")
        .attr('x', d => x(d.point) + x.bandwidth() / 2) // 定位到条形的中心
        .style("font-size", "12px")
        .attr('y', d => y(d.count) - 5) // 在条形顶部稍微上方位置显示数值
        .attr('text-anchor', 'middle')
        .text(d => x.bandwidth() > textThreshold ? d.count : ''); // 根据条形的宽度决定是否显示文本

    zoom(svg);
};

const roundedRectPath = (d, x, y) => {
    const x0 = x(d.point);
    const y0 = y(d.count);
    const x1 = x0 + x.bandwidth();
    const y1 = y(0);
    const r = Math.min(x.bandwidth(), y(0) - y(d.count)) / 8; // Radius for the rounded corners

    return `M${x0},${y0 + r}
            Q${x0},${y0} ${x0 + r},${y0}
            L${x1 - r},${y0}
            Q${x1},${y0} ${x1},${y0 + r}
            L${x1},${y1}
            L${x0},${y1}
            Z`;
};
</script>

<style scoped></style>
