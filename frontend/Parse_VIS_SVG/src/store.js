import { createStore } from 'vuex';

export default createStore({
  state() {
    return {
      currentPreviewFileName: null,
      gmInfoData: null, 
      loading: false,
      selectedSvg: null,
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
  },
});
