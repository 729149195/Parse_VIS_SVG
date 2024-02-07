<template>
    <svg ref="chart" width="230" height="140"></svg><br>
  </template>
  
  <script setup>
  import { onMounted, ref } from 'vue';
  import * as d3 from 'd3';
  
  // 生成随机数据的函数，生成包含x和y值的对象数组
  const generateRandomData = () => {
    return Array.from({ length: 50 }, () => ({
      x: Math.random() * 100,
      y: Math.random() * 100,
    }));
  };
  
  // 创建一个响应式的数据属性
  const randomData = ref(generateRandomData());
  
  const chart = ref(null);
  
  onMounted(() => {
      const data = randomData.value;
      if (data.length === 0) return;
  
      const svgWidth = 230, svgHeight = 140;
      const margin = { top: 8, right:15, bottom: 20, left: 25 };
      const width = svgWidth - margin.left - margin.right;
      const height = svgHeight - margin.top - margin.bottom;
  
      // 创建SVG画布
      const svg = d3.select(chart.value)
          .attr('width', svgWidth)
          .attr('height', svgHeight)
        .append('g')
          .attr('transform', `translate(${margin.left},${margin.top})`);
  
      // 设置x轴比例尺
      const x = d3.scaleLinear()
          .domain([0, 100])
          .range([0, width]);
  
      // 设置y轴比例尺
      const y = d3.scaleLinear()
          .domain([0, 100])
          .range([height, 0]);
  
      // 绘制散点图的圆点
      svg.selectAll('circle')
          .data(data)
          .enter().append('circle')
          .attr('cx', d => x(d.x))
          .attr('cy', d => y(d.y))
          .attr('r', 3) // 圆点的半径
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
  /* 样式保持不变 */
  .bar {
    fill: steelblue;
  }
  
  .title {
    font-size: 12px;
    color: #666;
    font-weight: 300;
  }
  </style>
  