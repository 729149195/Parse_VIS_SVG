import { createStore } from 'vuex';

export default createStore({
  state() {
    return {
      currentPreviewFileName: null,
      gmInfoData: null,
      loading: false,
      selectedSvg: null,
      selectedNodes: {
        nodeIds: [],
        group: null
      },
      AllVisiableNodes: [],
      ele_num_data : null
    };
  },
  mutations: {
    setCurrentPreviewFileName(state, filename) {
      state.currentPreviewFileName = filename;
    },
    setGMInfoData(state, data) {
      state.gmInfoData = data;
    },
    setLoading(state, isLoading) {
      state.loading = isLoading;
    },
    setSelectedSvg(state, svgContent) {
      state.selectedSvg = svgContent;
    },
    UPDATE_SELECTED_NODES(state, payload) {
      // console.log("Payload received:", payload.nodeIds);
      state.selectedNodes.nodeIds = payload.nodeIds;
      state.selectedNodes.group = payload.group;
    },
    SET_ALL_VISIBLE_NODES(state, nodeIds) {
      state.AllVisiableNodes = nodeIds;
    },
    GET_ELE_NUM_DATA(state, data) {
      state.ele_num_data = data;
    }
  },
});
