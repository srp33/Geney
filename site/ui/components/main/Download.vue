<template>

  <div class="download top row justify-content-center" v-if="filters">
    <div class="col-12">
      <h1>Download</h1>
      <div v-if="numSamples != null">
        <h3 v-if="numSamples >= 0">You have selected {{ numSamples }} samples.</h3>
        <h3 v-else>Unable to retreive number of samples.</h3>
      </div>
    </div>


    <div class="col-sm-4">
      <h2>Options</h2>

      <div class="form-group">
        <label>File Format</label>
        <selectize
          :options="fileformats.options"
          :value="options.fileformat"
          @updated="x => options.fileformat = x"
          :settings="fileformats.settings" ></selectize>
      </div>


      <button class="btn btn-primary btn-lg" @click="download">Download</button>
    </div>

  </div>
</template>

<script>
import router from '../../router'
import selectize from '../shared/Selectize'

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
        fileformat: 'csv',
        filename: 'test'
      },
      numSamples: null
    }
  },
  computed: {
    filters () {
      return this.$store.state.filters
    }
  },
  created () {
    let filters = this.$store.state.filters
    if (!filters || !filters.meta) {
      var newPath = this.$route.fullPath.replace(/\/download.*/, '')
      router.replace(newPath)
    } else {
      this.$http.post(`/api/datasets/${this.$route.params.dataset}/samples`, filters.meta).then(response => {
        this.$set(this, 'numSamples', response.body)
      }, response => {
        this.$set(this, 'numSamples', -1)
      })
    }
  },
  methods: {
    download () {
      let payload = {}
      Object.assign(payload, this.filters) // copy values from filters
      payload.options = this.options

      let form = document.createElement('form')
      form.setAttribute('method', 'post')
      form.setAttribute('action', `/api/datasets/${this.$route.params.dataset}/download`)
      form.setAttribute('target', '_blank')

      var hiddenField = document.createElement('input')
      hiddenField.setAttribute('type', 'hidden')
      hiddenField.setAttribute('name', 'query')
      hiddenField.setAttribute('value', JSON.stringify(payload))

      form.appendChild(hiddenField)

      document.body.appendChild(form)
      form.submit()
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
