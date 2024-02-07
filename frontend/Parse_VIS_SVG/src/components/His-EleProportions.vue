<template>
    <svg ref="chart" width="230" height="140"></svg><br>
</template>
  
<script setup>
import { onMounted, ref } from 'vue';
import * as d3 from 'd3';

// 创建一个响应式的数据属性
const randomData = ref([]);

// 生成随机数据的函数
const generateRandomData = () => {
    return Array.from({ length: 10 }, () => Math.floor(Math.random() * 100));
};

// 在组件挂载时生成数据
randomData.value = generateRandomData();

const chart = ref(null);

onMounted(() => {
    const data = randomData.value; // 使用本地生成的随机数据
    // console.log(data);
    if (data.length === 0) return;

    const svgWidth = 225, svgHeight = 150;
    const margin = { top: 5, right: 5, bottom: 30, left: 20 };
    const width = svgWidth - margin.left - margin.right;
    const height = svgHeight - margin.top - margin.bottom;

    // 创建SVG画布
    const svg = d3.select(chart.value)
        .append('svg')
        .attr('width', svgWidth)
        .attr('height', svgHeight)
        .append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);

    // 设置x轴
    const x = d3.scaleBand()
        .rangeRound([0, width])
        .padding(0.1)
        .domain(data.map((d, i) => i));

    // 设置y轴
    const y = d3.scaleLinear()
        .range([height, 0])
        .domain([0, d3.max(data, d => d)]);

    // 绘制直方图的矩形
    svg.selectAll('.bar')
        .data(data)
        .enter().append('rect')
        .attr('class', 'bar')
        .attr('x', (d, i) => x(i))
        .attr('y', d => y(d))
        .attr('width', x.bandwidth())
        .attr('height', d => height - y(d))
        .attr('fill', 'steelblue');

    // 添加x轴
    svg.append('g')
        .attr('transform', `translate(0,${height})`)
        .call(d3.axisBottom(x));

    // 添加y轴
    svg.append('g')
        .call(d3.axisLeft(y));
});
</script>
  
<style>
.bar {
    fill: steelblue;
}

.title {
    font-size: 12px;
    color: #666;
    font-weight: 300;
}
</style>
  