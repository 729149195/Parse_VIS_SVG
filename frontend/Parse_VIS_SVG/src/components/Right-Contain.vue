<template>
  <el-card class="box-card" v-loading="isLoading" element-loading-text="Parseing..." :element-loading-spinner="svg"
    element-loading-svg-view-box="-10, -10, 50, 50">
    <template #header>
      <div class="card-header">
        <span style="font-size:1.3em; font-weight: 700;" v-if="gmInfoData">{{ currentFileName }} </span>
        <el-button v-if="gmInfoData" class="button" type="primary" plain><span
            style="margin-right: 3px;">导出</span><el-icon style="margin-right: -4px;">
            <Download />
          </el-icon></el-button>
      </div>
    </template>
    <div class="card-body">
      <span style="font-size:1.1em; font-weight: 700;">process :</span>
      <el-card class="box-card-process" shadow="hover">
        <el-scrollbar height="35vh">
          <span v-if="gmInfoData"><el-tag effect="plain" style="font-size: 1em; margin-right: 10px;">nodes-num : {{
            gmInfoData.DiGraph.nodes }}</el-tag></span>
          <span v-if="gmInfoData"><el-tag effect="plain" style="font-size: 1em;">edges-num : {{
            gmInfoData.DiGraph.edges }}</el-tag></span>
          <el-empty description="No Data" :image-size="150" v-if="!gmInfoData" />
          <div v-if="gmInfoData" class="gm-info">
            <div v-for="(value, key) in gmInfoData.DiGraph.Nodes" :key="key">
              {{ key }}: {{ value }}
            </div>
          </div>
        </el-scrollbar>
      </el-card>

      <span style="font-size:1.1em; font-weight: 700; padding-top: 15px;">result :</span>

      <el-card class="box-card-result" shadow="hover">
        <el-scrollbar height="36vh">
          <el-empty description="No Data" :image-size="150" v-if="!gmInfoData" />
          <div v-if="gmInfoData" class="gm-info">
            <!-- <el-rate v-model="value" disabled show-score text-color="#ff9900" score-template="{value} points" /> -->
            <div v-for="(value, key) in gmInfoData.DiGraph.Edges" :key="key">
              {{ key }}: {{ value }}
            </div>
          </div>
        </el-scrollbar>
      </el-card>

    </div>

  </el-card>
</template>

<script setup>
import { ref, watch, computed } from 'vue';
import { useStore } from 'vuex';

const store = useStore();
const currentFileName = computed(() => {
  return store.state.currentPreviewFileName.replace('.svg', '');
});
const gmInfoData = computed(() => store.state.gmInfoData);
const isLoading = computed(() => store.state.loading);

const svg = `
        <path class="path" d="
          M 30 15
          L 28 17
          M 25.61 25.61
          A 15 15, 0, 0, 1, 15 30
          A 15 15, 0, 1, 1, 27.99 7.5
          L 15 15
        " style="stroke-width: 4px; fill: rgba(0, 0, 0, 0)"/>
      `
</script>

<style lang="scss">
.box-card {
  margin: 4px;
  min-height: 99vh;

  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 2vh;
  }
}

.title {
  font-weight: 900;
}

.el-card__body {
  padding: 5px;
}
</style>