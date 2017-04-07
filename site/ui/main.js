// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App'
import router from './router'
import store from './store'

import VueResource from 'vue-resource'
Vue.use(VueResource)

// load jQuery and Bootstrap (js and less)
import jQuery from 'jquery'
global.jQuery = jQuery
import 'bootstrap'
import 'bootstrap/less/bootstrap.less'
import 'selectize/dist/css/selectize.bootstrap3.css'
import 'font-awesome-webpack'
import 'simplemde/dist/simplemde.min.css'

/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  store,
  template: '<App/>',
  components: { App }
})
