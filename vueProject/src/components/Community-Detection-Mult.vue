<template>
    <svg :width="width" :height="height" ref="svg"></svg>
    <div class="hull-select">
        <el-switch v-model="subsubgroupHull" size="small" style="--el-switch-on-color: #9ecae1;" />
        <el-switch v-model="subgroupHull" size="small" style="--el-switch-on-color: #ff9896;" />
        <el-switch v-model="groupHull" size="small" style="--el-switch-on-color: #FFC000;" />
    </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import * as d3 from 'd3';
import { useStore } from 'vuex';
const store = useStore();

const width = 540;
const height = 426.5;
const svg = ref(null);
const apiUrl = 'http://127.0.0.1:8000/community_data_mult';
const subsubgroupHull = ref(true);
const subgroupHull = ref(true);
const groupHull = ref(true);

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
const subgroupHullColor = "#ff9896";
const subsubgroupHullColor = "#9ecae1";

async function fetchData() {
    const response = await fetch(apiUrl);
    const data = await response.json();
    graphData.value.nodes = data.GraphData.node;
    graphData.value.links = data.GraphData.links;
    graphData.value.groups = data.GraphData.group;
    graphData.value.subgroups = data.GraphData.subgroups;
    graphData.value.subsubgroups = data.GraphData.subsubgroups;
    submitAllNodes();
    initializeGraph();
}

onMounted(fetchData);
watch([groupHull, subgroupHull, subsubgroupHull], () => {
    const svgElement = d3.select(svg.value); // 选择SVG元素
    svgElement.selectAll('.group-hull').style('display', groupHull.value ? null : 'none');
    svgElement.selectAll('.subgroup-hull').style('display', subgroupHull.value ? null : 'none');
    svgElement.selectAll('.subsubgroup-hull').style('display', subsubgroupHull.value ? null : 'none');
});

function updatahull() {
    const svgElement = d3.select(svg.value); // 选择SVG元素
    svgElement.selectAll('.group-hull').style('display', groupHull.value ? null : 'none');
    svgElement.selectAll('.subgroup-hull').style('display', subgroupHull.value ? null : 'none');
    svgElement.selectAll('.subsubgroup-hull').style('display', subsubgroupHull.value ? null : 'none');
}

function submitAllNodes() {
    const nodeIds = graphData.value.nodes.map(node => {
        const parts = node.id.split("/");
        return parts[parts.length - 1]; // 假设节点的唯一标识位于id的最后一部分
    });

    // console.log(nodeIds); // Optional: For debugging purposes
    store.commit('UPDATE_SELECTED_NODES', { nodeIds, group: null }); // 假设这是你的mutation
}

function hullClicked(event, d) {
    // 确定当前激活的Hull层级
    let activeHullLevel;
    let groupName;

    // 检查所有的开关是否都关闭
    const isAllHullsOff = !groupHull.value && !subgroupHull.value && !subsubgroupHull.value;

    if (!isAllHullsOff) {
        if (groupHull.value) {
            activeHullLevel = graphData.value.groups;
        } else if (subgroupHull.value) {
            activeHullLevel = graphData.value.subgroups;
        } else if (subsubgroupHull.value) {
            activeHullLevel = graphData.value.subsubgroups;
        }

        // 找出点击的节点属于哪个组
        for (const group of activeHullLevel) {
            if (group.includes(d.id)) {
                groupName = group[0]; // 假设组的标识或名称存储在数组的第一个位置
                break;
            }
        }

        // 过滤出同组的所有节点
        const groupNodes = graphData.value.nodes.filter(node => activeHullLevel.find(group => group.includes(node.id) && group[0] === groupName));
        const nodeIds = groupNodes.map(node => {
            const parts = node.id.split("/");
            return parts[parts.length - 1];
        });

        // console.log(typeof(nodeIds));
        // 向Vuex提交这些节点的ID和组名
        store.commit('UPDATE_SELECTED_NODES', { nodeIds, group: null });
    } else {
        // 如果所有的开关都关闭，则只提交被点击的节点
        const parts = d.id.split("/");
        const nodeId = parts[parts.length - 1];

        // console.log([nodeId]);
        // 向Vuex提交被点击的节点ID
        store.commit('UPDATE_SELECTED_NODES', { nodeIds: [nodeId], group: null });
    }
}

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

    const hullGroup = contentGroup.append('g').attr('class', 'hulls');
    const linkGroup = contentGroup.append('g').attr('class', 'links');
    const nodeGroup = contentGroup.append('g').attr('class', 'nodes')

    simulation = d3.forceSimulation(graphData.value.nodes)
        .force('link', d3.forceLink(graphData.value.links).id(d => d.id).distance(30))
        .force('charge', d3.forceManyBody().strength(-80))
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
        .attr('r', 7)
        .attr("id", d => {
            const parts = d.id.split("/");
            return parts[parts.length - 1];
        })
        .attr("style", "cursor: pointer;")
        .attr("fill", d => {
            const svgTag = d.id.split('/'); // 获取 SVG 标签
            const parts = svgTag[svgTag.length - 1]
            const index = parts.split('_')[0]
            return customColorMap[index] || color(d.propertyValue * 1); // 使用自定义颜色或默认颜色
        })
        .on('click', hullClicked) // 绑定点击事件
        .call(drag(simulation));

    node.append('title')
        .text(d => {
            const idParts = d.id.split('/'); // 使用 '/' 分隔 id
            const lastPart = idParts.pop(); // 取最后一部分
            return `${lastPart}`; // 返回处理后的文本
        });

    simulation.on('tick', () => {
        hullGroup.selectAll('path').remove();
        drawHulls(hullGroup, graphData.value.groups, groupHullColor, 'group-hull');
        drawHulls(hullGroup, graphData.value.subgroups, subgroupHullColor, 'subgroup-hull');
        drawHulls(hullGroup, graphData.value.subsubgroups, subsubgroupHullColor, 'subsubgroup-hull');
        updatahull()

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
            .attr("r", 4.5)
            .attr("cx", 0)
            .attr("cy", -1)
            .attr("fill", color);

        legendItem.append("text")
            .attr("x", 10)
            .attr("y", 1.6)
            .text(tag)
            .attr("font-size", "10px") // 文本大小
            .attr("fill", "#000"); // 文本颜色
    });
    // 设置初始缩放级别
    const initialZoom = d3.zoomIdentity.translate(width / 2, height / 2).scale(0.5).translate(-width / 2, -height / 2);
    svgEl.call(zoom.transform, initialZoom);
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
        .style('stroke-width', className === 'group-hull' ? 35 : className === 'subgroup-hull' ? 30 : 25)
        .style('stroke-linejoin', 'round')
        .style('opacity', className === 'group-hull' ? 0.15 : 0.5);
}


</script>

<style lang="scss">
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

.hull-select {
    position: absolute;
    display: flex;
    flex-direction: column;
    padding: 0;
    margin: 0;
    bottom: 50px;

}
</style>