<template>

  <div class="description top" v-if="dataset">
    <img class="logo" src="../../assets/geney-no-lamp.png">
    <h1>{{ dataset.name }}</h1>
    <h3 v-html="dataset.description"></h3>
    <ul class="meta-types">
      <li><i class="fa fa-2x fa-align-justify" aria-hidden="true"></i><br>{{ dataset.numSamples }} Samples</li>
      <li><i class="fa fa-2x fa-flask" aria-hidden="true"></i><br>{{ dataset.numGenes }} Genes</li>
      <li><i class="fa fa-2x fa-gears" aria-hidden="true"></i><br>{{ dataset.numMetaTypes }} Meta Data Types</li>
    </ul>
    <router-link :to="'/dataset/' + dataset.id + '/filter'" class="btn btn-primary btn-lg">Select Samples & Genes</router-link>
  </div>
</template>

<script>

export default {
  name: 'description',
  data () {
    return {
    }
  },
  computed: {
    dataset () {
      return this.$store.state.dataset
    }
  }
}
</script>

<style lang="scss" scoped>

.meta-types {
  list-style-type: none;
  padding: 0;
  margin-top: 25px;
  margin-bottom: 50px;
  li {
    display: inline-block;
    margin: 0 10px;
    font-size: 1.25em;
  }
}
</style>
