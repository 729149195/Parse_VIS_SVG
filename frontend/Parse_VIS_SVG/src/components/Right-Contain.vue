<template>
  <el-card class="box-card" v-loading="isLoading" element-loading-text="Parseing..." :element-loading-spinner="svg"
    element-loading-svg-view-box="-10, -10, 50, 50">
    <template #header>
      <div class="card-header">
        <span style="font-size:1.3em; font-weight: 700;">CurrentFile : {{ currentFileName }} <span v-if="!gmInfoData">Not
            uploaded or not selected</span></span>
        <div>
          <span v-if="gmInfoData"><el-tag effect="plain" style="font-size: 1em; margin-right: 10px;">nodes-num : {{
            gmInfoData.DiGraph.nodes }}</el-tag></span>
          <span v-if="gmInfoData"><el-tag effect="plain" style="font-size: 1em;">edges-num : {{
            gmInfoData.DiGraph.edges }}</el-tag></span>
        </div>
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
        <el-scrollbar height="29vh">
          <div style="display: flex; justify-content: space-evenly;">
            <el-tooltip class="box-item" effect="dark" content="description" placement="top" v-if="gmInfoData"><el-card
                style="width: 25%; margin-right: 10px;" v-if="gmInfoData" shadow="hover"
                class="community_detection_card"><span class="card_title">basis_1</span><img :src="imageURLWithTimestamp"
                  alt="GMinfo Image" style="width: 100%;" v-if="gmInfoData" /></el-card>
            </el-tooltip>

            <el-tooltip class="box-item" effect="dark" content="Click to enlarge the svg" placement="top"
              v-if="gmInfoData"><el-card style=" width: 25%; padding: 0 !important; margin-right: 10px;" v-if="gmInfoData"
                shadow="hover" @Click="community_dialogVisible = true" class="community_detection_card"><span
                  class="card_title">community_detection</span>
                <CommunityDetection />
              </el-card>
            </el-tooltip>
            <el-tooltip class="box-item" effect="dark" content="description" placement="top" v-if="gmInfoData"><el-card
                style="width: 50%;  margin-right: 10px; display: flex; justify-content: center; align-items: center;"
                v-if="gmInfoData" shadow="hover" @Click="community_and_initsvg_dialogVisible = true"
                class="community_detection_card"><el-icon size="50px">
                  <Histogram />
                </el-icon><el-icon size="35px">
                  <Ticket />
                </el-icon></el-card>
            </el-tooltip>

            <el-dialog v-model="community_dialogVisible" style="padding: 0 !important;">
              <CommunityDetection :key="updateKey" />
            </el-dialog>

            <el-dialog v-model="community_and_initsvg_dialogVisible" style="padding: 0 !important; width: 90%;"
              title="Community counterpart element">
              <!-- 功能实现处 -->
              <div style="display: flex;">
                <el-card style="width: 50%; margin: 5px;" shadow="never" class="center"><span class="card_title" >Init SVG</span><br>
                  <div v-html="selectedSvg" class="svg-container"></div>
                </el-card>
                <el-card style="width: 50%; margin: 5px;" shadow="never"><span
                    class="card_title">community_detection</span><br>
                  <CommunityDetection :key="updateKey" />
                </el-card>
              </div>


            </el-dialog>
          </div>
          <el-empty description="No Data" :image-size="150" v-if="!gmInfoData" />
        </el-scrollbar>
      </el-card>
      <el-icon>
        <Odometer />
      </el-icon>
      <span style="font-size:1.1em; font-weight: 700; padding-top: 15px;"> Perceived results and recommendations :</span>
      <!-- 结果卡片 -->
      <el-card class="box-card-result" shadow="hover">
        <el-scrollbar height="42vh">
          <div v-if="gmInfoData" style="margin-bottom: 10px;">
            <el-input v-model="Expected_pattern" style="width: 90%; " placeholder="Please input Your expected pattern" />
            <el-button type="primary" style="width: 9%;" @click="perceive = !perceive">perceive</el-button>
          </div>
          <el-empty description="No Data" :image-size="150" v-if="!gmInfoData" />
          <span class="result_title" v-if="gmInfoData">Quantitative evaluation <span v-if="perceive">{{ Expected_pattern
          }}</span></span>
          <el-card v-if="gmInfoData" shadow="hover">

            <el-row :gutter="10" style="margin-left: 20px;margin-right: 20px;justify-content: space-around;">
              <el-col :span="4">
                <div class="statistic-card">
                  <el-statistic :value="gmInfoData.DiGraph.nodes
                    ">
                    <template #title>
                      <div style="display: inline-flex; align-items: center">
                        Clarity
                        <el-tooltip effect="dark" content="评估信息是否易于理解，图表中的数据点是否清晰（改善图表的布局、标签或图例以增加清晰度）" placement="top">
                          <el-icon style="margin-left: 4px" :size="12">
                            <Warning />
                          </el-icon>
                        </el-tooltip>
                      </div>
                    </template>
                  </el-statistic>
                  <div class="statistic-footer">
                    <div class="footer-item">
                      <el-rate v-model="value1" disabled show-score text-color="#ff9900" score-template="{value}star"
                        size="small" />
                    </div>
                  </div>
                </div>
              </el-col>
              <!-- <el-col :span="4">
                <div class="statistic-card">
                  <el-statistic :value="gmInfoData.DiGraph.edges * 11">
                    <template #title>
                      <div style="display: inline-flex; align-items: center">
                        Aesthetics
                        <el-tooltip effect="dark" content="评价图表的视觉吸引力和专业性（提供样式模板或颜色方案的选择）" placement="top">
                          <el-icon style="margin-left: 4px" :size="12">
                            <Warning />
                          </el-icon>
                        </el-tooltip>
                      </div>
                    </template>
                  </el-statistic>
                  <div class="statistic-footer">
                    <div class="footer-item">
                      <el-rate v-model="value2" disabled show-score text-color="#ff9900" score-template="{value}star"
                        size="small" />
                    </div>
                  </div>
                </div>
              </el-col> -->
              <el-col :span="4">
                <div class="statistic-card">
                  <el-statistic :value="gmInfoData.DiGraph.nodes * 113">
                    <template #title>
                      <div style="display: inline-flex; align-items: center">
                        Accuracy
                        <el-tooltip effect="dark" content="确保图表准确地表示数据，没有误导性的视觉元素（强调数据表示的改进，如调整比例、尺度或数据映射）"
                          placement="top">
                          <el-icon style="margin-left: 4px" :size="12">
                            <Warning />
                          </el-icon>
                        </el-tooltip>
                      </div>
                    </template>
                  </el-statistic>
                  <div class="statistic-footer">
                    <div class="footer-item">
                      <el-rate v-model="value3" disabled show-score text-color="#ff9900" score-template="{value}star"
                        size="small" />
                    </div>
                  </div>
                </div>
              </el-col>
              <el-col :span="4">
                <div class="statistic-card">
                  <el-statistic :value="gmInfoData.DiGraph.nodes * 43">
                    <template #title>
                      <div style="display: inline-flex; align-items: center">
                        Efficiency
                        <el-tooltip effect="dark" content="评估从图表中提取信息所需的时间和努力（建议调整图表类型或数据组织方式以提高阅读效率）" placement="top">
                          <el-icon style="margin-left: 4px" :size="12">
                            <Warning />
                          </el-icon>
                        </el-tooltip>
                      </div>
                    </template>
                  </el-statistic>
                  <div class="statistic-footer">
                    <div class="footer-item">
                      <el-rate v-model="value4" disabled show-score text-color="#ff9900" score-template="{value}star"
                        size="small" />
                    </div>
                  </div>
                </div>
              </el-col>
              <!-- <el-col :span="4">
                <div class="statistic-card">
                  <el-statistic :value="gmInfoData.DiGraph.nodes * 3">
                    <template #title>
                      <div style="display: inline-flex; align-items: center">
                        Accessibility
                        <el-tooltip effect="dark" content="确保图表对色盲用户或有视觉障碍的用户友好（文本反馈和工具提示，提供改善颜色对比度、添加替代文本的建议）"
                          placement="top">
                          <el-icon style="margin-left: 4px" :size="12">
                            <Warning />
                          </el-icon>
                        </el-tooltip>
                      </div>
                    </template>
                  </el-statistic>
                  <div class="statistic-footer">
                    <div class="footer-item">
                      <el-rate v-model="value5" disabled show-score text-color="#ff9900" score-template="{value}star"
                        size="small" />
                    </div>
                  </div>
                </div>
              </el-col> -->

            </el-row>
          </el-card>
          <span class="result_title" v-if="gmInfoData">Recommendations for improvement <span v-if="perceive">{{
            Expected_pattern }}</span></span>
          <el-card v-if="gmInfoData" shadow="hover">
            <el-button type="primary" style="width: 70%; height: 50px;" @click="report_dialogVisible = true">Interactive
              report</el-button>
            <el-button type="primary" style="width: 28%; height: 50px;">Case Studies & Examples</el-button>
            <el-dialog v-model="report_dialogVisible" title="Report on modifications to the dimensions" max-height="80vh"
              width="70vw">

              <el-tabs v-model="activeName" class="report-tabs">
                <el-scrollbar height="36vh">
                  <el-tab-pane label="Overview" name="first">Overview</el-tab-pane>
                  <el-tab-pane label="Clarity" name="second">Clarity</el-tab-pane>
                  <!-- <el-tab-pane label="Aesthetics" name="third">Aesthetics</el-tab-pane> -->
                  <el-tab-pane label="Accuracy" name="fourth">Accuracy</el-tab-pane>
                  <el-tab-pane label="Efficiency" name="fifth">Efficiency</el-tab-pane>
                  <!-- <el-tab-pane label="Accessibility" name="sixth">Accessibility</el-tab-pane> -->
                </el-scrollbar>
              </el-tabs>

            </el-dialog>
          </el-card>
        </el-scrollbar>
      </el-card>

    </div>

  </el-card>
