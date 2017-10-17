const express = require('express');
const bodyParser = require('body-parser');
const morgan = require('morgan');
const path = require('path');

if (!process.env.NODE_ENV) {
  process.env.NODE_ENV = 'development';
}

let config;
if (process.env.NODE_ENV === 'development') {
  config = require('../config').dev;
} else {
  config = require('./server-config.json');
}

const routes = require('./routes')(config);

let app = express();

app.use(morgan(':date[iso] | :method | :url | :remote-addr | :status | :response-time[5]'));
app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());
app.use(routes);

app.use('/', express.static('dist/'));

app.get('*', (req, res) => {
  res.sendFile(path.resolve('dist') + '/index.html');
});

module.exports = app.listen(config.port, err => {
  if (err) {
    console.log(err);
    return;
  }
  console.log('Listening on port ' + config.port);
});
