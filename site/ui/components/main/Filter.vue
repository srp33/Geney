<template>

  <div class="filter top" v-if="metaData">
    <div class="col-sm-6 col-sm-offset-3">
      <h1>Filter Samples</h1>
      <selectize
        :options="metaTypes"
        :value="currentMetaType"
        placeholder="Select meta type to filter"
        @updated="x => currentMetaType = x"
        :settings="settings.metaTypes"></selectize>

      <div class="spacer"></div>
      <selectize v-if="currentMetaType"
        :options="metaData.meta[currentMetaType]"
        :value="selectedMeta[currentMetaType]"
        @updated="updateMeta"
        placeholder="Filter Meta"
        :settings="settings.metaData"></selectize>
      
      <h1>Select Genes</h1>
      <selectize
        :options="metaData.genes"
        :value="selectedGenes"
        @updated="updateGenes"
        placeholder="All Genes"
        :settings="settings.genes"></selectize>

    </div>
    <div class="col-sm-8 col-sm-offset-2">
      <div v-if="numKeys">
        <h2>Let me get this right...</h2>
        <h3>You're looking for <strong>ROWS</strong> that have:</h3>
        <h4 v-for="(values,type,num) in metaQuery"> 
          <span v-for="(value, index) in values" v-if="index < 3">
            "{{value}}"
            <strong v-if="index == values.length - 2 && values.length <= 3"> OR </strong>
          </span>

          <span v-if="values.length > 3"> (among others)</span>
          in the "{{type}}" column

          <h4 v-if="num < numKeys - 1"><strong>AND</strong></h4>
        </h4>
        <div v-if="selectedGenes && selectedGenes.length">
          <h3>And you want only the <strong>COLUMNS</strong> with the genes listed above.</h3>
        </div>
        <h3 v-else>And you want <strong>ALL</strong> of the <strong>COLUMNS</strong>.</h3>
      
        <h2>Is that correct?</h2>
        <button @click="commit" class="btn btn-primary btn-lg confirm-btn">Confirm</button>
      </div>
      <div v-else>
        <h2>Please select some filters so we can grant your wish.</h2>
      </div>
    </div>
  </div>
</template>

<script>
import router from '../../router'
var selectize = require('../shared/Selectize')

export default {
  name: 'filter',
  components: {
    selectize
  },
  data () {
    return {
      selectedGenes: [],
      currentMetaType: '',
      selectedMeta: {},
      settings: {
        metaTypes: {
          maxItems: 1
        },
        metaData: {},
        genes: {}
      }
    }
  },
  computed: {
    metaQuery () {
      // basically just removes any undefined elements from the
      // selectedMeta object
      var q = JSON.parse(JSON.stringify(this.selectedMeta))
      for (var key in q) {
        if (!q[key]) {
          delete q[key]
        }
      }
      return q
    },
    numKeys () {
      return Object.keys(this.metaQuery).length
    },
    metaTypes () {
      if (this.metaData.meta) {
        return Object.keys(this.metaData.meta).map(x => ({'name': x}))
      } else {
        return false
      }
    },
    metaData () {
      return this.$store.state.metaData
    }

  },
  methods: {
    updateGenes (payload) {
      this.$set(this, 'selectedGenes', payload)
    },
    updateMeta (payload) {
      this.$set(this.selectedMeta, this.currentMetaType, payload)
    },
    commit () {
      this.$store.commit('filters', {meta: this.metaQuery, genes: this.selectedGenes})
      router.push('/dataset/' + this.$route.params.dataset + '/filter/download')
    }
  },
  created () {
    if (this.$store.state.filters) {
      this.selectedGenes = this.$store.state.filters.genes
      this.selectedMeta = this.$store.state.filters.meta
    }
  }
}
</script>

<style lang="scss" scoped>
h1, h2, h3 {
  font-weight: normal;
}
.spacer {
  margin-top: 15px;
}
.confirm-btn {
  margin-bottom: 50px;
}
</style>
