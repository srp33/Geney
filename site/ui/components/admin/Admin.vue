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
