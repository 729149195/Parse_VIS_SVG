<template>
    <svg ref="svgRef" :key="updateKey" width="900" height="600"></svg>
</template>

<script setup>
import * as d3 from 'd3';
import { onMounted, ref, watch, nextTick } from 'vue';
import { useStore } from 'vuex';
const store = useStore();

const svgRef = ref(null);
const updateKey = ref(0); // 定义 updateKey
const dataUrl = "http://127.0.0.1:8000/community_data";
const graphData = ref(null);
let g; // 用于引用SVG中的g元素

const zoom = d3.zoom()
    .scaleExtent([0.5, 5])
    .on("zoom", (event) => {
        g.attr("transform", event.transform);
    });

// 加载数据的函数
const fetchData = async () => {
    try {
        const response = await fetch(dataUrl);
        graphData.value = await response.json();
    } catch (error) {
        console.error("Failed to fetch data:", error);
    }
};

// D3 渲染逻辑
const renderGraph = () => {
    // 检查对话框是否已经打开并且SVG已经渲染
    if (!graphData.value || !svgRef.value || !svgRef.value.clientWidth) return;

    const width = svgRef.value.clientWidth; // 动态获取宽度
    const height = svgRef.value.clientHeight; // 动态获取高度

    d3.select(svgRef.value).selectAll("*").remove(); //清除之前的内容

    const svg = d3.select(svgRef.value)
        .attr("viewBox", [-width / 2, -height / 2, width, height])
        .call(zoom);

    g = svg.append("g"); // 创建g元素并赋值给变量g


    const color = d3.scaleOrdinal(d3.schemeCategory10);
    const links = graphData.value.links.map(d => ({ ...d }));
    const nodes = graphData.value.nodes.map(d => ({ ...d }));

    const simulation = d3.forceSimulation(nodes)
        .force("link", d3.forceLink(links).id(d => d.id))
        .force("charge", d3.forceManyBody())
        .force("center", d3.forceCenter(width / 2, height / 2));

    svg.attr("viewBox", [0, 0, width, height])
        .attr("style", "max-width: 100%; height: auto;");

    const link = svg.append("g")
        .attr("stroke", "#999")
        .attr("stroke-opacity", 0.6)
        .selectAll("line")
        .data(links)
        .join("line")
        .attr("stroke-width", d => Math.sqrt(d.value));

    const node = svg.append("g")
        .attr("stroke", "#fff")
        .attr("stroke-width", 2)
        .selectAll("circle")
        .data(nodes)
        .join("circle")
        .attr("r", 8)
        .attr("id", d => {
            const parts = d.id.split("/");
            return parts[parts.length - 1];
        })
        .attr("community-group", d => d.group)
        .attr("style", "cursor: pointer;")
        .attr("fill", d => color(d.group))
        .on("click", (event, d) => {
            handleNodeClick(d);
        });


    const labels = svg.append("g")
        .attr("class", "labels")
        .selectAll("text")
        .data(nodes)
        .join("text")
        .attr("x", d => d.x)
        .attr("y", d => d.y)
        .text(d => {
            const parts = d.id.split("/");
            return parts[parts.length - 1];
        })
        .attr("font-size", "13px")
        .attr("dx", 10)   // 设置文本相对于节点的位置
        .attr("dy", ".35em") // 垂直居中文本
        .style("user-select", "none") // 防止文本被选中
        .style("pointer-events", "none"); // 防止文本响应鼠标事件

    node.append("title")
        .text(d => d.id);

    node.call(d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended));

    function ticked() {
        link
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);

        node
            .attr("cx", d => d.x)
            .attr("cy", d => d.y);

        labels
            .attr("x", d => d.x)
            .attr("y", d => d.y);
    }

    function dragstarted(event) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        event.subject.fx = event.subject.x;
        event.subject.fy = event.subject.y;
    }

    function dragged(event) {
        event.subject.fx = event.x;
        event.subject.fy = event.y;
    }

    function dragended(event) {
        if (!event.active) simulation.alphaTarget(0);
        event.subject.fx = null;
        event.subject.fy = null;
    }
    function handleNodeClick(clickedNode) {
        const sameGroupNodes = nodes.filter(node => node.group === clickedNode.group);
        const nodeIds = sameGroupNodes.map(node => {
            const parts = node.id.split("/");
            return parts[parts.length - 1];
        });

        // 提交 Vuex mutation 或 action
        store.commit('UPDATE_SELECTED_NODES', { nodeIds, group: clickedNode.group });
    }

    simulation.on("tick", ticked);
};

onMounted(async () => {
    await nextTick(); // 确保组件渲染完成
    fetchData();
});
watch(() => graphData.value, renderGraph, { deep: true });
</script>

<style>
/* 您的样式 */
</style>
