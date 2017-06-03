import Vue from 'vue'
import VeeValidate from 'vee-validate'

const config = {
  fieldsBagName: 'valFields'
}
Vue.use(VeeValidate, config)

let Validator = VeeValidate.Validator

let validateCache = {
  id: {}
}

Validator.extend('idUsed', {
  getMessage () {
    return 'That ID is already in use!'
  },
  validate (value, args) {
    if (Array.isArray(value)) {
      value = value[0]
    }
    if (validateCache.id[value] !== undefined) {
      return new Promise(resolve => {
        resolve({
          valid: validateCache.id[value]
        })
      })
    }

    return Vue.http.get('/api/admin/validate/id?val=' + value).then(response => {
      validateCache.id[value] = response.data
      return { valid: response.data }
    }).catch(response => {
      return { valid: false }
    })
  }
})

export default Validator
