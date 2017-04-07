<template>

  <div class="404 top">
    <h1 class="large">404</h1>
    <!--<img class="logo" src="../assets/geney-no-lamp.png">-->
    <h1>Uh, what were you looking for?</h1>
    <h3>We couldn't find it...Sorry!</h3>

    <router-link to="/" class="btn btn-primary btn-lg">
      Go Home 
      <i class="fa fa-home" aria-hidden="true"></i>
    </router-link>

  </div>
</template>

<script>

export default {
  name: 'Error404',
  data () {
    return {
    }
  },
  created () {
  },
  computed: {
  },
  methods: {
  }
}
</script>

<style lang="scss" scoped>
  .large {
    font-size: 25em;
  }
</style>
