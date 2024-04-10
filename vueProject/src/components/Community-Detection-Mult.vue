<template>
    <svg :width="width" :height="height" ref="svg"></svg>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import * as d3 from 'd3';

const width = 540;
const height = 421;
const svg = ref(null);
const apiUrl = 'http://127.0.0.1:8000/community_data_mult';

const customColorMap = {
    "rect": "#E6194B", // 猩红
    "path": "#3CB44B", // 明绿
    "circle": "#FFE119", // 鲜黄
    "line": "#4363D8", // 宝蓝
    "polygon": "#F58231", // 橙色
    "polyline": "#911EB4", // 紫色
    "text": "#46F0F0", // 青色
    "ellipse": "#F032E6", // 紫罗兰
    "image": "#BCF60C", // 酸橙
    "clipPath": "#FABEBE", // 粉红
};

const graphData = ref({
    nodes: [],
    links: [],
    groups: [],
    subgroups: [],
    subsubgroups: []
});

let simulation;

const color = d3.scaleLinear().domain([-2, 4]).range(["#252525", "#cccccc"]);
const groupHullColor = "#FFC000";
const subgroupHullColor = "#9ecae1";
const subsubgroupHullColor = "#ff9896";

async function fetchData() {
    const response = await fetch(apiUrl);
    const data = await response.json();
    graphData.value.nodes = data.GraphData.node;
    graphData.value.links = data.GraphData.links;
    graphData.value.groups = data.GraphData.group;
    graphData.value.subgroups = data.GraphData.subgroups;
    graphData.value.subsubgroups = data.GraphData.subsubgroups;
    initializeGraph();
}

onMounted(fetchData);

function initializeGraph() {
    const svgEl = d3.select(svg.value)
        .attr('width', width)
        .attr('height', height);

    // 定义缩放行为
    const zoom = d3.zoom()
        .on("zoom", (event) => {
            contentGroup.attr("transform", event.transform);
        });

    // 将缩放行为应用于 SVG
    svgEl.call(zoom);

    // 添加一个 'g' 元素来包含所有图形内容（包括节点、连线和凸包）
    const contentGroup = svgEl.append('g').attr('class', 'content');
    
    // 注意：现在连线（links）、节点（nodes）和凸包（hulls）都应该添加到 contentGroup 下
    const hullGroup = contentGroup.append('g').attr('class', 'hulls');
    const linkGroup = contentGroup.append('g').attr('class', 'links');
    const nodeGroup = contentGroup.append('g').attr('class', 'nodes')

    simulation = d3.forceSimulation(graphData.value.nodes)
        .force('link', d3.forceLink(graphData.value.links).id(d => d.id).distance(30))
        .force('charge', d3.forceManyBody().strength(-120))
        .force('center', d3.forceCenter(width / 2, height / 2));

    // 创建连线
    const link = linkGroup.selectAll('line')
        .data(graphData.value.links)
        .enter().append('line')
        .attr('class', 'link')
        .style('stroke-width', d => Math.sqrt(d.value));

    // 创建节点
    const node = nodeGroup.selectAll('circle')
        .data(graphData.value.nodes)
        .enter().append('circle')
        .attr('class', 'node')
        .attr('r', 6)
        .attr("id", d => {
            const parts = d.id.split("/");
            return parts[parts.length - 1];
        })
        .attr("style", "cursor: pointer;")
        .attr("fill", d => {
            const svgTag = d.id.split('/'); // 获取 SVG 标签
            const parts = svgTag[svgTag.length - 1]
            const index = parts.split('_')[0]
            console.log(index)
            return customColorMap[index] || color(d.propertyValue * 1); // 使用自定义颜色或默认颜色
        })
        .call(drag(simulation));

    node.append('title')
        .text(d => `id: ${d.id}`);

    simulation.on('tick', () => {
        hullGroup.selectAll('path').remove();
        drawHulls(hullGroup, graphData.value.groups, groupHullColor, 'group-hull');
        drawHulls(hullGroup, graphData.value.subgroups, subgroupHullColor, 'subgroup-hull');
        drawHulls(hullGroup, graphData.value.subsubgroups, subsubgroupHullColor, 'subsubgroup-hull');

        link
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);

        node
            .attr('cx', d => d.x)
            .attr('cy', d => d.y);
    });
    // 添加图例
    const legendGroup = svgEl.append("g")
        .attr("class", "legend-group")
        .attr("transform", `translate(${width - 57}, 7)`); // 将图例放在 SVG 的右上角

    // 为每个标签添加图例项
    Object.entries(customColorMap).forEach(([tag, color], index) => {
        const legendItem = legendGroup.append("g")
            .attr("class", "legend-item")
            .attr("transform", `translate(0, ${index * 30})`); // 每个图例项向下偏移，适当调整间距以适合视图

        legendItem.append("circle")
            .attr("r", 4.5) // 根据实际情况调整圆的半径
            .attr("cx", 0) // 圆心的x坐标
            .attr("cy", -1) // 圆心的y坐标，由于已经通过transform进行了位移，这里可设置为0
            .attr("fill", color);

        legendItem.append("text")
            .attr("x", 10) // 文本的x坐标，让文本与圆形有些间隔
            .attr("y", 1.6) // 文本的y坐标，稍微调整以与圆形对齐
            .text(tag) // 显示的文本
            .attr("font-size", "10px") // 文本大小
            .attr("fill", "#000"); // 文本颜色
    });
}

// Drag behavior
const drag = (simulation) => {
    function start(event, d) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }

    function dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }

    function end(event, d) {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }

    return d3.drag()
        .on('start', start)
        .on('drag', dragged)
        .on('end', end);
};

function drawHulls(hullGroup, groups, fillColor, className) {
    const hullsData = groups.map(group => {
        const points = group.map(member => graphData.value.nodes.find(n => n.id === member)).map(n => [n.x, n.y]);
        // 对于只有一个节点的情况，创建虚拟点以构成凸包
        if (points.length === 1) {
            const [x, y] = points[0];
            return [
                [x, y],
                [x + 0.1, y + 0.1], // 添加一些微小的偏移创建虚拟点
                [x - 0.1, y - 0.1]
            ];
        }
        // 对于有两个节点的情况，同样添加虚拟点
        if (points.length === 2) {
            const [p1, p2] = points;
            const midX = (p1[0] + p2[0]) / 2;
            const midY = (p1[1] + p2[1]) / 2;
            return [
                p1,
                p2,
                [midX + 0.1, midY + 0.1], // 添加一个位于中点附近的虚拟点
            ];
        }
        return points;
    }).map(points => d3.polygonHull(points));

    hullGroup.selectAll(`.${className}`)
        .data(hullsData)
        .join('path')
        .attr('class', className)
        .attr('d', d => `M${d.join('L')}Z`)
        .style('fill', fillColor)
        .style('stroke', fillColor)
        .style('stroke-width', className === 'group-hull' ? 28 : className === 'subgroup-hull' ? 23 : 18)
        .style('stroke-linejoin', 'round')
        .style('opacity', className === 'group-hull' ? 0.2 : 0.8);
}


</script>

<style>
.links {
    stroke: #333;
    stroke-opacity: 0.6;
}

.nodes {
    stroke: #fff;
    stroke-width: 1.5px;
}

.hulls {
    fill: none;
    stroke: #c0c0c0;
}
</style>