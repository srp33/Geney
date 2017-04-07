import Vue from 'vue'
import Vuex from 'vuex'
import router from '../router'
Vue.use(Vuex)

export default new Vuex.Store({
  strict: process.env.NODE_ENV !== 'production', // strict mode is only for development
  state: {
    metaData: null,
    datasets: null,
    dataset: {},
    filters: null,
    datasetName: null,
    user: null
  },
  mutations: {
    metaData (state, value) {
      state.metaData = value
    },
    filters (state, value) {
      state.filters = value
    },
    datasets (state, value) {
      state.datasets = value
    },
    dataset (state, value) {
      state.dataset = value
    },
    user (state, value) {
      state.user = value
    }
  },
  actions: {
    getDatasets (context) {
      Vue.http.get('/api/datasets').then(response => {
        context.commit('datasets', response.data)
        if (router.currentRoute.params.dataset) {
          var id = router.currentRoute.params.dataset
          var dataset = {}
          for (var x of response.data) {
            if (x.id === id) {
              dataset = x
              break
            }
          }
          context.dispatch('setDataset', dataset)
        }
      }, response => {
        context.commit('datasets', [])
      })
    },
    getMetadata (context) {
      if (context.state.dataset) {
        // check if current metaData is the one we need right now
        if (context.state.metaData && context.state.metaData.dataset === context.state.dataset.id) {
          return
        }
        // see if there is a dataset
        if (!context.state.dataset.id) {
          return
        }
        context.commit('metaData', false)
        // check if localStorage is available on the browser
        if (window.localStorage) {
          // try to get the meta out of local storage
          try {
            var data = JSON.parse(window.localStorage.getItem(context.state.dataset + '_data'))
          } catch (e) {
            console.error('Error retrieving local storage:', e)
            // if it fails (for whatever reason) clear local storage so we can
            // make the http request and set it again
            window.localStorage.clear()
          }
          // if we were able to get the stored data, return a promise that
          // immediately resolves with the data we found
          if (data) {
            context.commit('metaData', data)
          }
        }
        Vue.http.get('/api/meta/' + context.state.dataset.id).then(response => {
          for (var key in response.data.meta) {
            response.data.meta[key] = response.data.meta[key].map(x => ({
              'name': x
            }))
          }
          response.data.genes = response.data.genes.map(x => ({
            'name': x
          }))
          response.data.dataset = context.state.dataset.id
          // window.localStorage.setItem(context.state.dataset + '_data', JSON.stringify(response.data))
          context.commit('metaData', response.data)
        }, response => {
          console.log('FAILED', response)
          router.replace('/404')
        })
      }
    },
    setDataset (context, payload) {
      console.log(payload)
      context.commit('dataset', payload)
      if (payload.id) {
        context.dispatch('getMetadata')
      } else {
        if (router.currentRoute.params.dataset) {
          router.replace('/404')
        }
      }
    },
    login (context, data) {
      if (context.state.user !== null) {
        throw Error('Cannot login while user is not null!')
      }
      Vue.http.post('/auth/login', {
        username: data.username,
        password: data.password
      }).then(response => {
        console.log(response)
        if (response.data.jwt) {
          localStorage.setItem('jwt', response.data.jwt)
          context.dispatch('getUser', data.callback)
        } else {
          data.callback(false)
        }
      }, response => {
        console.error('Login failed: ', response)
        data.callback(null)
      })
    },
    logout (context) {
      localStorage.removeItem('jwt')
      context.commit('user', null)
    },
    getUser (context, callback) {
      let user = null
      if (context.state.user === null) {
        let jwt = localStorage.getItem('jwt')
        console.log(typeof jwt)
        if (jwt) {
          jwt = jwt.split('.')
          let headers = JSON.parse(atob(jwt[0]))
          if (headers.alg === 'HS512' && headers.typ === 'JWT') {
            user = JSON.parse(atob(jwt[1]))
            context.commit('user', user)
          }
        }
      } else {
        user = context.state.user
      }
      if (user && user.exp < (Date.now() / 1000)) {
        localStorage.removeItem('jwt')
        user = null
        context.commit('user', user)
      }
      if (callback) {
        callback(user)
      }
    }
  }
})
