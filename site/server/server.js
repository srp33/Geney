const express = require('express');
const bodyParser = require('body-parser');
const morgan = require('morgan');
const config = require('../config');
const routes = require('./routes');

if (!process.env.NODE_ENV) {
  process.env.NODE_ENV = JSON.parse(config.dev.env.NODE_ENV);
}

let port = process.env.NODE_ENV === 'development'
  ? config.dev.backendPort
  : config.prod.port;

let app = express();

app.use(morgan(':date[iso] | :method | :url | :remote-addr | :status | :response-time[5]'));
app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());
app.use(routes);

module.exports = app.listen(port, err => {
  if (err) {
    console.log(err);
    return;
  }
  console.log('Listening on port ' + port);
});
