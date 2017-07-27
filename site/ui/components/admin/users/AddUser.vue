<template>
  <div class="add-user row">
    <div class="col-12 text-center">
      <h3>Add User</h3>
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

    <div class="form-group col-sm-6 offset-sm-3" :class="{'has-danger': errors.has('username')}">
      <label for="username" class="form-control-label">Username</label>
      <input type="text" name="username" id="username" v-model="username" class="form-control"
            v-validate="'required|usernameUsed'" :class="{'form-control-danger': errors.has('username')}" data-vv-delay="500">
      <span v-if="errors.has('username')" class="form-control-feedback">{{ errors.first('username') }}</span>
    </div>

    <div class="form-group col-sm-6 offset-sm-3" :class="{'has-danger': errors.has('email')}">
      <label for="email" class="form-control-label">Email</label>
      <input type="text" name="email" id="email" v-model="email" class="form-control"
            v-validate="'required|email'" :class="{'form-control-danger': errors.has('email')}" data-vv-delay="500">
      <span v-if="errors.has('email')" class="form-control-feedback">{{ errors.first('email') }}</span>
    </div>

    <div class="form-group col-sm-6 offset-sm-3" :class="{'has-danger': errors.has('password')}">
      <label for="password" class="form-control-label">Password</label>
      <input type="password" name="password" id="password" v-model="pass1" class="form-control"
            v-validate="'required'" :class="{'form-control-danger': errors.has('password')}" >
      <span v-if="errors.has('password')" class="form-control-feedback">{{ errors.first('password') }}</span>
    </div>

    <div class="form-group col-sm-6 offset-sm-3" :class="{'has-danger': errors.has('confirm password') && blurred['confirm password']}">
      <label for="confirm password" class="form-control-label">Confirm Password</label>
      <input type="password" name="confirm password" id="confirm password" v-model="pass2" class="form-control"
            v-validate="'required|confirmed:password'" :class="{'form-control-danger': errors.has('confirm password') && blurred['confirm password']}"
            @blur="blur('confirm password')">
      <span v-if="errors.has('confirm password') && blurred['confirm password']" class="form-control-feedback">{{ errors.first('confirm password') }}</span>
    </div>

    <div class="form-group col-sm-6 offset-sm-3">
      <label class="form-control-label">Privileges</label>
      <selectize
        :options="mappedPrivileges"
        :value="privileges"
        @updated="updatePrivileges"></selectize>
    </div>

    <div class="col-12 text-center" style="margin-bottom: 50px;">
      <button class="btn btn-primary" @click="addUser()">Save</button>
    </div>
  </div>
</template>


<script>
import router from '../../../router';
const selectize = require('../../shared/Selectize');

export default {
  name: 'add_user',
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
      privileges: [],
      selected: [],
      availablePrivileges: ['datasets', 'users'],
      blurred: {}
    };
  },
  created () {
  },
  computed: {
    mappedPrivileges () {
      return this.availablePrivileges.map(permission => {
        return { name: permission };
      });
    }
  },
  methods: {
    // marks the input as having been blurred
    // password confirmtation won't show error
    // message until it has been blurred
    blur (input) {
      this.$set(this.blurred, input, true);
    },
    updatePrivileges (payload) {
      this.$set(this, 'privileges', payload);
    },
    addUser () {
      this.$validator.validateAll().then(valid => {
        if (valid) {
          this.$http.put('/api/users/', {
            username: this.username,
            password: this.pass1,
            firstname: this.firstname,
            lastname: this.lastname,
            email: this.email,
            privileges: this.privileges
          }).then(response => {
            this.$store.commit('addAlert', {
              variant: 'success',
              message: 'User added successfully.',
              show: 3
            });
            setTimeout(() => {
              router.push('/admin/users');
            }, 250);
          }).catch(response => {
            console.error('failure', response);
          });
        }
      });
    }
  },
  filters: {
  }
};
</script>

<style lang="scss" scoped>

</style>
