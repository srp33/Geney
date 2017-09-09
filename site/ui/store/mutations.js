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
    console.log('dataset', value);
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
};
