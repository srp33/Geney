<template>

  <div class="download top row justify-content-center" v-if="filters">
    <div class="col-12">
      <h1>Download</h1>
      <div v-if="numSamples != null">
        <h3 v-if="numSamples >= 0" id="num-samples-selected">You have selected {{ numSamples }} samples.</h3>
        <h3 v-else id="num-samples-error">Unable to retreive number of samples.</h3>
      </div>

      <div class="col-sm-6 offset-sm-3 column-selection" id="features">
        <h4>Select {{ dataset.featureDescriptionPlural | capitalize }}</h4>

        <b-form-radio-group v-model="radios.features" stacked>
          <b-form-radio value="all">Download All {{ dataset.featureDescriptionPlural | capitalize }}</b-form-radio>
          <b-form-radio value="selected">Download Selected {{ dataset.featureDescriptionPlural | capitalize }}</b-form-radio>
        </b-form-radio-group>

        <div v-show="radios.features === 'selected'">
          <selectize
            :options="metaData.features.options"
            :value="selectedFeatures"
            @updated="updateFeatures"
            :placeholder="'All ' + $options.filters.capitalize(dataset.featureDescriptionPlural)"
            :settings="getSelectizeSettings('features', metaData.features)"
            errorMessage="Required"
            id="feature-select"></selectize>
        </div>
      </div>

      <div class="col-sm-6 offset-sm-3 column-selection" id="metatypes">
        <h4>Select Variables</h4>

        <b-form-radio-group v-model="radios.variables" stacked>
          <b-form-radio value="all">Download All Variables</b-form-radio>
          <b-form-radio value="selected">Download Selected Variables</b-form-radio>
        </b-form-radio-group>

        <div v-show="radios.variables === 'selected'">
          <selectize
            :options="metaTypes"
            :value="selectedVariables"
            placeholder="Variables"
            @updated="updateVariables"
            :settings="metaTypeSettings"
            errorMessage="Required"
            id="variable-select"></selectize>
        </div>
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
      <div class="col-12">
        <b-form-checkbox id="checkbox1"
                      v-model="options.gzip">
          Gzip Downloaded File
        </b-form-checkbox>
      </div>

      <button class="btn btn-primary btn-lg" @click="download" id="download-btn">Download</button>
    </div>

  </div>
</template>

<script>
import router from '../../router';
import selectize from '../shared/Selectize';
import $ from 'jquery';

