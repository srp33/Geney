<template>
  <div>
    <div class="download top row justify-content-center" v-if="filters">
      <div class="col-12">
        <h1>Filter Columns</h1>
        <div v-if="numSamples != null">
          <h3 v-if="numSamples > 0" id="num-samples-selected">You have selected {{ numSamples }} samples.</h3>
          <span v-else-if="numSamples === 0" id="num-samples-selected">
            <h3>Uh oh. Your filters didn't match any samples!</h3>
            <h4>Click <router-link :to="'/dataset/' + dataset.id + '/filter'">here</router-link> to edit your filters</h4>
          </span>
          <h3 v-else id="num-samples-error">Unable to retreive number of samples.</h3>
        </div>
        <h2>Select Features:</h2>
        <div class="col-lg-6 offset-sm-3 column-selection" id="features" v-for="group in Object.keys(groups)" :key="group">
          <!-- <h4>Select {{ dataset.featureDescriptionPlural | capitalize }}</h4> -->
          <b-row align-h="end">
            <b-col align-self="center" cols="auto">
              <h5>{{group.replace(/_/g, ' ')}}:</h5>
            </b-col>

            <b-col cols="6">
              <b-form-radio-group @change="x => setRadioValue(group, x)" v-model="downloadRadios[group]" stacked class="left-align">
                <b-form-radio value="all">Download All</b-form-radio>
                <b-form-radio value="selected">Download Selected</b-form-radio>
              </b-form-radio-group>
            </b-col>
          </b-row>

          <b-row v-show="downloadRadios[group] === 'selected'" align-h="center">
            <b-col cols="8">
              <selectize class="top-cushion"
                :options="groups[group]"
                :value="selectedFeatures[group]"
                @updated="x => updateFeatures(group, x)"
                :placeholder="'Begin typing to see more results or leave blank for none'"
                :settings="getSelectizeSettings(group)"
                :errorMessage="'Please select some features or click \'Download all (' + group +')\''"
                :id="group + '-feature-select'"></selectize>
            </b-col>
          </b-row>
        </div>
      </div>

      <div class="col-sm-4">
        <div class="col-12">
          <h2>Continue with these filters?</h2>
          <button @click="filterColumns" class="btn btn-primary btn-lg confirm-btn">
            Confirm
            <span v-if="formErrors" v-b-tooltip="downloadTooltipSettings"></span>
          </button>
        </div>

        <!-- <div class="col-12" id="plot-container">
          <button class="btn btn-primary btn-lg" @click="plot" id="plot-btn" :disabled="plotlyErrors">
            Visualize with plot.ly
            <span v-if="plotlyErrors" v-b-tooltip="plotlyTooltipSettings"></span>
          </button>
        </div> -->

        <!-- <div v-if="geneSets !== null && Object.keys(geneSets).length > 0">
                <selectize
                  :options="geneSets"
                  :value="selectedSets"
                  @updated="updateSets"
                  :placeholder="$options.filters.capitalize(dataset.featureDescription) + ' Sets - begin typing to see more results'"
                  :settings="{}"
                  id="feature-select"></selectize>
                  *Information about gene sets can be found on the Pathway Commons <a href="http://www.pathwaycommons.org/" target="_blank">website</a>.
                  <h5>Total Number of {{ dataset.featureDescriptionPlural | capitalize }} Selected: {{ numFeatures }}</h5>
              </div> -->

        <div class="col-12">
          <router-link class="btn btn-secondary" style="margin-top: 10px;" :to="`/dataset/${dataset.id}/filter`">Back</router-link>
        </div>
      </div>
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
      formErrors: false,
      maxQueries: 30,
      secondsBetweenQueries: 2,
      numQueries: 0,
      emailForm: {
        email: '',
        name: '',
        checked: [],
      },
    };
  },
  computed: {
    downloadRadios () {
      return this.$store.state.downloadRadios;
    },
    downloadStatus () {
      return this.$store.state.downloadStatus;
    },
    downloadPath () {
      return this.$store.state.downloadPath;
    },
    groups () {
      return this.$store.state.groups;
    },
    numSamples () {
      return this.$store.state.numSamples;
    },
    numColumns () {
      return this.$store.state.numColumns;
    },
    sampleFile () {
      return this.$store.state.sampleFile;
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
    selectedFeatures () {
      return this.$store.state.selectedFeatures;
    },
    selectedSets () {
      return this.$store.state.selectedSets;
    },
    selectedVariables () {
      return this.$store.state.selectedVariables;
    },
    numFeatures () {
      return this.getFeatures().length;
    },
    numDataPoints () {
      if (this.numColumns && this.numSamples) {
        return this.numColumns * this.numSamples;
      } else {
        return null;
      }
    },
    geneSets () {
      if (this.metaData.geneSets) {
        var options = Object.keys(this.metaData.geneSets);
        const items = options.map(item => {
          return {name: item};
        });
        for (var set in items) {
          var numGenes = this.metaData.geneSets[items[set]['name']]['genes'].length;
          items[set]['name'] = items[set]['name'] + ' (' + numGenes + ')';
          // console.log(numGenes);
        }
        return items;
      } else {
        return null;
      }
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
              <span>No features selected.</span><br>
            `;
          }
        }
      }

      return settings;
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
      const newPath = this.$route.fullPath.replace(/\/columns.*/, '');
      router.replace(newPath);
    } else {
      this.$http.post(`/api/datasets/${this.$route.params.dataset}/samples`, filters).then(response => {
        this.$store.commit('sampleData', response.data);
      }, response => {
        this.$store.commit('numSamples', -1);
      });
    }
  },
  methods: {
    getFormErrors () {
      let valid = false;
      let errors = {};
      errors.features = true;
      const filteredFeatures = this.getFilteredFeatures();
      if (filteredFeatures.groups.length > 0 || filteredFeatures.features.length > 0) {
        valid = true;
        errors = {};
      }
      if (this.numSamples === 0) {
        valid = false;
        errors.numSamples = true;
      }
      return valid ? null : errors;
    },
    getSelectizeSettings (group) {
      const baseSettings = {valueField: 'value'};
      if (this.groups && this.groups[group] === null) {
        const loadfn = function (query, callback) {
          this.$http.get(
            `/api/datasets/${this.$route.params.dataset}/groups/${group}/search/${query}`
          ).then(response => {
            const items = response.data.map(item => {
              return {name: item[1], value: item};
            });
            callback(items);
          }, failedResponse => {
            callback();
          });
        };
        baseSettings.load = loadfn.bind(this);
        return baseSettings;
      } else {
        return baseSettings;
      }
    },
    getFilteredFeatures () {
      var features = [];
      var groups = [];
      for (var group in this.groups) {
        if (this.downloadRadios[group] === 'all') {
          groups = groups.concat(group);
          // var values = [];
          // this.groups[group].forEach(element => {
          //   values.push(element.name);
          // });
          // features = features.concat(values);
        } else {
          if (this.selectedFeatures[group]) {
            for (var i in this.selectedFeatures[group]) {
              features.push(this.selectedFeatures[group][i]);
            }
            // features = features.concat(this.selectedFeatures[group]);
          }
        }
      }
      return {groups: groups, features: features};
    },
    setRadioValue (group, value) {
      this.$store.commit('downloadRadios', {group: group, value: value});
      this.formErrors = this.getFormErrors();
      this.$forceUpdate();
    },
    updateFeatures (group, features) {
      var featureIndices = [];
      if (!features) {
        features = [];
      }
      for (let i in features) {
        featureIndices = featureIndices.concat(features[i].split(',')[0]);
      }
      this.$store.commit('selectedFeatures', {group: group, value: featureIndices});
      this.formErrors = this.getFormErrors();
      this.$forceUpdate();
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
    filterColumns () {
      const query = this.getQuery();
      console.log(query);
      this.$http.post(`/api/datasets/${this.$route.params.dataset}/columns`, query).then(response => {
        this.$store.commit('columnData', response.data);
        this.download();
      }, response => {
        console.log('error');
      });
    },
    download () {
      if (this.numDataPoints <= this.$store.state.maxDataPoints) {
        if (this.formErrors !== null) {
          this.triggerErrorState();
          return;
        }
        router.push(`/dataset/${this.$route.params.dataset}/filter/download`);
      } else {
        this.$store.commit('addAlert', {
          variant: 'danger',
          message: 'Too many datapoints selected.\nPlease add more filters or remove features\nto fit your data within ' +
          this.$store.state.maxDataPoints + ' data points (currently requesting ' + this.numDataPoints +
          ' data points).',
          show: 15,
        });
      }
    },
    getQuery () {
      const filteredFeatures = this.getFilteredFeatures();
      return {
        sampleFile: this.sampleFile,
        features: filteredFeatures.features,
        groups: filteredFeatures.groups,
      };
    },
    getFeatures () {
      var features = new Set(this.selectedFeatures);
      if (this.metaData.geneSets && this.selectedSets.length > 0) {
        var geneSets = this.metaData.geneSets;
        for (var i = 0; i < this.selectedSets.length; i++) {
          features = this.union(features, new Set(geneSets[this.selectedSets[i].replace(/( \(\d*\)$)/g, '')]['genes']));
        }
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

<style lang="scss">
h1, h2, h3, h4 {
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
.waiting {
  margin-top: 7rem;
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

.top-cushion {
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

.left-align {
  text-align: left;
}
</style>
