export default {
  metaData (state, value) {
    state.metaData = value;
  },
  filters (state, value) {
    state.filters = value;
  },
  datasets (state, value) {
    state.datasets = value;
  },
  dataset (state, value) {
    state.dataset = value;
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
};
