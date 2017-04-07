<template>

  <div class="manage-users">

    <h1>Manage Users</h1>



  </div>
</template>


<script>

export default {
  name: 'manage_datasets',
  data () {
    return {
    }
  },
  created () {
  },
  computed: {
    datasets () {
      return this.$store.state.datasets
    }
  },
  methods: {
  }
}
</script>

<style lang="scss" scoped>

</style>
