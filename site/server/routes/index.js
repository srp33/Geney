module.exports = function (config) {
  return [
    require('./user-routes')(config),
    require('./mock-dataset-routes'),
  ];
};
