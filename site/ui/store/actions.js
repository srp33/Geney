import Vue from 'vue';
import router from '../router';

export default {
  getDatasets (context) {
    Vue.http.get('/api/datasets').then(response => {
      const datasets = response.data;
      for (let datasetId in datasets) {
        datasets[datasetId].id = datasetId;
        if (!datasets[datasetId].featureDescription) {
          datasets[datasetId].featureDescriptionPlural = 'features';
          datasets[datasetId].featureDescription = 'feature';
        }
      }
      context.commit('datasets', datasets);
      if (router.currentRoute.params.dataset) {
        const id = router.currentRoute.params.dataset;
        let dataset = datasets[id] || {};
        context.dispatch('setDataset', dataset);
      }
    }, response => {
      context.commit('datasets', []);
    });
  },
  getDatasetMetadata (context) {
    if (context.state.dataset) {
      // check if current metaData is the one we need right now
      if (context.state.metaData && context.state.metaData.dataset === context.state.dataset.id) {
        return;
      }
      // see if there is a dataset
      if (!context.state.dataset.id) {
        return;
      }
      context.commit('metaData', false);
      context.commit('initializeMetaCache');
      // check if localStorage is available on the browser
      if (window.localStorage) {
        let data;
        // try to get the meta out of local storage
        try {
          data = JSON.parse(window.localStorage.getItem(context.state.dataset.id + '_data'));
        } catch (e) {
          console.error('Error retrieving local storage:', e);
          // if it fails (for whatever reason) clear local storage so we can
          // make the http request and set it again
          window.localStorage.clear();
        }
        // if we were able to get the stored data, return a promise that
        // immediately resolves with the data we found
        if (data) {
          context.commit('metaData', data);
          return;
        }
      }
      Vue.http.get(`/api/datasets/${context.state.dataset.id}/meta`).then(response => {
        const metadata = response.data;
        for (let key in metadata.meta) {
          const metaType = metadata.meta[key];
          if (Array.isArray(metaType.options)) {
            metaType.options = metaType.options.map(x => ({
              'name': x,
            }));
          }
        }
        if (Array.isArray(metadata.features.options)) {
          metadata.features.options = metadata.features.options.map(x => ({
            'name': x,
          }));
        }
        metadata.dataset = context.state.dataset.id;
        // window.localStorage.setItem(context.state.dataset.id + '_data', JSON.stringify(metadata));
        context.commit('metaData', metadata);
      }, response => {
        console.log('FAILED', response);
        router.replace('/404');
      });
    }
  },
  getDatasetGroups (context) {
    if (context.state.dataset) {
      // check if current metaData is the one we need right now
      if (context.state.metaData && context.state.metaData.dataset === context.state.dataset.id) {
        return;
      }
      // see if there is a dataset
      if (!context.state.dataset.id) {
        return;
      }
      context.commit('metaData', false);
      context.commit('initializeMetaCache');
      // check if localStorage is available on the browser
      if (window.localStorage) {
        let data;
        // try to get the meta out of local storage
        try {
          data = JSON.parse(window.localStorage.getItem(context.state.dataset.id + '_data'));
        } catch (e) {
          console.error('Error retrieving local storage:', e);
          // if it fails (for whatever reason) clear local storage so we can
          // make the http request and set it again
          window.localStorage.clear();
        }
        // if we were able to get the stored data, return a promise that
        // immediately resolves with the data we found
        if (data) {
          context.commit('metaData', data);
          return;
        }
      }
      Vue.http.get(`/api/datasets/${context.state.dataset.id}/groups`).then(response => {
        const groups = response.data;
        for (let key in groups) {
          if (Array.isArray(groups[key])) {
            groups[key] = groups[key].map(x => ({
              'name': x,
            }));
          }
        }
        context.commit('groups', groups);
      }, response => {
        console.log('FAILED', response);
        router.replace('/404');
      });
    }
  },
  setDataset (context, payload) {
    context.commit('dataset', payload);
    if (payload.id) {
      context.dispatch('getDatasetGroups');
    } else {
      if (router.currentRoute.params.dataset) {
        router.replace('/404');
      }
    }
  },
  logout (context) {
    localStorage.removeItem('jwt');
    context.commit('user', null);
  },
  getUser (context) {
    let user = null;
    try {
      let jwt = localStorage.getItem('jwt');
      if (jwt) {
        jwt = jwt.split('.');
        let headers = JSON.parse(atob(jwt[0]));
        if (headers.alg === 'HS512' && headers.typ === 'JWT') {
          user = JSON.parse(atob(jwt[1]));
          context.commit('user', user);
        }
      }
      if (user && user.exp < (Date.now() / 1000)) {
        localStorage.removeItem('jwt');
        user = null;
        context.commit('user', user);
      }
    } catch (e) {
      console.error('JWT malformed');
      localStorage.removeItem('jwt');
    }
    return user;
  },
  getUsers (context) {
    return Vue.http.get('/api/users').then(response => {
      return response.data;
    }, response => {
      let messageText;
      switch (response.status) {
        case 401:
          router.replace('/');
          messageText = 'You need to be logged in.';
          break;
        case 403:
          router.replace('/admin');
          messageText = 'You do not have permission.';
          break;
        default:
          router.replace('/');
          messageText = 'Unknown server error. Please try again.';
      }
      context.commit('addAlert', {
        variant: 'danger',
        message: messageText,
        show: 3,
      });
    });
  },
};