</template>

<script setup>
import { ref, watch, computed } from 'vue';
import { useStore } from 'vuex';
import CommunityDetection from './Community-Detection.vue';
import { Warning } from '@element-plus/icons-vue';

const value1 = ref(1.2)
// const value2 = ref(4.7)
const value3 = ref(0.7)
const value4 = ref(3.7)
// const value5 = ref(2.7)
const perceive = ref(false);
const activeName = ref('first')
const community_dialogVisible = ref(false)
const community_and_initsvg_dialogVisible = ref(false)
const report_dialogVisible = ref(false)
const Expected_pattern = ref('')
const store = useStore();
const updateKey = ref(0);
const gmInfoData = computed(() => store.state.gmInfoData);
const isLoading = computed(() => store.state.loading);
const selectedSvg = computed(() => store.state.selectedSvg);
const baseURL = "http://localhost:8000/static/GMinfo.png";
const lastUpdate = ref(new Date().getTime());

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


const currentFileName = computed(() => {
  if (store.state.currentPreviewFileName)
    return store.state.currentPreviewFileName.replace('.svg', '');
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
.result_title {
  font-size: 16px;
  font-weight: 800;
  color: #666;
}

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


.el-statistic {
  --el-statistic-content-font-size: 28px;
}

.statistic-card {
  height: 100%;
  padding: 10px;
  border-radius: 4px;
}

.statistic-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  font-size: 12px;
  color: var(--el-text-color-regular);
  margin-top: 16px;
}

.statistic-footer .footer-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.statistic-footer .footer-item span:last-child {
  display: inline-flex;
  align-items: center;
  margin-left: 4px;
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

.svg-container  {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 90%;
  width: 100%;
  svg{
    width: 100% !important; /* 最大宽度为容器宽度 */
    height: 100% !important;
    object-fit: contain !important; /* 保持比例 */
  }
}

.center{
  .el-card__body{
    height: 100%;
    width: 100%;
  }
}
</style>