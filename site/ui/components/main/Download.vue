<template>

  <div class="download top" v-if="filters">
    <h1>Download</h1>
    <h3>You have selected 478 samples.</h3>

    
    <div class="col-sm-6 col-sm-offset-3">
      <h2>Options</h2>

      <div class="form-group">
        <label>File Format</label>
        <selectize
          :options="fileformats.options"
          :value="options.fileformat"
          @updated="x => options.fileformat = x"
          :settings="fileformats.settings" ></selectize>
      </div>

      <button class="btn btn-primary btn-lg">Download</button>
    </div>

  </div>
</template>

<script>
import router from '../../router'
var selectize = require('../shared/Selectize')

export default {
  name: 'download',
  components: {
    selectize
  },
  data () {
    return {
      fileformats: {
        options: [
          {value: 'csv', name: 'Comma Separated Values ( .csv )'},
          {value: 'tsv', name: 'Tab Separated Values ( .tsv )'},
          {value: 'gct', name: 'Gene Cluster Text ( .gct )'},
          {value: 'json', name: 'JavaScript Object Notation ( .json )'}
        ],
        settings: {
          maxItems: 1,
          valueField: 'value'
        }
      },
      options: {
        fileformat: 'csv'
      }
    }
  },
  computed: {
    filters () {
      return this.$store.state.filters
    }
  },
  created () {
    if (!this.$store.state.filters) {
      var newPath = this.$route.fullPath.replace(/\/download.*/, '')
      router.replace(newPath)
    }
  }
}
</script>

<style lang="scss" scoped>
h1, h2, h3 {
  font-weight: normal;
}
.form-group {
  label {
    font-size: 1.25em;
  }
}
</style>
