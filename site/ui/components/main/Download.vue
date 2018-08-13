<template>
  <div>
    <div v-if="downloadStatus === 'creating'">
    <!-- <div v-if="true"> -->
      <h1 class="waiting">Please wait while Geney grants your data wishes...</h1>
      <div class="loader"></div>
      <button @click="cancelDownload" class="btn btn-danger btn-lg cancel-btn">Cancel</button>
    </div>
    <div v-else-if="downloadStatus === 'timeout'" class="download top justify-content-center">
      <h1>Tired of waiting?</h1>
      <p>Geney is working extra hard to get your data, but is taking a little bit longer than usual.<br>
          Enter your email here and we'll send you a download link as soon as it's ready!
      </p>
      <div class="row justify-content-center">
        <b-form @submit="submitEmailForm" @reset="cancelDownload">
          <b-form-group id="emailInputGroup"
                        label="Email address:"
                        label-for="emailInput"
                        description="We'll never share your email with anyone else.">
            <b-form-input id="emailInput"
                          type="email"
                          v-model="emailForm.email"
                          required
                          placeholder="Enter email">
            </b-form-input>
          </b-form-group>
          <b-form-group id="nameInputGroup"
                        label="Your Name:"
                        label-for="nameInput">
            <b-form-input id="nameInput"
                          type="text"
                          v-model="emailForm.name"
                          required
                          placeholder="Enter name">
            </b-form-input>
          </b-form-group>
          <b-button type="submit" variant="primary">Submit</b-button>
          <b-button type="reset" variant="danger">Cancel Download</b-button>
        </b-form>
      </div>
    </div>
    <div v-else>
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

          <div class="col-sm-6 offset-sm-3 column-selection" id="features" v-for="group in Object.keys(groups)" :key="group">
            <!-- <h4>Select {{ dataset.featureDescriptionPlural | capitalize }}</h4> -->
            <h4>Select Features: {{group}}</h4>

            <b-form-radio-group @change="x => setRadioValue(group, x)" v-model="downloadRadios[group]" stacked class="left-align">
              <b-form-radio value="all">Download All ({{group}})</b-form-radio>
              <b-form-radio value="selected">Download Selected  ({{group}})</b-form-radio>
            </b-form-radio-group>

            <div v-show="downloadRadios[group] === 'selected'">
              <selectize class="top-cushion"
                :options="groups[group]"
                :value="selectedFeatures[group]"
                @updated="x => updateFeatures(group, x)"
                :placeholder="'Begin typing to see more results'"
                :settings="getSelectizeSettings(group)"
                :errorMessage="'Please select some features or click \'Download all (' + group +')\''"
                :id="group + '-feature-select'"></selectize>
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
            </div>
          </div>

          <!-- <div class="col-sm-6 offset-sm-3 column-selection" id="metatypes">
            <h4>Select Metadata Variables</h4>

            <b-form-radio-group v-model="variablesRadioValue" stacked class="left-align">
              <b-form-radio value="all"><span class="radio-label">Download All Metadata Variables</span></b-form-radio>
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
          </div> -->

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
    </div>
  </div>
</template>

