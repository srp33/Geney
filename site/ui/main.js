// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App'
import router from './router'
import store from './store'
import validator from './validator'
import './http'
import BootstrapVue from 'bootstrap-vue'
import VueMasonryPlugin from 'vue-masonry'
// load jQuery and Bootstrap (js and less)
import jQuery from 'jquery'
import './styles/main.scss'
import 'font-awesome-webpack'

global.jQuery = jQuery
Vue.use(VueMasonryPlugin)
Vue.use(BootstrapVue)
/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  store,
  validator,
  template: '<App/>',
  components: { App }
})
