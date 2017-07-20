<template>
  <div class="edit-user row">
    <div class="col-12 text-center">
      <h3>Edit User</h3>
    </div>

    <div class="form-group col-sm-6 offset-sm-3" :class="{'has-danger': errors.has('firstname')}">
      <label for="firstname" class="form-control-label">First Name</label>
      <input type="text" name="firstname" id="firstname" v-model="firstname" class="form-control"
            v-validate="'required'" :class="{'form-control-danger': errors.has('firstname')}">
      <span v-if="errors.has('firstname')" class="form-control-feedback">{{ errors.first('firstname') }}</span>
    </div>

    <div class="form-group col-sm-6 offset-sm-3" :class="{'has-danger': errors.has('lastname')}">
      <label for="lastname" class="form-control-label">Last Name</label>
      <input type="text" name="lastname" id="lastname" v-model="lastname" class="form-control"
            v-validate="'required'" :class="{'form-control-danger': errors.has('lastname')}">
      <span v-if="errors.has('lastname')" class="form-control-feedback">{{ errors.first('lastname') }}</span>
    </div>

    <div class="form-group col-sm-6 offset-sm-3">
      <label for="username" class="form-control-label">Username</label>
      <input type="text" name="username" id="username" v-model="username" class="form-control" readonly>
    </div>

    <div class="form-group col-sm-6 offset-sm-3" :class="{'has-danger': errors.has('email')}">
      <label for="email" class="form-control-label">Email</label>
      <input type="text" name="email" id="email" v-model="email" class="form-control"
            v-validate="'required|email'" :class="{'form-control-danger': errors.has('email')}" data-vv-delay="500">
      <span v-if="errors.has('email')" class="form-control-feedback">{{ errors.first('email') }}</span>
    </div>

    <div class="form-group col-sm-6 offset-sm-3" :class="{'has-danger': errors.has('password')}">
      <label for="password" class="form-control-label">New Password</label>
      <input type="password" name="password" id="password" v-model="pass1" class="form-control"
            v-validate="''" :class="{'form-control-danger': errors.has('password')}" >
      <span v-if="errors.has('password')" class="form-control-feedback">{{ errors.first('password') }}</span>
    </div>

    <div class="form-group col-sm-6 offset-sm-3" :class="{'has-danger': errors.has('confirm password') && blurred['confirm password']}">
      <label for="confirm password" class="form-control-label">Confirm Password</label>
      <input type="password" name="confirm password" id="confirm password" v-model="pass2" class="form-control"
            v-validate="'confirmed:password'" :class="{'form-control-danger': errors.has('confirm password') && blurred['confirm password']}"
            @blur="blur('confirm password')">
      <span v-if="errors.has('confirm password') && blurred['confirm password']" class="form-control-feedback">{{ errors.first('confirm password') }}</span>
    </div>

    <div class="form-group col-sm-6 offset-sm-3" v-if="Array.isArray(privileges)">
      <label class="form-control-label">Privileges</label>
      <selectize
        :options="mappedPrivileges"
        :value="privileges"
        @updated="updatePrivileges"></selectize>
    </div>

    <div class="col-12 text-center" style="margin-bottom: 15px;">
      <button class="btn btn-primary" @click="saveUser()">Save</button>
    </div>

    <div class="col-12 text-center" style="margin-bottom: 50px;">
      <button class="btn btn-danger" @click="deleteUser()">Delete</button>
    </div>
  </div>
</template>


<script>
import router from '../../../router'
const selectize = require('../../shared/Selectize')

export default {
  name: 'edit_user',
  components: {
    selectize
  },
  data () {
    return {
      firstname: '',
      lastname: '',
      username: '',
      email: '',
      pass1: '',
      pass2: '',
      accepted: '',
      privileges: null,
      selected: [],
      availablePrivileges: ['datasets', 'users'],
      blurred: {}
    }
  },
  created () {
    let selectedUser = null
    this.$store.dispatch('getUsers').then(users => {
      if (Array.isArray(users)) {
        users.forEach(user => {
          if (user.username === this.$route.params.user) {
            user.privileges = JSON.parse(user.privileges)
            selectedUser = user
          }
        })
        if (selectedUser) {
          for (let prop of ['firstname', 'lastname', 'username', 'email', 'privileges']) {
            this[prop] = selectedUser[prop]
          }
        }
      }
      if (!selectedUser) {
        router.push('/404')
      }
    })
  },
  computed: {
    mappedPrivileges () {
      return this.availablePrivileges.map(permission => {
        return { name: permission }
      })
    }
  },
  methods: {
    // marks the input as having been blurred
    // password confirmtation won't show error
    // message until it has been blurred
    blur (input) {
      this.$set(this.blurred, input, true)
    },
    updatePrivileges (payload) {
      this.$set(this, 'privileges', payload)
    },
    saveUser () {
      this.$validator.validateAll().then((valid) => {
        if (valid) {
          this.$http.patch('/api/admin/users/' + this.username, {
            password: this.pass1.length ? this.pass1 : undefined,
            firstname: this.firstname,
            lastname: this.lastname,
            email: this.email,
            privileges: this.privileges
          }).then(response => {
            this.$store.commit('addAlert', {
              variant: 'success',
              message: 'User updated successfully.',
              show: 3
            })
            setTimeout(() => {
              router.push('/admin/users')
            }, 250)
          }).catch(response => {
            this.$store.commit('addAlert', {
              variant: 'danger',
              message: 'Error saving user.',
              show: 3
            })
            console.error(response)
          })
        }
      })
    },
    deleteUser () {
      let confirmed = window.confirm(`Do you really want to delete ${this.username}?`)
      if (confirmed) {
        this.$http.delete('/api/admin/users/' + this.username)
          .then(response => {
            this.$store.commit('addAlert', {
              variant: 'success',
              message: 'User deleted.',
              show: 3
            })
            setTimeout(() => {
              router.push('/admin/users')
            }, 250)
          }).catch(response => {
            console.log(response)
          })
      }
    }
  },
  filters: {
  }
}
</script>

<style lang="scss" scoped>

</style>
