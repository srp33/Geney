import Vue from 'vue'
import VeeValidate from 'vee-validate'
Vue.use(VeeValidate)

let Validator = VeeValidate.Validator

Validator.extend('idUsed', {
  getMessage () {
    return 'That ID is already in use!'
  },
  validate (value, args) {
    // return new Promise(resolve => {
    //   resolve({
    //     valid: true,
    //     data: value !== 'trigger' ? undefined : { message: 'Not this value' }
    //   })
    // })
    return Vue.http.get('/api/admin/validate/id?val=' + value).then(response => {
      return { valid: response.data }
    }).catch(response => {
      return { valid: false }
    })
  }
})

export default Validator