export default {
  name: 'download',
  components: {
    selectize,
  },
  data () {
    return {
      fileformats: {
        options: [
          {value: 'tsv', name: 'Tab Separated Values ( .tsv )'},
          {value: 'csv', name: 'Comma Separated Values ( .csv )'},
          {value: 'json', name: 'JavaScript Object Notation ( .json )'},
        ],
        settings: {
          maxItems: 1,
          valueField: 'value',
        },
      },
      options: {
        fileformat: 'tsv',
        gzip: false,
      },
      numSamples: null,
      radios: {
        features: 'selected',
        variables: 'selected',
      },
    };
  },
  computed: {
    filters () {
      return this.$store.state.filters;
    },
    dataset () {
      return this.$store.state.dataset;
    },
    metaData () {
      return this.$store.state.metaData;
    },
    // this is a copy and paste from Filter.vue
    // TODO: move these two functions to their own module so it's not duplicated
    metaTypes () {
      if (this.metaData && this.metaData.meta) {
        return Object.keys(this.metaData.meta).map(x => ({'name': x}));
      } else if (this.$store.state.filters && this.$store.state.filters.meta) {
        return Object.keys(this.$store.state.filters.meta).map(val => ({ name: val }));
      } else {
        return [];
      }
    },
    metaTypeSettings () {
      const baseSettings = {
        required: true,
      };
      if (this.metaData && this.metaData.meta === null) {
        const loadfn = function (query, callback) {
          this.$http.get(
            `/api/datasets/${this.$route.params.dataset}/meta/search/${query}`
          ).then(response => {
            const items = response.data.map(item => {
              return {name: item};
            });
            callback(items);
          }, failedResponse => {
            console.log(failedResponse);
            callback();
          });
        };
        baseSettings.load = loadfn.bind(this);
        return baseSettings;
      } else {
        return baseSettings;
      }
    },
    selectedFeatures () {
      return this.$store.state.selectedFeatures;
    },
    selectedVariables () {
      return this.$store.state.selectedVariables;
    },
  },
  created () {
    const filters = this.$store.state.filters;
    if (!filters) {
      const newPath = this.$route.fullPath.replace(/\/download.*/, '');
      router.replace(newPath);
    } else {
      const query = {filters: filters, features: [], metaTypes: []};
      this.$http.post(`/api/datasets/${this.$route.params.dataset}/samples`, query).then(response => {
        this.$set(this, 'numSamples', response.body);
      }, response => {
        this.$set(this, 'numSamples', -1);
      });
    }
  },
  mounted () {
  },
  methods: {
    updateFeatures (features) {
      if (!features) {
        features = [];
      }
      this.$store.commit('selectedFeatures', features);
    },
    updateVariables (variables) {
      if (!variables) {
        variables = [];
      }
      this.$store.commit('selectedVariables', variables);
    },
    // this is a copy and paste from Filter.vue
    // TODO: move this function to it's own module so it's not duplicated
    getSelectizeSettings (metaType, metaData) {
      const settings = {
        required: true,
      };
      if (metaData.options === null) {
        const loadfn = function (query, callback) {
          this.$http.get(
            `/api/datasets/${this.$route.params.dataset}/meta/${metaType}/search/${query}`
          ).then(response => {
            const items = response.data.map(item => {
              return {name: item};
            });
            callback(items);
          }, failedResponse => {
            console.log(failedResponse);
            callback();
          });
        };
        settings.load = loadfn.bind(this);
      }
      return settings;
    },
    valid () {
      let valid = true;
      if (this.radios.features === 'selected' && this.selectedFeatures.length === 0) {
        // fake the input box losing focus so it will turn red
        $(this.$el).find('#feature-select').find('.selectize-input').trigger('focusout');
        valid = false;
      }
      if (this.radios.variables === 'selected' && this.selectedVariables.length === 0) {
        $(this.$el).find('#variable-select').find('.selectize-input').trigger('focusout');
        valid = false;
      }
      return valid;
    },
    download () {
      console.log(this.valid());
      if (!this.valid()) {
        return;
      }
      let metaTypes, features;

      switch (this.radios.variables) {
        case 'all':
          metaTypes = [];
          break;
        case 'selected':
          metaTypes = this.selectedVariables;
          break;
      }

      switch (this.radios.features) {
        case 'all':
          features = [];
          break;
        case 'selected':
          features = this.selectedFeatures;
          break;
      }

      const query = {
        filters: this.filters,
        features: features,
        metaTypes: metaTypes,
      };

      const form = document.createElement('form');
      form.setAttribute('method', 'post');
      form.setAttribute('action', `/api/datasets/${this.$route.params.dataset}/download`);
      form.setAttribute('target', '_blank');

      const queryField = document.createElement('input');
      queryField.setAttribute('type', 'hidden');
      queryField.setAttribute('name', 'query');
      queryField.setAttribute('value', JSON.stringify(query));

      const optionsField = document.createElement('input');
      optionsField.setAttribute('type', 'hidden');
      optionsField.setAttribute('name', 'options');
      optionsField.setAttribute('value', JSON.stringify(this.options));

      form.appendChild(queryField);
      form.appendChild(optionsField);

      document.body.appendChild(form);
      form.submit();
      document.body.removeChild(form);
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
#download-btn {
  margin-top: 25px;
}
.column-selection {
  margin-top: 25px;
  margin-bottom: 25px;
  h4 {
    font-weight: 300;
  }
}
</style>
