import Vue from 'vue';
import VeeValidate from 'vee-validate';

const config = {
  fieldsBagName: 'valFields',
};
Vue.use(VeeValidate, config);

let Validator = VeeValidate.Validator;

let validateCache = {
  id: {},
  username: {},
};

Validator.extend('idUsed', {
  getMessage () {
    return 'That ID is already in use!';
  },
  validate (value, args) {
    if (Array.isArray(value)) {
      value = value[0];
    }
    if (validateCache.id[value] !== undefined) {
      return new Promise(resolve => {
        resolve({
          valid: validateCache.id[value],
        });
      });
    }

    return Vue.http.get('/api/datasets/validate?val=' + value).then(response => {
      validateCache.id[value] = response.data;
      return { valid: response.data };
    }).catch(response => {
      return { valid: false };
    });
  },
});

Validator.extend('usernameUsed', {
  getMessage () {
    return 'That username is taken.';
  },
  validate (value, args) {
    console.log(value);
    if (Array.isArray(value)) {
      value = value[0];
    }
    if (validateCache.username[value] !== undefined) {
      return new Promise(resolve => {
        resolve({
          valid: validateCache.username[value],
        });
      });
    }

    return Vue.http.get('/api/users/validate?val=' + value).then(response => {
      validateCache.username[value] = response.data;
      return { valid: response.data };
    }).catch(response => {
      return { valid: false };
    });
  },
});

export default Validator;
