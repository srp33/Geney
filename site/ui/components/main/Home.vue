<template>

  <div class="home top" v-if="datasets">
    <div class="logo">
      <img src="../../assets/geney-no-lamp.png">
    </div>
    <div class="col-xs-12">
      <div v-if="datasets.length > 0" class="col-sm-8 col-sm-offset-2">
        <h1>Please select a dataset</h1>
        <selectize
          :options="datasets"
          :value="selected.id"
          placeholder="Select Dataset"
          @updated="setSelected"
          :settings="settings" ></selectize>
      </div>
      <div v-else>
        <h1>No Datasets Found.</h1>

      </div>
    </div>
    <router-link v-if="selected.id" @click="selectDataset" :to="path" class="btn btn-primary btn-lg">View Dataset Description</router-link>
    
  </div>
</template>

<script>
var selectize = require('../shared/Selectize')
// import router from '../router'

export default {
  name: 'home',
  components: {selectize},
  data () {
    return {
      selected: {},
      settings: {
        maxItems: 1,
        valueField: 'id',
        labelField: 'name'
      }
    }
  },
  created () {
  },
  computed: {
    datasets () {
      return this.$store.state.datasets
    },
    path () {
      return '/dataset/' + this.selected.id || ''
    }
  },
  methods: {
    setSelected (value) {
      var dataset = {}
      for (var x of this.datasets) {
        if (x.id === value) {
          dataset = x
          break
        }
      }
      this.$set(this, 'selected', dataset)
    },
    selectDataset () {
      this.$store.dispatch('setDataset', this.selected)
    }
  }
}
</script>

<style lang="scss" scoped>

</style>
