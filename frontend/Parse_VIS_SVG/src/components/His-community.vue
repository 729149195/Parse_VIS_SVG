<template>
    <div ref="chartContainer"></div>
</template>
  
<script setup>
import { onMounted, ref, computed } from 'vue';
import * as d3 from 'd3';
import { useStore } from 'vuex';
const store = useStore();

const eleURL = "http://localhost:8000/ele_num_data"
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

    const width = 245;
    const height = 190;
    const marginTop = 20;
    const marginRight = 10;
    const marginBottom = 40;
    const marginLeft = 30;

    const x = d3.scaleBand()
        .domain(data.map(d => d.tag))
        .range([marginLeft, width - marginRight])
        .padding(0.1);


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
                x.range([marginLeft, width - marginRight].map(d => event.transform.applyX(d)));
                svg.selectAll('.bars')
                    .attr('x', d => x(d.tag))
                    .attr('width', x.bandwidth());
                svg.selectAll('.bar-text')
                    .attr('x', d => x(d.tag) + x.bandwidth() / 2); // 更新文本位置
                svg.selectAll('.x-axis').call(d3.axisBottom(x));
            }));
    };


    svg.append('g')
        .selectAll('rect')
        .data(data)
        .join('rect')
        .attr('class', 'bars')
        .attr('fill', d => d.visible ? 'steelblue' : '#999')
        .attr('x', d => x(d.tag))
        .attr('y', d => y(d.num))
        .attr('height', d => y(0) - y(d.num))
        .attr('width', x.bandwidth());

    svg.append('g')
        .attr('class', 'x-axis')
        .attr('transform', `translate(0,${height - marginBottom})`)
        .call(d3.axisBottom(x))
        .selectAll("text")
        .style("text-anchor", "end")
        .style("pointer-events", "none")
        .style("font-size", "10px") // 设置字体大小为10px
        .attr("dx", "-.4em")
        .attr("dy", ".15em")
        .attr("transform", "rotate(-45)");

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
        .attr('x', d => x(d.tag) + x.bandwidth() / 2) // 定位到条形的中心
        .style("font-size", "12px") // 设置字体大小为10px
        .attr('y', d => y(d.num) - 5) // 在条形顶部稍微上方位置显示数值
        .attr('text-anchor', 'middle') // 确保文本居中对齐
        .text(d => d.num); // 设置文本内容为数值
    zoom(svg);
};
</script>
  
<style scoped></style>
  