<script>
import router from '../../router';
import selectize from '../shared/Selectize';
import $ from 'jquery';
// import Vue from 'vue';
// import { mapGetters } from 'vuex';

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
          {value: 'pickle', name: 'Pickled Python Object ( .pkl )'},
          {value: 'hdf5', name: 'Hierarchical Data Format HDF5 ( .h5 )'},
          {value: 'excel', name: 'Microsoft Excel Spreadsheet ( .xlsx )'},
          {value: 'feather', name: 'Apache Feather Format ( .feather )'},
          {value: 'parquet', name: 'Apache Parquet Format ( .pq )'},
          {value: 'html', name: 'Hypertext Markup Language ( .html )'},
          {value: 'sqlite', name: 'SQLite Relational Database ( .sql )'},
          {value: 'arff', name: 'Attribute-Relation File Format ( .arff )'},
          {value: 'msgpack', name: 'MessagePack Serialization Format ( .msgpack )'},
          {value: 'stata', name: 'Stata Proprietary Format ( .dta )'},
        ],
        settings: {
          maxItems: 1,
          valueField: 'value',
        },
      },
      mimeTypes: {
        'csv': 'text/csv',
        'json': 'application/json',
        'tsv': 'text/tsv',
        'html': 'text/html',
        'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'pq': 'application/parquet',
        'feather': 'application/feather',
        'pkl': 'application/pickle',
        'msgpack': 'application/msgpack',
        'dta': 'application/stata',
        'arff': 'application/arff',
        'sql': 'application/sqlite',
        'h5': 'application/hdf5',
      },
      options: {
        fileformat: 'tsv',
        gzip: false,
      },
      numSamples: null,
      // downloadErrors: false,
      formErrors: false,
      // downloadRadios: {},
      maxQueries: 2,
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
    // ...mapGetters({
    //   downloadRadios: 'getDownloadRadios',
    // }),
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
              <span>No features selected.</span><br>
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
      const query = {filters: filters, features: [], groups: []};
      this.$http.post(`/api/datasets/${this.$route.params.dataset}/samples`, query).then(response => {
        this.$set(this, 'numSamples', response.body);
      }, response => {
        this.$set(this, 'numSamples', -1);
      });
    }
  },
  methods: {
    cancelDownload (evt) {
      if (evt) {
        evt.preventDefault();
      }
      this.$http.get(`/api/data/cancel/${this.downloadPath}`).then(response => {
        this.$store.commit('downloadPath', '');
      }, response => {
        console.log('error');
      });
      // console.log('finished canceling');
      this.$store.commit('downloadStatus', '');
      this.numQueries = 0;
    },
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
      const baseSettings = {};
      if (this.groups && this.groups[group] === null) {
        const loadfn = function (query, callback) {
          this.$http.get(
            `/api/datasets/${this.$route.params.dataset}/groups/${group}/search/${query}`
          ).then(response => {
            const items = response.data.map(item => {
              return {name: item.replace(group + '_', '')};
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
            for (var feature in this.selectedFeatures[group]) {
              features.push(group + '_' + this.selectedFeatures[group][feature]);
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
      if (!features) {
        features = [];
      }
      this.$store.commit('selectedFeatures', {group: group, value: features});
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
    submitEmailForm (evt) {
      evt.preventDefault();
      var params = {email: this.emailForm.email, name: this.emailForm.name};

      this.$http.post(`/api/data/notify/${this.downloadPath}`, params, {emulateJSON: true}).then(response => {
        console.log('sent notification information');
      }, response => {
        console.log('error');
      });

      this.$store.commit('downloadStatus', '');
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
      this.$store.commit('downloadStatus', 'creating');
      // if (this.formErrors !== null) {
      //   this.triggerErrorState();
      //   return;
      // }
      const query = this.getQuery();

      var params = {query: JSON.stringify(query), options: JSON.stringify(this.options)};

      this.$http.post(`/api/datasets/${this.$route.params.dataset}/query`, params, {emulateJSON: true}).then(response => {
        this.$store.commit('downloadPath', response.data['download_path']);
        this.getDownload(response.data['download_path']);
        // const form = document.createElement('form');
        // form.setAttribute('method', 'post');
        // form.setAttribute('action', `/api/datasets/${this.$route.params.dataset}/download/${this.downloadPath}`);
        // form.setAttribute('target', '_blank');

        // const optionsField = document.createElement('input');
        // optionsField.setAttribute('type', 'hidden');
        // optionsField.setAttribute('name', 'options');
        // optionsField.setAttribute('value', JSON.stringify(this.options));
        // form.appendChild(optionsField);
        // document.body.appendChild(form);
        // form.submit();
        // document.body.removeChild(form);
      }, response => {
        console.log('error');
      });
      // const form = document.createElement('form');
      // form.setAttribute('method', 'post');
      // form.setAttribute('action', `/api/datasets/${this.$route.params.dataset}/download`);
      // form.setAttribute('target', '_blank');

      // const queryField = document.createElement('input');
      // queryField.setAttribute('type', 'hidden');
      // queryField.setAttribute('name', 'query');
      // queryField.setAttribute('value', JSON.stringify(query));

      // const optionsField = document.createElement('input');
      // optionsField.setAttribute('type', 'hidden');
      // optionsField.setAttribute('name', 'options');
      // optionsField.setAttribute('value', JSON.stringify(this.options));

      // form.appendChild(queryField);
      // form.appendChild(optionsField);

      // document.body.appendChild(form);
      // form.submit();
      // document.body.removeChild(form);
    },
    getDownload (downloadPath) {
      // const dataset = this.$route.params.dataset;
      this.$http.get(`/api/data/status/${downloadPath}`).then(response => {
        if (response.data['status']) {
          var sleep = new Promise((resolve, reject) => {
            setTimeout(() => {
              if (this.downloadStatus === 'creating') {
                if (this.numQueries > this.maxQueries) {
                  this.numQueries = 0;
                  console.log('timeout!');
                  this.$store.commit('downloadStatus', 'timeout');
                } else {
                  // console.log('not ready yet');
                  this.getDownload(downloadPath);
                }
              }
              resolve();
            }, 2000);
          });

          Promise.all([sleep]).then(() => {
            this.numQueries += 1;
            // console.log('trying again...');
          });
        } else {
          const url = window.location.origin + response.data['url'];
          this.$store.commit('downloadStatus', '');
          var link = document.createElement('a');
          link.href = url;
          link.click();
        }
      }, response => {
        console.log('error');
      });
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
      const filteredFeatures = this.getFilteredFeatures();
      return {
        filters: this.filters,
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
    // watch: {
    //   downloadRadios: function (val) {
    //     for (let radio in val) {
    //       console.log(radio);
    //       if (radio === 'all') {
    //         this.formErrors = true;
    //       }
    //     }
    //   },
    // },
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
