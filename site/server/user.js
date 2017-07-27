const bcrypt = require('bcryptjs');

module.exports = class User {
  constructor (userDefinition, ignore) {
    if (!Array.isArray(ignore)) {
      ignore = [];
    }
    let keys = [
      'username',
      'firstname',
      'lastname',
      'email',
      'privileges',
      'email_reset_id',
      'failed_attempts',
    ];
    for (let key of keys) {
      if (userDefinition[key] === undefined && ignore.indexOf(key) === -1) {
        throw new Error('User object missing key: ' + key);
      } else {
        this[key] = userDefinition[key];
      }
      if (userDefinition.password) {
        this.password = userDefinition.password;
      } else if (userDefinition.passhash) {
        this.passhash = userDefinition.passhash;
      }
      if (typeof this.privileges === 'string') {
        this.privileges = JSON.parse(this.privileges);
      }
    }
  }

  getPayload () {
    return {
      username: this.username,
      firstname: this.firstname,
      lastname: this.lastname,
      email: this.email,
      privileges: this.privileges,
    };
  }

  getPasshash (callback) {
    if (this.passhash) {
      callback(this.passhash);
    } else if (this.password) {
      bcrypt.hash(this.password, 10, (err, hash) => {
        if (err) {
          callback(false);
        } else {
          callback(hash);
        }
      });
    } else {
      callback(false);
    }
  }
};
