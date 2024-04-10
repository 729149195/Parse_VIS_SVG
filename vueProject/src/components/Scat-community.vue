<template>
  <div ref="chartContainer"></div>
</template>

<script setup>
import { onMounted, ref, computed } from 'vue';
import * as d3 from 'd3';
import { useStore } from 'vuex';
const store = useStore();

const eleURL = "http://localhost:8000/group_data"
const chartContainer = ref(null);
// const ele_num_array = computed(() => store.state.ele_num_data);  //从store中获取当前svg所有tag及其标签数量的接口

onMounted(async () => {
  if (!chartContainer.value) return;
  try {
    const response = await fetch(eleURL);
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    const data = await response.json();
    store.commit('GET_ELE_NUM_DATA', data);
    render(data)
  } catch (error) {
    console.error('There has been a problem with your fetch operation:', error);
  }
});

const render = (data) => {
  if (!chartContainer.value) return;

  const width = 290;
  const height = 225;
  const marginTop = 20;
  const marginRight = 10;
  const marginBottom = 40;
  const marginLeft = 45;

  // 修改x轴的比例尺为scalePoint，适用于散点图
  const x = d3.scalePoint()
    .domain(data.map(d => d.group))
    .range([marginLeft, width - marginRight])
    .padding(0.5); // 为散点图设置padding，确保分布均匀

  // y轴比例尺保持不变，适用于线性数据
  const y = d3.scaleLinear()
    .domain([0, d3.max(data, d => d.num)]).nice()
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
        // 更新x比例尺的范围
        x.range([marginLeft, width - marginRight].map(d => event.transform.applyX(d)));

        // 更新散点的位置
        svg.selectAll('circle')
          .attr('cx', d => x(d.group)); // 更新点的cx属性以反映缩放/平移后的新位置
        svg.selectAll('.circle-text')
          .attr('x', d => x(d.group) + x.bandwidth() / 2); // 更新文本位置
        // 更新x轴
        svg.selectAll('.x-axis').call(d3.axisBottom(x).tickSizeOuter(0));
      }));
  };

  // 绘制散点图的点
  svg.append('g')
    .selectAll('circle')
    .data(data)
    .join('circle')
    .attr('cx', d => x(d.group)) // 使用cx属性定位点的x位置
    .attr('cy', d => y(d.num)) // 使用cy属性定位点的y位置
    .attr('r', 5) // 设置点的半径
    .attr('fill', 'steelblue'); // 根据数据的visible属性设置填充色


  svg.append('g')
    .attr('class', 'x-axis')
    .attr('transform', `translate(0,${height - marginBottom})`)
    .call(d3.axisBottom(x))
    .selectAll("text")
    .style("text-anchor", "end")
    .style("pointer-events", "none")
    .style("font-size", "10px") // 设置字体大小为10px
    // .attr("dx", "-.2em")
    .attr("dy", "1.15em");
    // .attr("transform", "rotate(-45)");

  svg.append('g')
    .attr('class', 'y-axis')
    .style("pointer-events", "none")
    .attr('transform', `translate(${marginLeft},0)`)
    .call(d3.axisLeft(y));

  svg.append("text")
        .attr("transform", `translate(${width / 2},${height - 5})`)
        .style("text-anchor", "middle")
        .style("font-size", "10px")
        .attr("dx", "11em")
        .attr("dy", ".25em")
        .text("Community");

    // 添加 y 轴图例
    svg.append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", 15)
        .attr("x", 0 - (height / 2))
        .style("text-anchor", "middle")
        .style("font-size", "12px")
        .attr("dx", "3.50em")
        .attr("dy", "-.2em")
        .text("Community Number");

  zoom(svg);
};
</script>

<style scoped></style>
