const jwt = require('express-jwt');
const router = require('express').Router();
const UserService = new (require('../users/user-service'))();
const config = require('../../config');
const jwtAuth = jwt({ secret: config.dev.secret });


router.post('/auth/login', (req, res, next) => {
  if (req.user) {
    res.sendStatus(400);
  } else {
    console.log('YASSS')
    UserService.authenticateUser(req.body.username, req.body.password, (jwt, errorcode) => {
      console.log(jwt, errorcode)
      if (errorcode) {
        res.sendStatus(errorcode);
      } else {
        res.json({jwt: jwt});
      }
    });
  }
});

router.all('/api/users/*', jwtAuth, (req, res, next) => {
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

router.get('/api/users', (req, res) => {
  UserService.getAllUsers((users, errorcode) => {
    if (users) {
      res.json(users);
    } else {
      res.sendStatus(errorcode);
    }
  });
});

router.put('/api/users', (req, res) => {
  UserService.addUser(req.body, (success, errorcode) => {
    if (success) {
      res.sendStatus(201);
    } else {
      res.sendStatus(errorcode);
    }
  });
});

router.get('/api/users/validate', (req, res, next) => {
  UserService.getUser(req.query.val, user => {
    if (user === null) {
      res.json(true);
    } else {
      res.json(false);
    }
  });
});

router.patch('/api/users/:id', (req, res) => {
  req.body.username = req.params.id;
  UserService.updateUser(req.body, (success, errorcode) => {
    if (success) {
      res.sendStatus(200);
    } else {
      res.sendStatus(errorcode);
    }
  });
});

router.delete('/api/users/:id', (req, res) => {
  UserService.deleteUser(req.params.id, (success, errorcode) => {
    if (success) {
      res.sendStatus(200);
    } else {
      res.sendStatus(errorcode);
    }
  });
});

module.exports = router;
