<template>
  <el-card class="box-card" v-loading="isLoading" element-loading-text="Parseing..." :element-loading-spinner="svg"
    element-loading-svg-view-box="-10, -10, 50, 50">
    <template #header>
      <div class="card-header">
        <span style="font-size:1.3em; font-weight: 700;">CurrentSVG : {{ store.state.currentPreviewFileName }} <span
            v-if="!gmInfoData">Not
            uploaded or not selected</span></span>
        <el-button v-if="gmInfoData" class="button" type="primary" plain><span
            style="margin-right: 3px;">导出</span><el-icon style="margin-right: -4px;">
            <Download />
          </el-icon></el-button>
      </div>
    </template>
    <div class="card-body">

      <el-icon>
        <Finished />
      </el-icon>
      <span style="font-size:1.1em; font-weight: 700;"> Perception process and basis :</span>
      <!-- 分析过程卡片 -->
      <el-card class="box-card-process" shadow="hover">
        <el-scrollbar height="54vh">
          <el-empty description="No Data" :image-size="100" v-if="!gmInfoData" />
          <div style="justify-content: space-evenly;" v-if="gmInfoData">
            <!-- <el-tooltip class="box-item" effect="dark" content="description" placement="top" v-if="gmInfoData"><el-card
                style="width: 25%; margin-right: 10px;" v-if="gmInfoData" shadow="hover"
                class="community_detection_card"><span class="card_title">basis_1</span><img :src="imageURLWithTimestamp"
                  alt="GMinfo Image" style="width: 100%;" v-if="gmInfoData" /></el-card>
            </el-tooltip> -->
            <div style="display: flex;">
              <el-card style="width: 50%; margin:5px;" shadow="hover" class="center">
                <span class="card_title">Init SVG</span><br>
                <div v-html="selectedSvg" class="svg-container"></div>
              </el-card>
              <el-card style="width: 50%; margin:5px;" shadow="hover"><span
                  class="card_title">community_detection</span><br>
                <CommunityDetection :key="updateKey" />
              </el-card>
            </div>
            <div style="display: flex; justify-content: center;">
              <el-card style="width: 99%; " shadow="hover">
                <el-scrollbar>
                  <div style="display: flex; margin-bottom: 5px;">
                    <span v-if="gmInfoData"><el-tag effect="plain" style="font-size: 1em; margin-right: 10px;">
                        nodes-num : {{ gmInfoData.DiGraph.nodes }}</el-tag></span>
                    <span v-if="gmInfoData"><el-tag effect="plain" style="font-size: 1em; margin-right: 10px;">
                        edges-num : {{ gmInfoData.DiGraph.edges }}</el-tag></span>
                    <span v-if="gmInfoData"><el-tag effect="plain" style="font-size: 1em; margin-right: 10px;">
                        Selected community : {{ selectedCommunity }}</el-tag></span>
                  </div>
                  <span v-if="gmInfoData"><el-tag effect="plain" style="font-size: 1em; margin-right: 10px;">
                      The nodes in this community : {{ selectedNodeIds.join(', ') }}</el-tag></span>
                </el-scrollbar>
              </el-card>
            </div>
          </div>

        </el-scrollbar>
      </el-card>
      <el-icon>
        <Odometer />
      </el-icon>
      <span style="font-size:1.1em; font-weight: 700;;"> Perceived results and recommendations :</span>
      <!-- 结果卡片 -->
      <el-card class="box-card-result" shadow="hover">
        <el-scrollbar height="20vh" style="display: flex; justify-content: center; align-items: center;">
          <el-empty description="No Data" :image-size="60" v-if="!gmInfoData" />
          <div style="display: flex; justify-content: center;"><el-card v-if="gmInfoData" shadow="hover"
              style=" width: 24%; padding: 0 !important; margin-right: 10px;">
              <span class="card_title">直方图1：元素比例 横（元素类别）纵：(比例)</span><br>
            </el-card>
            <el-card v-if="gmInfoData" shadow="hover" style=" width: 24%; padding: 0 !important; margin-right: 10px;">
              <span class="card_title">直方图2：属性比例（缺省）</span><br>
            </el-card>
            <el-card v-if="gmInfoData" shadow="hover" style=" width: 24%; padding: 0 !important; margin-right: 10px;">
              <span class="card_title">直方图3：bbox（缺省）</span><br>
            </el-card>
            <el-card v-if="gmInfoData" shadow="hover" style=" width: 24%; padding: 0 !important;">
              <span class="card_title">散点图+一组直方图：横（数量/大小）纵：(内、外强度)</span><br>
            </el-card>
          </div>
        </el-scrollbar>
      </el-card>

    </div>

  </el-card>
</template>

<script setup>
import { ref, watch, computed } from 'vue';
import { useStore } from 'vuex';
import CommunityDetection from './Community-Detection.vue';

const community_dialogVisible = ref(false)
const community_and_initsvg_dialogVisible = ref(false)
const store = useStore();
const updateKey = ref(0);
const gmInfoData = computed(() => store.state.gmInfoData);
const isLoading = computed(() => store.state.loading);
const selectedSvg = computed(() => store.state.selectedSvg);
const selectedCommunity = computed(() => store.state.selectedNodes.group);
const selectedNodeIds = computed(() => store.state.selectedNodes.nodeIds);
const allVisiableNodes = computed(() => store.state.AllVisiableNodes);
const baseURL = "http://localhost:8000/static/GMinfo.png";
const lastUpdate = ref(new Date().getTime());

watch(selectedNodeIds, () => {
  const svgContainer = document.querySelector('.svg-container');
  if (!svgContainer) return;

  const svg = svgContainer.querySelector('svg');
  if (!svg) return;
  // 首先重置所有节点的透明度
  svg.querySelectorAll('*').forEach(node => {
    node.style.opacity = '';
  });

  // 调整不在 allVisiableNodes 中的节点的透明度
  svg.querySelectorAll('*').forEach(node => {
    if (allVisiableNodes.value.includes(node.id) && !selectedNodeIds.value.includes(node.id)) {
      node.style.opacity = '0.05'; // 调整透明度
    }
  });
});

const refreshComponent = () => {
  updateKey.value++;
};


watch(community_dialogVisible, (newValue) => {
  if (newValue) {
    refreshComponent(); // 当对话框打开时，刷新组件
  }
});

watch(community_and_initsvg_dialogVisible, (newValue) => {
  if (newValue) {
    refreshComponent(); // 当对话框打开时，刷新组件
  }
});


// const currentFileName = computed(() => {
//   if (store.state.currentPreviewFileName)
//     return store.state.currentPreviewFileName.replace('.svg', '');
// });


const imageURLWithTimestamp = computed(() => {
  return `${baseURL}?t=${lastUpdate.value}`;
});

const updateImage = () => {
  lastUpdate.value = new Date().getTime();  // 更新时间戳
};

watch(gmInfoData, () => {
  updateImage();  // 当 gmInfoData 改变时调用 updateImage
});

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

.el-button {
  margin-left: 8px;
}

.community_detection_card {
  cursor: pointer;

  .el-card__body {
    padding: 0 !important;
  }
}

.card_title {
  padding-left: 8px;
  color: #999;
}

.green {
  color: var(--el-color-success);
}

.red {
  color: var(--el-color-error);
}

.report-tabs>.el-tabs__content {
  padding: 5px;
}

.svg-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 33vh;
  width: 100%;

  svg {
    width: 100% !important;
    height: 100% !important;
    object-fit: contain !important;
  }
}

.center {
  .el-card__body {
    height: 100%;
    width: 100%;
  }
}

.box-card-process {
  margin-bottom: 5px;
}
</style>