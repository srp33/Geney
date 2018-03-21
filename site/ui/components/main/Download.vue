<template>

  <div class="download top row justify-content-center" v-if="filters">
    <div class="col-12">
      <h1>Download</h1>
      <div v-if="numSamples != null">
        <h3 v-if="numSamples > 0" id="num-samples-selected">You have selected {{ numSamples }} samples.</h3>
        <span v-else-if="numSamples === 0" id="num-samples-selected">
          <h3>Uh oh. Your filters didn't match any samples!</h3>
          <h4>Click <router-link :to="'/dataset/' + dataset.id + '/filter'">here</router-link> to edit your filters</h4>
        </span>
        <h3 v-else id="num-samples-error">Unable to retreive number of samples.</h3>
      </div>

      <div class="col-sm-6 offset-sm-3 column-selection" id="features">
        <h4>Select {{ dataset.featureDescriptionPlural | capitalize }}</h4>

        <b-form-radio-group v-model="featuresRadioValue" stacked>
          <b-form-radio value="all">Download All {{ dataset.featureDescriptionPlural | capitalize }}</b-form-radio>
          <b-form-radio value="selected">Download Selected {{ dataset.featureDescriptionPlural | capitalize }} and/or {{ dataset.featureDescription | capitalize}} sets</b-form-radio>
        </b-form-radio-group>

        <div v-show="featuresRadioValue === 'selected'">
          <selectize class="top-cussion"
            :options="metaData.features.options"
            :value="selectedFeatures"
            @updated="updateFeatures"
            :placeholder="'Individual ' + $options.filters.capitalize(dataset.featureDescriptionPlural) + ' - begin typing to see more results'"
            :settings="getSelectizeSettings('features', metaData.features)"
            :errorMessage="'Please select some ' + dataset.featureDescriptionPlural + ' or click \'Download all ' + $options.filters.capitalize(dataset.featureDescriptionPlural) +'\''"
            id="feature-select"></selectize>
          <div v-if="geneSets !== null">
            <selectize v-if="geneSets !== null"
              :options="geneSets"
              :value="selectedSets"
              @updated="updateSets"
              :placeholder="$options.filters.capitalize(dataset.featureDescription) + ' Sets - begin typing to see more results'"
              :settings="{}"
              id="feature-select"></selectize>
              *Information about gene sets can be found on the Pathway Commons <a href="http://www.pathwaycommons.org/" target="_blank">website</a>.
              <h5>Total Number of {{ dataset.featureDescriptionPlural | capitalize }} Selected: {{ numFeatures }}</h5>
          </div>
        </div>
      </div>

      <div class="col-sm-6 offset-sm-3 column-selection" id="metatypes">
        <h4>Select Metadata Variables</h4>

        <b-form-radio-group v-model="variablesRadioValue" stacked>
          <b-form-radio value="all">Download All Metadata Variables</b-form-radio>
          <b-form-radio value="selected">Download Selected Metadata Variables</b-form-radio>
        </b-form-radio-group>

        <div v-show="variablesRadioValue === 'selected'">
          <selectize
            :options="metaTypes"
            :value="selectedVariables"
            placeholder="Metadata Variables - begin typing to see more results"
            @updated="updateVariables"
            :settings="metaTypeSettings"
            errorMessage="Please select from variables or click 'Download All Metadata Variables'"
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

      <div class="col-12">
        <button class="btn btn-primary btn-lg" @click="download" id="download-btn" :disabled="formErrors">
          Download
          <span v-if="formErrors" v-b-tooltip="downloadTooltipSettings"></span>
        </button>
      </div>

      <div class="col-12" id="plot-container">
        <button class="btn btn-primary btn-lg" @click="plot" id="plot-btn" :disabled="plotlyErrors">
          Visualize with plot.ly
          <span v-if="plotlyErrors" v-b-tooltip="plotlyTooltipSettings"></span>
        </button>
      </div>

      <div class="col-12">
        <router-link class="btn btn-secondary" :to="`/dataset/${dataset.id}/filter`">Back</router-link>
      </div>

    </div>

  </div>
</template>

<script>
import router from '../../router';
import selectize from '../shared/Selectize';
import $ from 'jquery';

