import Vue from 'vue';
import Vuex from 'vuex';
import state from './state';
import mutations from './mutations';
import actions from './actions';
Vue.use(Vuex);

export default new Vuex.Store({
  strict: process.env.NODE_ENV !== 'production', // strict mode is only for development
  state: state,
  mutations: mutations,
  actions: actions,
});
