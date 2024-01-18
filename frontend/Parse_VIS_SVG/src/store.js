// store.js
import { createStore } from 'vuex';

export default createStore({
  state() {
    return {
      currentPreviewFileName: null,
      gmInfoData: null, 
      loading: false,
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
  },
});
