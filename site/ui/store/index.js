import Vue from 'vue';
import Vuex from 'vuex';
import state from './state';
import mutations from './mutations';
import actions from './actions';
Vue.use(Vuex);

export default new Vuex.Store({
  strict: process.env.NODE_ENV !== 'production', // strict mode is only for development
  state: state,
  getters: {
    getOptions: () => {
      return state.options;
    },
    getSelectedFeatures: () => {
      return state.selectedFeatures;
    },
    getDownloadRadios: () => {
      return state.downloadRadios;
    },
  },
  mutations: mutations,
  actions: actions,
});
