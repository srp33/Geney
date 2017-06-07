<template>

  <div class="admin top">
    <router-view></router-view>
  </div>
</template>


<script>
import router from '../../router'

export default {
  name: 'admin',
  data () {
    return {
    }
  },
  created () {
    this.$store.dispatch('getUser').then(user => {
      if (user === null || user.username === undefined) {
        router.push('/login')
      } else {
        if (user.privileges.length) {
          let route = user.privileges[0]
          router.replace('/admin/' + route)
        } else {
          this.$store.state.commit('addAlert', {
            variant: 'danger',
            message: 'You have no permissions!',
            show: 3
          })
        }
      }
    })
  }
}
</script>

<style lang="scss" scoped>

.admin {
  text-align: left;
  padding-left: 25px;
  padding-right: 25px;
}

</style>
