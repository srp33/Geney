<template>

  <div class="admin">
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
    console.log('Checking authenticated')
    this.$store.dispatch('getUser', (user) => {
      if (user === null || user.username === undefined) {
        router.push('/login')
      }
    })
  }
}
</script>

<style lang="scss" scoped>

.admin {
  margin-left: 200px;
  text-align: left;
  padding-left: 25px;
}

</style>
