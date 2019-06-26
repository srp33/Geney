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
  getDatasetGroups (context) {
    if (context.state.dataset) {
      // check if current metaData is the one we need right now
      // see if there is a dataset
      if (!context.state.dataset.id) {
        return;
      }
      Vue.http.get(`/api/datasets/${context.state.dataset.id}/groups`).then(response => {
        const groups = response.data;
        for (let key in groups) {
          context.commit('selectedFeatures', {group: key, value: 'all'});
          if (Array.isArray(groups[key])) {
            groups[key] = groups[key].map(x => ({
              name: x[1],
              value: x,
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
  clearDataset (context) {
    context.commit('filters', {});
    context.commit('selectedPathways', []);
    context.commit('selectedFeatures', null);
    context.commit('columnIndicesFile', null);
    context.commit('columnNamesFile', null);
    context.commit('sampleFile', null);
    context.commit('numSamples', null);
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