// based on some rough napkin math
// 20 characters per item, with a limit of 5MB is about 25000, and we'll give ourselves some wiggleroom
const MAX_ITEMS_PLOTLY = 22500;
const MAX_COLS_PLOTLY = 25;

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
    };
  },
  computed: {
    geneSets () {
      if (this.metaData.geneSets) {
        var options = Object.keys(this.metaData.geneSets);
        const items = options.map(item => {
          return {name: item};
        });
        return items;
      } else {
        return null;
      }
    },
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
    selectedSets () {
      return this.$store.state.selectedSets;
    },
    selectedVariables () {
      return this.$store.state.selectedVariables;
    },
    downloadTooltipSettings () {
      const settings = {
        html: true,
        placement: 'top',
        title: '',
      };

      if (this.formErrors) {
        if (this.formErrors.numSamples) {
          settings.title += `
            <span>Your filters did not match any samples. No data to download.</span><br>
          `;
        } else {
          if (this.formErrors.features) {
            settings.title += `
              <span>No ${this.dataset.featureDescriptionPlural} selected.</span><br>
            `;
          }

          if (this.formErrors.variables) {
            settings.title += `
              <span>No variables selected.</span><br>
            `;
          }
        }
      }

      return settings;
    },
    plotlyTooltipSettings () {
      const settings = Object.assign({}, this.downloadTooltipSettings);
      settings.container = '#plot-container';
      if (this.plotlyErrors) {
        if (this.plotlyErrors.maxItems) {
          settings.title += `
            <span>Too many results to visualize with plot.ly. Please filter your data more.</span><br>
          `;
        }
        if (this.plotlyErrors.maxColumns) {
          settings.title += `
            <span>${this.numColumns} ${this.dataset.featureDescriptionPlural} and variables selected. No more than ${MAX_COLS_PLOTLY} allowed.</span><br>
          `;
        }
      }
      return settings;
    },
    formErrors () {
      let valid = true;
      let errors = {};
      if (this.featuresRadioValue === 'selected' && this.selectedFeatures.length === 0 && this.selectedSets.length === 0) {
        valid = false;
        errors.features = true;
      }
      if (this.variablesRadioValue === 'selected' && this.selectedVariables.length === 0) {
        valid = false;
        errors.variables = true;
      }
      if (this.numSamples === 0) {
        valid = false;
        errors.numSamples = true;
      }
      return valid ? null : errors;
    },
    plotlyErrors () {
      let valid = this.formErrors === null;
      let errors = valid ? {} : this.formErrors;
      if ((this.numSamples * this.numColumns) > MAX_ITEMS_PLOTLY) {
        errors.maxItems = true;
        valid = false;
      }
      if (this.numColumns > MAX_COLS_PLOTLY) {
        errors.maxColumns = true;
        valid = false;
      }
      return valid ? null : errors;
    },
    numColumns () {
      let numFeatures, numVariables;

      switch (this.featuresRadioValue) {
        case 'all':
          numFeatures = this.dataset.numFeatures;
          break;
        case 'selected':
          numFeatures = this.selectedVariables.length;
          break;
      }

      switch (this.variablesRadioValue) {
        case 'all':
          numVariables = this.dataset.numMetaTypes;
          break;
        case 'selected':
          numVariables = this.selectedFeatures.length;
          break;
      }

      return numFeatures + numVariables;
    },
    numFeatures () {
      return this.getFeatures().length;
    },
    variablesRadioValue: {
      get () {
        return this.$store.state.downloadRadios.variables;
      },
      set (value) {
        this.$store.commit('variablesRadioValue', value);
      },
    },
    featuresRadioValue: {
      get () {
        return this.$store.state.downloadRadios.features;
      },
      set (value) {
        this.$store.commit('featuresRadioValue', value);
      },
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
    updateSets (sets) {
      if (!sets) {
        sets = [];
      }
      this.$store.commit('selectedSets', sets);
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
      const settings = {};
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
    triggerErrorState () {
      if (!this.formErrors) {
        return;
      }
      if (this.formErrors.features) {
        // fake the input box losing focus so it will turn red
        $(this.$el).find('#feature-select').find('.selectize-input').trigger('focusout');
      }
      if (this.formErrors.variables) {
        $(this.$el).find('#variable-select').find('.selectize-input').trigger('focusout');
      }
    },
    download () {
      if (this.formErrors !== null) {
        this.triggerErrorState();
        return;
      }
      const query = this.getQuery();

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
    plot () {
      if (this.formErrors !== null) {
        this.triggerErrorState();
        return;
      }
      const query = this.getQuery();

      this.$http.post(`/api/datasets/${this.$route.params.dataset}/link`, query).then(response => {
        const data = response.data;
        if (data.link) {
          const linkElem = document.createElement('a');
          linkElem.setAttribute('href', `https://plot.ly/external/?url=${data.link}`);
          linkElem.setAttribute('target', '_blank');
          document.body.appendChild(linkElem);
          linkElem.click();
          document.body.removeChild(linkElem);
        } else {
          this.$store.commit('addAlert', {
            variant: 'danger',
            message: 'Error generating link. Please try again later.',
            show: 3,
          });
        }
      }, error => {
        console.error(error);
        this.$store.commit('addAlert', {
          variant: 'danger',
          message: 'Error generating link. Please try again later.',
          show: 3,
        });
      });
    },
    getQuery () {
      let metaTypes, features;

      switch (this.variablesRadioValue) {
        case 'all':
          metaTypes = [];
          break;
        case 'selected':
          metaTypes = this.selectedVariables;
          break;
      }

      switch (this.featuresRadioValue) {
        case 'all':
          features = [];
          break;
        case 'selected':
          if (this.selectedSets.length > 0) {
            features = this.getFeatures();
          } else {
            features = this.selectedFeatures;
          }
          break;
      }

      return {
        filters: this.filters,
        features: features,
        metaTypes: metaTypes,
      };
    },
    getFeatures () {
      var features = new Set(this.selectedFeatures);
      console.log([...features]);
      if (this.metaData.geneSets && this.selectedSets.length > 0) {
        var geneSets = this.metaData.geneSets;
        for (var i = 0; i < this.selectedSets.length; i++) {
          features = this.union(features, new Set(geneSets[this.selectedSets[i]]['genes']));
        }
        console.log([...features]);
      }
      return [...features];
    },
    union (setA, setB) {
      for (var elem of setB) {
        setA.add(elem);
      }
      return setA;
    },
  },
};
</script>

<style lang="scss" scoped>
h1, h2, h3 {
  font-weight: normal;
}
h5 {
  margin-top: 10px;
}
.form-group {
  label {
    font-size: 1.25em;
  }
}
#download-btn, #plot-btn {
  margin-top: 25px;
  position: relative;
  span {
    position: absolute;
    top: 0px;
    left: 0px;
    height: 100%;
    width: 100%;
  }
}
#plot-btn {
  margin-bottom: 25px;
}

.top-cussion {
  margin-top: 10px;
}

.column-selection {
  margin-top: 25px;
  margin-bottom: 25px;
  h4 {
    font-weight: 300;
  }
}

#plot-container {
  .tooltip-inner {
    max-width: 1000px !important;
  }
}
</style>
