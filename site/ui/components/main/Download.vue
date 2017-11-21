<template>

  <div class="download top row justify-content-center" v-if="filters">
    <div class="col-12">
      <h1>Download</h1>
      <div v-if="numSamples != null">
        <h3 v-if="numSamples >= 0" id="num-samples-selected">You have selected {{ numSamples }} samples.</h3>
        <h3 v-else id="num-samples-error">Unable to retreive number of samples.</h3>
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


      <button class="btn btn-primary btn-lg" @click="download" id="download-btn">Download</button>
    </div>

  </div>
</template>

<script>
import router from '../../router';
import selectize from '../shared/Selectize';

export default {
  name: 'download',
  components: {
    selectize,
  },
  data () {
    return {
      fileformats: {
        options: [
          {value: 'csv', name: 'Comma Separated Values ( .csv )'},
          {value: 'tsv', name: 'Tab Separated Values ( .tsv )'},
          {value: 'json', name: 'JavaScript Object Notation ( .json )'},
        ],
        settings: {
          maxItems: 1,
          valueField: 'value',
        },
      },
      options: {
        fileformat: 'csv',
      },
      numSamples: null,
    };
  },
  computed: {
    filters () {
      return this.$store.state.filters;
    },
  },
  created () {
    const filters = this.$store.state.filters;
    if (!filters || !filters.meta) {
      const newPath = this.$route.fullPath.replace(/\/download.*/, '');
      router.replace(newPath);
    } else {
      console.log(`/api/datasets/${this.$route.params.dataset}/samples`);
      this.$http.post(`/api/datasets/${this.$route.params.dataset}/samples`, filters).then(response => {
        this.$set(this, 'numSamples', response.body);
      }, response => {
        this.$set(this, 'numSamples', -1);
      });
    }
  },
  mounted () {
  },
  methods: {
    download () {
      const payload = {};
      Object.assign(payload, this.filters); // copy values from filters
      payload.options = this.options;

      const form = document.createElement('form');
      form.setAttribute('method', 'post');
      form.setAttribute('action', `/api/datasets/${this.$route.params.dataset}/download`);
      form.setAttribute('target', '_blank');

      const hiddenField = document.createElement('input');
      hiddenField.setAttribute('type', 'hidden');
      hiddenField.setAttribute('name', 'query');
      hiddenField.setAttribute('value', JSON.stringify(payload));

      form.appendChild(hiddenField);

      document.body.appendChild(form);
      form.submit();
    },
  },
};
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
