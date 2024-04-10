<template>
    <div ref="chartContainer" class="chart-container" :key="updateKey"></div>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import * as d3 from 'd3';

const eleURL = "http://127.0.0.1:8000/cluster_probabilities";
const chartContainer = ref(null);
const margin = { top: 10, right: 20, bottom: 60, left: 30 }; // 定义边距
const width = 1340 + margin.left + margin.right;
const height = 760 + margin.top + margin.bottom;

onMounted(async () => {
    if (!chartContainer.value) return;
    try {
        const response = await fetch(eleURL);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const rawData = await response.json();
        const data = processData(rawData);
        render(data);
    } catch (error) {
        console.error('There has been a problem with your fetch operation:', error);
    }
});

const processData = (rawData) => {
    let processedData = [];
    rawData.forEach((node, nodeIndex) => {
        node.probabilities.forEach((probability, groupIndex) => {
            processedData.push({
                node: node.id,
                group: groupIndex,
                probability: probability,
            });
        });
    });
    return processedData;
};

const render = (data) => {
    // 设置 SVG 容器
    const svg = d3.select(chartContainer.value)
        .append('svg')
        .attr('width', width)
        .attr('height', height)
        .append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);

    

    // 获取所有唯一的 id 后缀
    const ids = [...new Set(data.map(d => d.node.split('/').pop()))];
    const groups = d3.range(1, 51); // 竖轴的范围为 1 到 50

    // 创建比例尺
    const xScale = d3.scaleBand().domain(ids).range([0, width - margin.left - margin.right]).padding(0.05);
    const yScale = d3.scaleBand().domain(groups).range([height - margin.top - margin.bottom, 0]).padding(0.05);

    // 颜色比例尺
    const colorScale = d3.scaleSequential(d3.interpolateInferno)
        .domain([d3.max(data, d => d.probability), 0]);

    // 绘制方块
    svg.selectAll('.block')
        .data(data)
        .enter()
        .append('rect')
        .attr('x', d => xScale(d.node.split('/').pop()))
        .attr('y', d => yScale(d.group))
        .attr('width', xScale.bandwidth())
        .attr('height', yScale.bandwidth())
        .style('fill', d => colorScale(d.probability));

    // 添加坐标轴
    const xAxis = d3.axisBottom(xScale).tickSizeOuter(0);
    const yAxis = d3.axisLeft(yScale).tickSizeOuter(0);

    svg.append('g')
        .attr('class', 'x-axis') // 添加 class 名称
        .attr('transform', `translate(0,${height - margin.top - margin.bottom})`)
        .call(xAxis)
        .selectAll('text')
        .style('text-anchor', 'end')
        .attr('dx', '-1em')
        .attr('dy', '-0.5em')
        .attr('transform', 'rotate(-90)')
        .style('fill', 'black') // 明确设置文本颜色
        .style('font-size', '12px'); // 调整字体大小

    // 绘制 y 轴并调整样式
    svg.append('g').call(yAxis)
        .selectAll('text')
        .style('fill', 'black') // 明确设置文本颜色
        .style('font-size', '12px'); // 调整字体大小

    // 为坐标轴线条增加样式
    svg.selectAll('.domain')
        .style('stroke', 'black') // 设置轴线的颜色
        .style('stroke-width', '1px'); // 设置轴线的宽度

    svg.selectAll('.tick line')
        .style('stroke', 'black') // 设置刻度线的颜色
        .style('stroke-width', '1px'); // 设置刻度线的宽度



    const legendHeight = 730; // 图例的高度
    const legendWidth = 10; // 图例的宽度
    const numSwatches = 50; // 图例的颜色块数量
    const legendDomain = colorScale.domain();
    const legendScale = d3.scaleLinear()
        .domain([0, numSwatches - 1])
        .range([legendDomain[1], legendDomain[0]]); // 注意反转颜色域
    const legendData = Array.from(Array(numSwatches).keys());

    const legend = svg.append('g')
        .attr('transform', `translate(${width - 40}, 10)`); // 调整图例位置

    // 修改了这里，以确保颜色条是从高到低的概率值排列
    legend.selectAll('rect')
        .data(legendData)
        .enter()
        .append('rect')
        // 这里改变了计算 y 值的方法，确保颜色条按照概率值从高到低排列
        .attr('y', (d, i) => legendHeight - (i + 1) * (legendHeight / numSwatches))
        .attr('x', 0)
        .attr('height', legendHeight / numSwatches)
        .attr('width', legendWidth)
        .attr('fill', d => colorScale(legendScale(d)));

    // 旋转并调整图例文本标签的位置
    // 注意：最高概率值的文本应该位于图例的顶部，而最低概率值的文本应该位于底部
    legend.append('text')
        .attr('transform', `translate(${legendWidth + textYOffset}, 0) rotate(90)`)
        .style('font-size', '10px')
        .style('fill', 'black') // 确保文本颜色为黑色，增强可见性
        .text(d3.format(".2f")(legendDomain[0])); // 最高概率值

    legend.append('text')
        .attr('transform', `translate(${legendWidth + textYOffset}, ${legendHeight}) rotate(90)`)
        .style('font-size', '10px')
        .style('fill', 'black') // 确保文本颜色为黑色，增强可见性
        .text(d3.format(".2f")(legendDomain[1])); // 最低概率值

    // 为图例标题添加适当的旋转和位置调整
    legend.append('text')
        .attr('transform', `translate(${legendWidth + 20}, ${legendHeight / 2}) rotate(90)`)
        .style('font-size', '12px')
        .style('text-anchor', 'middle')
        .style('fill', 'black') // 确保文本颜色为黑色，增强可见性
        .text('Probability');

    // 创建缩放行为，只针对 x 轴
    const zoom = d3.zoom()
        .scaleExtent([1, 10]) // 允许的缩放范围
        .translateExtent([[0, 0], [width, height]]) // 拖动范围
        .on('zoom', (event) => {
            // 更新 xScale 的域
            const newXScale = event.transform.rescaleX(xScale);

            // 更新坐标轴
            svg.select('.x-axis').call(xAxis.scale(newXScale));

            // 更新方块的位置和宽度
            svg.selectAll('rect')
                .attr('x', d => newXScale(d.node.split('/').pop()))
                .attr('width', newXScale.bandwidth());
        });

    // 应用缩放行为到容器
    d3.select(chartContainer.value).select('svg')
        .call(zoom);
};

</script>

<style scoped>
/* .el-dialog__body{
    padding: 0px !important; 
} */
</style>
