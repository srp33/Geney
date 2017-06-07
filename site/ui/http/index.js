import Vue from 'vue'
import VueResource from 'vue-resource'
Vue.use(VueResource)

Vue.http.interceptors.push((request, next) => {
  let jwt = localStorage.getItem('jwt')
  if (jwt) {
    request.headers.set('Authorization', 'Bearer ' + jwt)
  }
  next((response) => {
    if (typeof response.data === 'object' && response.data.jwt) {
      localStorage.setItem('jwt', response.data.jwt)
      console.log(Vue.store)
    }
  })
})
