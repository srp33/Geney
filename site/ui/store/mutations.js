export default {
  downloadStatus (state, value) {
    state.downloadStatus = value;
  },
  downloadPath (state, value) {
    state.downloadPath = value;
  },
  groups (state, value) {
    state.groups = value;
  },
  options (state, value) {
    state.options[value.variable] = value.options;
  },
  metaData (state, value) {
    state.metaData = value;
  },
  filters (state, value) {
    state.filters = value;
    if (state.filters) {
      state.selectedVariables = Object.keys(state.filters);
    }
  },
  datasets (state, value) {
    state.datasets = value;
  },
  dataset (state, value) {
    state.dataset = value;
    state.selectedFeatures = {};
    state.selectedVariables = [];
    state.downloadRadios = {};
  },
  user (state, value) {
    state.user = value;
  },
  addAlert (state, alert) {
    state.alerts.push(alert);
  },
  users (state, users) {
    state.users = users;
  },
  cachedMeta (state, payload) {
    if (!state.cachedMeta[payload.dataset]) {
      state.cachedMeta[payload.dataset] = {};
    }

    state.cachedMeta[payload.dataset][payload.metaType] = payload.value;
  },
  initializeMetaCache (state) {
    if (state.dataset && state.dataset.id && !state.cachedMeta[state.dataset.id]) {
      state.cachedMeta[state.dataset.id] = {};
    }
  },
  selectedFeatures (state, payload) {
    state.selectedFeatures[payload.group] = payload.value;
  },
  selectedSets (state, payload) {
    state.selectedSets = payload;
  },
  selectedVariables (state, payload) {
    state.selectedVariables = payload;
  },
  lastMetaType (state, payload) {
    state.lastMetaType = payload;
  },
  downloadRadios (state, payload) {
    state.downloadRadios[payload.group] = payload.value;
  },
  featuresRadioValue (state, payload) {
    switch (payload) {
      case 'all':
        state.downloadRadios.features = 'all';
        break;
      case 'selected':
        state.downloadRadios.features = 'selected';
        break;
      default:
        throw new Error(`unknown features radio type ${payload}`);
    }
  },
  variablesRadioValue (state, payload) {
    switch (payload) {
      case 'all':
        state.downloadRadios.variables = 'all';
        break;
      case 'selected':
        state.downloadRadios.variables = 'selected';
        break;
      default:
        throw new Error(`unknown variables radio type ${payload}`);
    }
  },
};
