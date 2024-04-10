<template>
    <div ref="chartContainer" style="width: 550px; height: 200px; overflow: hidden;"></div>
  </template>
  
  <script setup>
  import { onMounted, ref } from 'vue';
  import * as d3 from 'd3';
  
  const eleURL = "http://localhost:8000/layer_data"
  const chartContainer = ref(null);
  
  onMounted(async () => {
    if (!chartContainer.value) return;
    try {
      const response = await fetch(eleURL);
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      const data = await response.json();
      renderTree(data);
    } catch (error) {
      console.error('There has been a problem with your fetch operation:', error);
    }
  });
  
  const renderTree = (data) => {
    const width = 550;
    const height = 200;
    const margin = { top: 20, right: 10, bottom: 20, left: 40 };
  
    d3.select(chartContainer.value).select('svg').remove();
  
    const svg = d3.select(chartContainer.value)
      .append('svg')
      .attr('viewBox', `0 0 ${width} ${height + margin.top + margin.bottom}`)
      .style('user-select', 'none');
  
    const g = svg.append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);
  
    const zoom = d3.zoom()
      .scaleExtent([0.5, 8])
      .on('zoom', (event) => g.attr('transform', event.transform));
  
    svg.call(zoom);
  
    const root = d3.hierarchy(data).sum(d => d.value);
    const tree = d3.tree().nodeSize([20, 70]); // [节点之间的垂直距离, 节点之间的水平距离]

    const treeData = tree(root);
  
    const link = g.selectAll(".link")
      .data(treeData.links())
      .join("path")
      .attr("class", "link")
      .attr("d", d3.linkHorizontal()
          .x(d => d.y)
          .y(d => d.x))
      .attr("fill", "none")
      .attr("stroke", "#555")
      .attr("stroke-opacity", 0.4)
      .attr("stroke-width", 1.5);
  
    const node = g.selectAll(".node")
      .data(root.descendants())
      .join("g")
      .attr("class", "node")
      .attr("transform", d => `translate(${d.y},${d.x})`);
  
    node.append("circle")
      .attr("r", 2.5)
      .attr("fill", d => d.children ? "#555" : "#999");
  
    node.append("text")
      .attr("dy", "0.31em")
      .attr("x", d => d.children ? -6 : 6)
      .text(d => d.data.name.split("/").pop())
      .filter(d => d.children)
      .attr("text-anchor", "end")
      .clone(true).lower()
      .attr("stroke-linejoin", "round")
      .attr("stroke-width", 1)
      .attr("stroke", "white")
      .attr("style", "font-size: 1px;");
  };
  </script>
  
  <style scoped>
.link {
  fill: none;
  stroke: #555;
  stroke-opacity: 0.4;
  stroke-width: 1.5;
}

.node {
  font: 5px sans-serif; /* 调整整个节点的字体大小 */
}

.node circle {
  fill: #555;
  stroke-width: 2px;
}

.node text {
  stroke: white;
  stroke-width: 0.3px;
  user-select: none;
  font-size: 10px; /* 直接调整文本的字体大小 */
}
</style>

  