<template>
  <el-card class="box-card" v-loading="isLoading" element-loading-text="Parseing..." :element-loading-spinner="svg"
    element-loading-svg-view-box="-10, -10, 50, 50">
    <template #header>
      <div class="card-header">
        <span style="font-size:1.2em; font-weight: 700;">CurrentSVG : {{ store.state.currentPreviewFileName }} <span
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
        <el-scrollbar height="54.1vh">
          <div style="justify-content: space-evenly;">
            <!-- <el-tooltip class="box-item" effect="dark" content="description" placement="top" v-if="gmInfoData"><el-card
                style="width: 25%; margin-right: 10px;" v-if="gmInfoData" shadow="hover"
                class="community_detection_card"><span class="card_title">basis_1</span><img :src="imageURLWithTimestamp"
                  alt="GMinfo Image" style="width: 100%;" v-if="gmInfoData" /></el-card>
            </el-tooltip> -->
            <div style="display: flex;">
              <el-card style="width: 50%; margin:3px;" shadow="hover" class="center">
                <span class="card_title">Init SVG</span><br>
                <el-empty description="No Data" :image-size="165" v-if="!gmInfoData" />
                <div v-html="selectedSvg" class="svg-container" v-if="gmInfoData"></div>
              </el-card>
              <el-card style="width: 50%; margin:3px;" shadow="hover"><span
                  class="card_title">community_detection</span><br>
                <el-empty description="No Data" :image-size="165" v-if="!gmInfoData" />
                <CommunityDetection :key="updateKey" v-if="gmInfoData" />
              </el-card>
            </div>
            <div style="display: flex; justify-content: center;">
              <el-card style="width: 100%; margin:3px;" shadow="hover" class="statistical">
                <el-scrollbar>
                  <el-empty description="No Data" :image-size="30" v-if="!gmInfoData" />
                  <div style="display: flex; margin-bottom: 3px;">
                    <span v-if="gmInfoData"><el-tag effect="plain">
                        nodes number : {{ gmInfoData.DiGraph.nodes }}</el-tag></span>
                    <span v-if="gmInfoData"><el-tag effect="plain">
                        edges number : {{ gmInfoData.DiGraph.edges }}</el-tag></span>
                    <!-- <span v-if="selectedCommunity"><el-tag effect="plain">
                        Selected community : {{ selectedCommunity }}</el-tag></span> -->
                  </div>
                  <!-- <span v-if="selectedCommunity"><el-tag effect="plain">
                      The nodes in {{ selectedCommunity }} community : {{ selectedNodeIds.join(', ') }}</el-tag></span> -->
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
        <!-- <template #content>元素比例 <br /> 横轴（元素类别）<br /> 纵：(数量/比例) <br />灰色/蓝色为不可视/可视元素</template> -->
        <el-card shadow="hover" style=" width: 18%;">
          <el-empty description="No Data" :image-size="95" v-if="!gmInfoData" />
          <HisEleProportions v-if="gmInfoData" />
        </el-card>

        <!-- <template #content> 属性比例 <br /> 横轴（元素属性）<br /> 纵：(数量/比例) <br />灰色/蓝色为不可视/可视元素</template> -->
        <el-card shadow="hover" style=" width: 52%;">
          <el-empty description="No Data" :image-size="95" v-if="!gmInfoData" />
          <div>
          <el-dropdown :hide-on-click="false">
            <span class="el-dropdown-link">
              Other<el-icon class="el-icon--right"><arrow-down /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item>fill_color</el-dropdown-item>
                <el-dropdown-item>opacity</el-dropdown-item>
                <el-dropdown-item>brightness</el-dropdown-item>
                <el-dropdown-item divided>saturation </el-dropdown-item>
                <el-dropdown-item >stroke_color</el-dropdown-item>
                <el-dropdown-item >stroke_width</el-dropdown-item>
                <el-dropdown-item divided>tag_match</el-dropdown-item>
                <el-dropdown-item >layer</el-dropdown-item>
                <el-dropdown-item >text_content</el-dropdown-item>
                <el-dropdown-item >bottom_edge</el-dropdown-item>
                <el-dropdown-item >left_edge</el-dropdown-item>
                <el-dropdown-item >right_edge</el-dropdown-item>
                <el-dropdown-item >area</el-dropdown-item>
                <el-dropdown-item >overlap_ratio</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
          <HisAttrProportionsVue v-if="gmInfoData" />
        </div>
        </el-card>

        <!-- <el-tooltip placement="top">
            <template #content v-if="!changebbox"> 定界框 <br /> 横轴（元素位置）<br /> 纵：(数量/比例) <br />灰色/蓝色为不可视/可视元素 <br />点击切换为网格视图</template>
            <template #content v-if="changebbox"> 定界框 <br /> 横轴（元素位置）<br /> 纵：(数量/比例) <br />灰色/蓝色为不可视/可视元素 <br />点击切换为直方视图</template>
            <el-card shadow="hover" style=" width: 25%; position: relative;" @click="changebbox = !changebbox">
              <HisBbox v-if="!changebbox" />
              <img :src="imageURLWithTimestamp" alt="GMinfo Image"
                style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; width: 100%;" v-if="changebbox" />
            </el-card>
          </el-tooltip> -->

        <!-- <template #content> 社区散点（当前） ⇄ 社区直方<br /> 横轴（社区编号）<br /> 纵：(社区大小) <br />灰色/蓝色为不可视/可视元素</template>-->
        <!-- <template #content v-if="!changeSH"> 社区直方（当前） ⇄ 社区散点 <br /> 横轴（社区编号）<br /> 纵：(社区强度)
              <br />灰色/蓝色为不可视/可视元素</template> -->
        <el-card shadow="hover" style=" width: 28%;">
          <el-empty description="No Data" :image-size="95" v-if="!gmInfoData" />
          <ScatCommunity v-if="gmInfoData" />
          <!-- <HisCommunity v-if="!changeSH" /> -->
        </el-card>
      </el-card>

    </div>

  </el-card>
</template>

<script setup>
import { ref, watch, computed } from 'vue';
import { useStore } from 'vuex';
import CommunityDetection from './Community-Detection.vue';
import HisEleProportions from './His-EleProportions.vue';
import HisAttrProportionsVue from './His-AttrProportions.vue';
import HisBbox from './His-bbox.vue';
import ScatCommunity from './Scat-community.vue';
import HisCommunity from './His-community.vue';
import { ArrowDown } from '@element-plus/icons-vue'

const changeSH = ref(true)
const changebbox = ref(true)
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
  height: 44vh;
  width: 100%;

  svg {
    width: 100% !important;
    height: 100% !important;
    object-fit: contain !important;
  }
}

.fourSVG-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 10vh;
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

  .el-card__body {
    padding: 5px !important;
  }
}

.statistical {
  font-size: 1em;
  ;
  font-weight: 900;

  span {
    margin-right: 5px;
  }
}

.box-card-result {
  .el-card__body {
    padding: 8px !important;
    height: 100%;
    display: flex;
    justify-content: space-around;
  }
}
.example-showcase .el-dropdown + .el-dropdown {
  margin-left: 15px;
}
.example-showcase .el-dropdown-link {
  cursor: pointer;
  color: var(--el-color-primary);
  display: flex;
  align-items: center;
}
</style>