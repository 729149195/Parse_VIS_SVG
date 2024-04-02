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
        <el-scrollbar height="53.47vh">
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
              <el-card style="width: 50%; margin:3px;" shadow="hover"><span class="card_title">community_detection
                  <el-icon style="position: relative; top:0.2em; cursor: pointer;" @click="refresh">
                    <Refresh />
                  </el-icon></span><br>
                <el-empty description="No Data" :image-size="165" v-if="!gmInfoData" />
                <!-- <CommunityDetection :key="updateKey" v-if="gmInfoData" /> -->
                <CommunityDetectionMult :key="updateKey" v-if="gmInfoData" />
              </el-card>
            </div>
            <div style="display: flex; justify-content: center;">
              <el-card style="width: 100%; margin:2px;" shadow="hover" class="statistical">
                <el-scrollbar>
                  <el-empty description="No Data" :image-size="30" v-if="!gmInfoData" />
                  <div style="display: flex; margin-bottom: 2px;">
                    <span v-if="gmInfoData"><el-tag effect="plain">
                        nodes number : {{ gmInfoData.DiGraph.nodes }}</el-tag></span>
                    <span v-if="gmInfoData"><el-tag effect="plain">
                        edges number : {{ gmInfoData.DiGraph.edges }}</el-tag></span>
                    <span v-if="selectedCommunity"><el-tag effect="plain">
                        Selected community : {{ selectedCommunity }}</el-tag></span>
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
        <el-card shadow="hover" style=" width: 18%;">
          <el-empty description="No Data" :image-size="95" v-if="!gmInfoData" />
          <HisEleProportions v-if="gmInfoData" />
        </el-card>

        <el-card shadow="hover" style=" width: 52%;">
          <el-empty description="No Data" :image-size="95" v-if="!gmInfoData" />
          <div>
            <el-cascader v-model="value_cascader" :options="options_cascader" @change="handleChange_cascader"
              v-if="gmInfoData" />
              <div v-if="gmInfoData">
                <FillStatistician v-show="is_fill"/>
                <strokeStatistician v-show="is_stroke"/>
                <span v-show="is_top">is_top</span>
                <span v-show="is_bottom">is_bottom</span>
                <span v-show="is_left">is_left</span>
                <span v-show="is_right">is_right</span>
                <span v-show="is_layer">is_layer</span>
                <span v-show="is_similarity">is_similarity</span>
                <HisAttrProportionsVue v-show="is_aLLattrNumber"/>
              </div>
          </div>
        </el-card>

        <el-card shadow="hover" style=" width: 28%;">
          <el-empty description="No Data" :image-size="95" v-if="!gmInfoData" />
          <ScatCommunity v-if="gmInfoData" />
        </el-card>
      </el-card>
    </div>
  </el-card>
</template>

<script setup>
import { ref, watch, computed, onMounted } from 'vue';
import { useStore } from 'vuex';
import CommunityDetection from './Community-Detection.vue';
import CommunityDetectionMult from './Community-Detection-Mult.vue';
import HisEleProportions from './His-EleProportions.vue';
import HisAttrProportionsVue from './Statisticians/His-AttrProportions.vue';
import FillStatistician from './Statisticians/Fill-Statistician.vue';
import strokeStatistician from './Statisticians/stroke-Statistician.vue';
import topStatistician from './Statisticians/top-Statistician.vue';
import bottomStatistician from './Statisticians/bottom-Statistician.vue';
import leftStatistician from './Statisticians/left-Statistician.vue';
import rightStatistician from './Statisticians/right-Statistician.vue';
import layerStatistician from './Statisticians/layer-Statistician.vue';
import similarityStatistician from './Statisticians/similarity-Statistician.vue';
import ScatCommunity from './Scat-community.vue';

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

const value_cascader = ref([])
const select_cascader = ref('a')

const is_fill = ref(select_cascader.value === 'fill')
const is_stroke = ref(select_cascader.value === 'stroke')
const is_top = ref(select_cascader.value === 'top')
const is_bottom = ref(select_cascader.value === 'bottom')
const is_left = ref(select_cascader.value === 'left')
const is_right = ref(select_cascader.value === 'right')
const is_layer = ref(select_cascader.value === 'layer')
const is_similarity = ref(select_cascader.value === 'similarity')
const is_aLLattrNumber = ref(select_cascader.value === 'aLLattrNumber')


const handleChange_cascader = (value) => {
  select_cascader.value = value[value.length - 1]
  console.log(select_cascader.value)
}

onMounted(() =>{
  value_cascader.value = ['aLLattrNumber']
  select_cascader.value = 'aLLattrNumber'
})

watch(select_cascader, ()=>{
  is_fill.value = select_cascader.value === 'fill'
  is_stroke.value = select_cascader.value ==='stroke'
  is_top.value = select_cascader.value === 'top'
  is_bottom.value = select_cascader.value === 'bottom'
  is_left.value = select_cascader.value === 'left'
  is_right.value = select_cascader.value === 'right'
  is_layer.value = select_cascader.value === 'layer'
  is_similarity.value = select_cascader.value ==='similarity'
  is_aLLattrNumber.value = select_cascader.value === 'aLLattrNumber'
})

const options_cascader = [
  {
    value: 'color',
    label: 'Color',
    children: [
      {
        value: 'fill',
        label: 'Fill'
      },
      {
        value: 'stroke',
        label: 'Stroke'
      }
    ]
  },
  {
    value: 'edge',
    label: 'Edge',
    children: [
      {
        value: 'top',
        label: 'Top'
      },
      {
        value: 'bottom',
        label: 'Bottom'
      },
      {
        value: 'left',
        label: 'Left'
      },
      {
        value: 'right',
        label: 'Right'
      }
    ]
  },
  {
    value: 'layer',
    label: 'Layer'
  },
  {
    value: 'similarity',
    label: 'Similarity'
  },
  {
    value: 'aLLattrNumber',
    label: 'ALLattrNumber'
  }
]

watch(selectedNodeIds, () => {
  const svgContainer = document.querySelector('.svg-container');
  if (!svgContainer) return;

  const svg = svgContainer.querySelector('svg');
  if (!svg) return;
  svg.querySelectorAll('*').forEach(node => {
    node.style.opacity = '';
  });

  svg.querySelectorAll('*').forEach(node => {
    if (allVisiableNodes.value.includes(node.id) && !selectedNodeIds.value.includes(node.id)) {
      node.style.opacity = '0.05'; 
    }
  });
});

const refresh = () => {
  const svgContainer = document.querySelector('.svg-container');
  const svg = svgContainer.querySelector('svg');
  svg.querySelectorAll('*').forEach(node => {
    node.style.opacity = '1';
  })
}

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

.example-showcase .el-dropdown+.el-dropdown {
  margin-left: 15px;
}

.example-showcase .el-dropdown-link {
  cursor: pointer;
  color: var(--el-color-primary);
  display: flex;
  align-items: center;
}
</style>