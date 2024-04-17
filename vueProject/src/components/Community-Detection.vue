<template>
    <div>
    <svg ref="svgRef" :key="updateKey" width="900" height="708"></svg>
    </div>
</template>

<script setup>
import * as d3 from 'd3';
import { onMounted, ref, watch, nextTick } from 'vue';
import { useStore } from 'vuex';
const store = useStore();

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
    const allnodeid = graphData.value.nodes.map(d => {
        const parts = d.id.split("/");
        return parts[parts.length - 1];
    });
    store.commit('SET_ALL_VISIBLE_NODES', allnodeid);
};

// D3 渲染逻辑
const renderGraph = () => {
    // 检查对话框是否已经打开并且SVG已经渲染
    if (!graphData.value || !svgRef.value || !svgRef.value.clientWidth) return;

    const width = svgRef.value.clientWidth * 2; // 动态获取宽度
    const height = svgRef.value.clientHeight * 2; // 动态获取高度

    d3.select(svgRef.value).selectAll("*").remove(); //清除之前的内容

    const svg = d3.select(svgRef.value)
        .attr("viewBox", [-width / 2, -height / 2, width, height])
        .call(zoom);

    g = svg.append("g"); // 创建g元素并赋值给变量g

    const color = d3.scaleOrdinal(d3.schemePastel2);
    const links = graphData.value.links.map(d => ({ ...d }));
    const nodes = graphData.value.nodes.map(d => ({ ...d }));
    const groupByGroup = d3.groups(nodes, d => d.group);
    let groupPaths = {}; // 用于存储每个组的凸包路径
    // console.log()



    const simulation = d3.forceSimulation(nodes)
        .force("link", d3.forceLink(links).id(d => d.id).distance(70))
        .force("charge", d3.forceManyBody().strength(-200))
        .force("center", d3.forceCenter(width / 2, height / 2))
        .force("x", d3.forceX(width / 2).strength(0.06)) // 添加X轴力
        .force("y", d3.forceY(height / 2).strength(0.06)) // 添加Y轴力
        .on("tick", ticked); // 使用 tick 事件实时更新凸包

    svg.attr("viewBox", [0, 0, width, height])
        .attr("style", "max-width: 100%; height: auto;");

    const hullGroup = g.append("g").attr("class", "hull-group");
    const linkGroup = g.append("g").attr("class", "link-group");
    const nodeGroup = g.append("g").attr("class", "node-group");

    // hullGroup.selectAll(".hull").remove();

    groupByGroup.forEach(group => {
        const groupName = group[0];
        const points = group[1].map(d => [d.x, d.y]);
        let fakePoints = [];
        if (points.length === 2) {
            // Calculate fake points for rounded convex hull effect
            const dx = points[1][0] - points[0][0];
            const dy = points[1][1] - points[0][1];
            const scale = 0.00001;
            const mx = (points[0][0] + points[1][0]) / 2;
            const my = (points[0][1] + points[1][1]) / 2;
            fakePoints = [
                [mx + dy * scale, my - dx * scale],
                [mx - dy * scale, my + dx * scale]
            ];
        }

        const hullPoints = d3.polygonHull(points.concat(fakePoints));
        if (hullPoints) {
            hullPoints.push(hullPoints[0]); // Close the path by pushing the first point again
            groupPaths[groupName] = "M" + hullPoints.join("L") + "Z"; // Ensure path is closed
        }


        const hullsSelection = hullGroup.selectAll(".hull")
            .data(Object.entries(groupPaths), d => d[0]);

        hullsSelection.join(
            enter => enter.append("path")
                .attr("class", "hull")
                .attr("fill", d => d3.color(color(d[0])).copy({ opacity: 1 }).toString())
                .attr("stroke", d => color(d[0]))
                .attr("stroke-width", 75)
                .attr("stroke-linejoin", "round")
                .attr("d", d => d[1])
                .on('click', (event, d) => {
                    hullClicked(event, d)
                })
                .attr("style", "cursor: pointer;"),
            update => update
                .attr("d", d => d[1]),
            exit => exit.remove()
        );

    });

    function updateHulls() {
        groupByGroup.forEach(group => {
            const groupName = group[0];
            const points = group[1].map(d => [d.x, d.y]);
            let fakePoints = [];
            if (points.length === 2) { 
                // Calculate fake points for rounded convex hull effect
                const dx = points[1][0] - points[0][0];
                const dy = points[1][1] - points[0][1];
                const scale = 0.00001;
                const mx = (points[0][0] + points[1][0]) / 2;
                const my = (points[0][1] + points[1][1]) / 2;
                fakePoints = [
                    [mx + dy * scale, my - dx * scale],
                    [mx - dy * scale, my + dx * scale]
                ];
            }

            const hullPoints = d3.polygonHull(points.concat(fakePoints));
            if (hullPoints) {
                hullPoints.push(hullPoints[0]); // Close the path by pushing the first point again
                groupPaths[groupName] = "M" + hullPoints.join("L") + "Z"; // Ensure path is closed
            }


            const hullsSelection = hullGroup.selectAll(".hull")
                .data(Object.entries(groupPaths), d => d[0]);

            hullsSelection.join(
                enter => enter.append("path")
                    .attr("class", "hull")
                    .attr("fill", d => d3.color(color(d[0])).copy({ opacity: 1 }).toString())
                    .attr("stroke", d => color(d[0]))
                    .attr("stroke-width", 60)
                    .attr("stroke-linejoin", "round")
                    .attr("d", d => d[1])
                    .on('click', (event, d) => {
                        hullClicked(event, d)
                    })
                    .attr("style", "cursor: pointer;"),
                update => update
                    .attr("d", d => d[1]),
                exit => exit.remove()
            );

        });
    }

    const link = linkGroup.append("g")
        .attr("stroke", "#000")
        .attr("stroke-opacity", 0.8)
        .selectAll("line")
        .data(links)
        .join("line")
        .attr("stroke-width", d => d.value );

    const node = nodeGroup.append("g")
        .attr("stroke", "#000")
        .attr("stroke-width", 3)
        .selectAll("circle")
        .data(nodes)
        .join("circle")
        .attr("r", 14)
        .attr("id", d => {
            const parts = d.id.split("/");
            return parts[parts.length - 1];
        })
        .attr("community-group", d => d.group)
        .attr("style", "cursor: pointer;")
        .attr("fill", d => {
            const svgTag = d.id.split('/'); // 获取 SVG 标签
            const parts = svgTag[svgTag.length - 1]
            const index = parts.split('_')[0]
            return customColorMap[index] || color(d.group); // 使用自定义颜色或默认颜色
        })
        .on("click", (event, d) => {
            handleNodeClick(d);
        })
        .on("mouseover", (event, d) => {
            const [x, y] = d3.pointer(event, svg.node());
            const xOffset = 30; // 根据需要调整偏移量
            const yOffset = 10;  // 如有必要，也可以对y进行调整

            svg.selectAll(".labels text")
                .filter(node => node.id === d.id)
                .style("display", "block")
                .attr("x", x + xOffset)
                .attr("y", y + yOffset);
        });
    

    node.call(d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended));

    function ticked() {
        updateHulls(); // 更新凸包的位置和样式
        link
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);

        node
            .attr("cx", d => d.x)
            .attr("cy", d => d.y);

        // labels
        //     .attr("x", d => d.x)
        //     .attr("y", d => d.y);
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

    function hullClicked(event, d) {
        const groupName = d[0];
        const groupNodes = nodes.filter(node => String(node.group) === groupName);
        const nodeIds = groupNodes.map(node => {
            const parts = node.id.split("/");
            return parts[parts.length - 1];
        });
        
        store.commit('UPDATE_SELECTED_NODES', { nodeIds, group: groupName });
    }

    simulation.on("tick", ticked);

    const legendGroup = svg.append("g")
        .attr("class", "legend-group")
        .attr("transform", `translate(${width - 145}, 20)`); // 将图例放在 SVG 的右上角

    // 为每个标签添加图例项
    Object.entries(customColorMap).forEach(([tag, color], index) => {
        const legendItem = legendGroup.append("g")
            .attr("class", "legend-item")
            .attr("transform", `translate(0, ${index * 100})`); // 每个图例项向下偏移

        legendItem.append("circle")
            .attr("r", 15)
            .attr("cx", -45) // 向左移动 5 个单位
            .attr("fill", color);

        legendItem.append("text")
            .attr("x", -15)
            .attr("y", 9)
            .text(tag)
            .attr("font-size", "35px")
            .attr("fill", "#000");
    });
};

onMounted(async () => {
    await nextTick(); // 确保组件渲染完成
    fetchData();
});
watch(() => graphData.value, renderGraph, { deep: true });
</script>
