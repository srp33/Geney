const express = require('express');
const jwt = require('express-jwt');
const bodyParser = require('body-parser');
const config = require('../config');
const UserService = new (require('./user-service'))();

// TODO: REMOVE
const datasets = require('../ui/api/datasets.json');
const lincslevel2 = require('../ui/api/lincslevel2.json');

if (!process.env.NODE_ENV) {
  process.env.NODE_ENV = JSON.parse(config.dev.env.NODE_ENV);
}

let port = process.env.NODE_ENV === 'development'
  ? config.dev.backendPort
  : config.prod.port;

let app = express();

app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());

const jwtAuth = jwt({ secret: config.dev.secret });

// app.use(jwt({
//   secret: config.dev.secret,
//   credentialsRequired: false
// }))

// TODO: REMOVE THESE
app.get('/api/datasets', (req, res, next) => {
  res.json(datasets);
});

app.get('/api/datasets/lincslevel2/meta', (req, res, next) => {
  res.json(lincslevel2);
});

app.get('/api/datasets/validate', (req, res, next) => {
  res.json(req.query.val !== 'lincslevel2');
});

app.put('/api/datasets', (req, res, next) => {
  res.sendStatus(202);
  console.log(req);
});

app.post('/api/datasets/:id/samples', (req, res, next) => {
  res.json(428);
});

app.post('/api/datasets/:id/download', (req, res, next) => {
  let query = JSON.parse(req.body.query);
  let filename = query.options.filename + '.' + query.options.fileformat;
  res.header({
    'Content-Type': 'text/plain',
    'Content-disposition': 'attachment; filename=' + filename,
  });
  res.send('YAY!');
  res.end();
});

app.patch('/api/datasets/:id', (req, res, next) => {
  res.json(true);
});
// END TODO

app.post('/auth/login', (req, res, next) => {
  if (req.user) {
    res.sendStatus(400);
  } else {
    UserService.authenticateUser(req.body.username, req.body.password, (jwt, errorcode) => {
      if (errorcode) {
        res.sendStatus(errorcode);
      } else {
        res.json({jwt: jwt});
      }
    });
  }
});

app.all('/api/users/*', jwtAuth, (req, res, next) => {
  if (!req.user) {
    res.sendStatus(401); // Unauthorized
  } else {
    if (req.user.privileges.indexOf('users') === -1) {
      res.sendStatus(403); // Forbidden
    } else {
      next();
    }
  }
});

app.get('/api/users', (req, res) => {
  UserService.getAllUsers((users, errorcode) => {
    if (users) {
      res.json(users);
    } else {
      res.sendStatus(errorcode);
    }
  });
});

app.put('/api/users', (req, res) => {
  UserService.addUser(req.body, (success, errorcode) => {
    if (success) {
      res.sendStatus(201);
    } else {
      res.sendStatus(errorcode);
    }
  });
});

app.get('/api/users/validate', (req, res, next) => {
  UserService.getUser(req.query.val, user => {
    if (user === null) {
      res.json(true);
    } else {
      res.json(false);
    }
  });
});

app.patch('/api/users/:id', (req, res) => {
  req.body.username = req.params.id;
  UserService.updateUser(req.body, (success, errorcode) => {
    if (success) {
      res.sendStatus(200);
    } else {
      res.sendStatus(errorcode);
    }
  });
});

app.delete('/api/users/:id', (req, res) => {
  UserService.deleteUser(req.params.id, (success, errorcode) => {
    if (success) {
      res.sendStatus(200);
    } else {
      res.sendStatus(errorcode);
    }
  });
});

module.exports = app.listen(port, err => {
  if (err) {
    console.log(err);
    return;
  }
  console.log('Listening on port ' + port);
});
