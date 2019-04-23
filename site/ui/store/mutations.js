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
  filters (state, value) {
    state.filters = value;
  },
  addFilter (state, payload) {
    if (!payload.key || payload.key === false) {
      state.filters[payload.variable.index] = {value: payload.value, variable: payload.variable};
    } else {
      state.filters[payload.variable.index].value[payload.index][payload.key] = payload.value;
    }
  },
  removeFilter (state, variable) {
    delete state.filters[variable.index];
  },
  datasets (state, value) {
    state.datasets = value;
  },
  dataset (state, value) {
    state.dataset = value;
    state.selectedFeatures = {};
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
  selectedFeatures (state, payload) {
    state.selectedFeatures[payload.group] = payload.value;
  },
  columnData (state, payload) {
    state.columnNamesFile = payload.columnNamesFile;
    state.columnIndicesFile = payload.columnIndicesFile;
    state.numColumns = payload.numColumns;
  },
  sampleData (state, payload) {
    state.sampleFile = payload.sampleFile;
    state.numSamples = payload.numSamples;
  },
  sampleFile (state, value) {
    state.sampleFile = value;
  },
  numSamples (state, value) {
    state.numSamples = value;
  },
  numColumns (state, value) {
    state.numColumns = value;
  },
  selectedPathways (state, payload) {
    state.selectedPathways = payload;
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
