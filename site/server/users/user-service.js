const path = require('path');
const sqlite3 = require('sqlite3');
const queries = require('./sql-queries');
const bcrypt = require('bcryptjs');
const token = require('jsonwebtoken');
const tokenConfig = {algorithm: 'HS512', expiresIn: '30m'};
const User = require('./user');

module.exports = class UserService {
  constructor (secret) {
    this.secret = secret;
    this.db = new sqlite3.Database(path.join(__dirname, 'geney.db'));
    this.db.run(queries.create, err => {
      if (err) {
        console.error(err);
        process.exit(1);
      }
    });
  }

  /**
   * Gets a user from the database and parses the privileges
   *
   * @param {string} username
   * @param {function} callback
   * @return {User}
   */
  getUser (username, callback) {
    let statement = this.db.prepare(queries.getUser);
    statement.get(username, (err, userDefinition) => {
      if (err) {
        callback(null);
      }
      // check if user exists
      if (userDefinition) {
        try {
          callback(new User(userDefinition));
        } catch (e) {
          callback(false);
        }
      } else {
        callback(null);
      }
    });
  }

  /**
   *
   * @param {string} password
   * @param {string} passhash
   * @param {function} callback
   */
  validatePassword (password, passhash, callback) {
    bcrypt.compare(password, passhash, (err, valid) => {
      console.log('VALID', valid);
      if (err) {
        callback(false);
      } else {
        callback(!!valid);
      }
    });
  }

  /**
   * Checks the username and password and returns a jwt is
   *
   * @param  {string} username
   * @param  {string} password
   * @param  {function} callback
   */
  authenticateUser (username, password, callback) {
    this.getUser(username, user => {
      if (!user) {
        callback(false, 401);
        return;
      }
      user.getPasshash(hash => {
        if (!hash) {
          callback(false, 401);
          return;
        }
        this.validatePassword(password, hash, valid => {
          if (valid) {
            token.sign(user.getPayload(), this.secret, tokenConfig, (err, jwt) => {
              if (err) {
                callback(false, 500);
              } else {
                callback(jwt);
              }
            });
          } else {
            callback(false, 401);
          }
        });
      });
    });
  }

  getAllUsers (callback) {
    this.db.all(queries.getAllUsers, (err, rows) => {
      if (err) {
        callback(500);
      } else {
        callback(rows);
      }
    });
  }

  addUser (userDefinition, callback) {
    try {
      let user = new User(userDefinition, ['email_reset_id', 'failed_attempts']);
      let privileges = JSON.stringify(user.privileges);
      user.getPasshash(passhash => {
        if (!passhash) {
          callback(false, 500);
          return;
        }
        let statement = this.db.prepare(queries.addUser);
        statement.run(
          user.username,
          user.firstname,
          user.lastname,
          user.email,
          passhash,
          privileges,
          0,
          err => {
            callback(!err, 500);
          });
      });
    } catch (e) {
      console.log(e);
      callback(false, 400);
    }
  }

  updateUser (userDefinition, callback) {
    try {
      let user = new User(userDefinition, ['email_reset_id', 'failed_attempts']);
      let privileges = JSON.stringify(user.privileges);
      user.getPasshash(passhash => {
        let statement;
        if (passhash === false) {
          statement = this.db.prepare(queries.updateUser,
            user.firstname,
            user.lastname,
            user.email,
            privileges,
            user.username);
        } else {
          statement = this.db.prepare(queries.updateUserWithPassword,
            user.firstname,
            user.lastname,
            user.email,
            privileges,
            passhash,
            user.username);
        }
        statement.run(err => {
          if (!err) {
            callback(true);
          } else {
            callback(false, 500);
          }
        });
      });
    } catch (e) {
      callback(false, 400);
    }
  }

  deleteUser (username, callback) {
    let statement = this.db.prepare(queries.deleteUser, username);
    statement.run(err => {
      if (!err) {
        callback(true);
      } else {
        callback(false, 500);
      }
    });
  }
};
