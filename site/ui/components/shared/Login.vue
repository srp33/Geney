<template>

  <div class="login container">
    <form>
      <div class="col-xs-12">
        <h1 class="heading">
          Login
          <br>
          <h4>Please enter your username and password below to manage datasets.</h4>
          <h4>Note that you do not need to login to download any data.</h4>
        </h1>

        <div class="form-group col-sm-6 col-sm-offset-3">
          <label for="username">Username</label>
          <input id="username" type="text" v-model="username" class="form-control" name="username">
        </div>

        <div class="form-group col-sm-6 col-sm-offset-3">
          <label for="password">Password</label>
          <input id="password" type="password" v-model="password" class="form-control" name="password">
        </div>
      </div>
      <div class="col-xs-12">
        <button class="btn btn-primary btn-lg"
                :disabled="username.length <= 4 || password.length <= 4" @click="login">
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
      password: ''
    }
  },
  created () {
    this.$store.dispatch('getUser', user => {
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
      e.preventDefault() // stop form from submitting
      this.$store.dispatch('login', {
        username: this.username,
        password: this.password,
        callback (user) {
          if (user && user.username) {
            router.push('/admin')
          } else {
            alert('Invalid username or password')
            that.username = ''
            that.password = ''
          }
        }
      })
    }
  }
}
</script>

<style lang="scss" scoped>

.heading {
  margin-bottom: 50px;
}

</style>
