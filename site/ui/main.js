// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App'
import router from './router'
import store from './store'
import validator from './validator'
import './http'

import BootstrapVue from 'bootstrap-vue'
Vue.use(BootstrapVue)

import VueMasonryPlugin from 'vue-masonry'
Vue.use(VueMasonryPlugin)

// load jQuery and Bootstrap (js and less)
import jQuery from 'jquery'
global.jQuery = jQuery
import 'bootstrap/scss/bootstrap.scss'
import 'selectize/dist/css/selectize.bootstrap3.css'
import 'font-awesome-webpack'
import 'simplemde/dist/simplemde.min.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'

/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  store,
  validator,
  template: '<App/>',
  components: { App }
})
