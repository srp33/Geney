<template>

  <div class="login container top">
    <form @submit.prevent="login">
      <div class="row">
        <h1 class="heading text-center col-12">
          Login
          <br>
          <h4>Please enter your username and password below to manage datasets.</h4>
          <h4>Note that you do not need to login to download any data.</h4>
        </h1>

        <h4 v-if="invalidLogin" class="text-center col-12">{{loginMessage}}<br>
          <small>Attempts: {{invalidCount}}</small>
        </h4>

        <div class="form-group col-sm-6 offset-sm-3" :class="{'has-danger': errors.has('username') && !invalidLogin}">
          <label for="username" class="form-control-label">Username</label>
          <input id="username" type="text" v-model="username" class="form-control" name="username"
                v-validate="'required'" :class="{'form-control-danger': errors.has('username') && !invalidLogin}">
          <span v-show="errors.has('username') && !invalidLogin" class="form-control-feedback">{{ errors.first('username') }}</span>
        </div>

        <div class="form-group col-sm-6 offset-sm-3" :class="{'has-danger': errors.has('password') && !invalidLogin}">
          <label for="password" class="form-control-label">Password</label>
          <input id="password" type="password" v-model="password" class="form-control" name="password"
                v-validate="'required'" :class="{'form-control-danger': errors.has('password') && !invalidLogin}">
          <span v-show="errors.has('password') && !invalidLogin" class="form-control-feedback">{{ errors.first('password') }}</span>
        </div>
      </div>
      <div class="col-xs-12">
        <button class="btn btn-primary btn-lg" :disabled="errors.any()">
          Login
        </button>
      </div>
    </form>
  </div>
</template>


<script>
import router from '../../router'

export default {
  name: 'login',
  data () {
    return {
      username: '',
      password: '',
      invalidLogin: false,
      loginMessage: '',
      invalidCount: 0
    }
  },
  created () {
    this.$store.dispatch('getUser').then(user => {
      if (user && user.username) {
        router.push('/admin')
      } else if (user && !user.username) {
        this.$store.dispatch('logout')
      }
    })
  },
  methods: {
    login (e) {
      let that = this
      this.$validator.validateAll().then(() => {
        that.$http.post('/auth/login', {
          username: that.username,
          password: that.password
        }).then(response => {
          if (response.data.jwt) {
            that.$store.dispatch('getUser').then(user => {
              if (user && user.username) {
                router.push('/admin')
              } else {
                that.failLogin()
              }
            })
          } else {
            that.failLogin('Invalid username or password')
          }
        }, response => {
          console.error('Login failed: ', response)
          that.failLogin()
        })
      }).catch(() => {})
    },
    failLogin (msg) {
      this.invalidLogin = true
      this.loginMessage = msg || 'Authentication error. Please try again.'
      this.username = ''
      this.password = ''
      this.invalidCount++
    }
  }
}
</script>

<style lang="scss" scoped>

.heading {
  margin-bottom: 50px;
}

</style>
