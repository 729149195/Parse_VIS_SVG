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
    setSelectedSvg(state, svgUrl) {
      state.selectedSvg = svgUrl;
    },
    UPDATE_SELECTED_NODES(state, payload) {
      state.selectedNodes.nodeIds = payload.nodeIds;
      state.selectedNodes.group = payload.group;
  },
  },
});
