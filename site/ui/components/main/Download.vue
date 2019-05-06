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
          <div v-if="numSamples != null && numColumns != null">
            <h3 v-if="numSamples > 0" id="num-samples-selected">
              You have selected {{ numSamples }} samples and {{ numColumns }} features.<br>
              Your download will contain {{ numDataPoints }} data points.<br>
            </h3>
            <span v-else-if="numSamples === 0" id="num-samples-selected">
              <h3>Uh oh. Your filters didn't match any samples!</h3>
              <h4>Click <router-link :to="'/dataset/' + dataset.id + '/filter'">here</router-link> to edit your filters</h4>
            </span>
            <h3 v-else id="num-samples-error">Unable to retreive number of samples.</h3>
          </div>
        </div>


        <div class="col-sm-4" style="margin-top: 20px;">
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

          <div class="col-12">
            <router-link class="btn btn-secondary" style="margin-top: 10px;" :to="`/dataset/${dataset.id}/filter`">Back</router-link>
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
          // {value: 'csv', name: 'Comma Separated Values ( .csv )'},
          // {value: 'json', name: 'JavaScript Object Notation ( .json )'},
          // {value: 'hdf5', name: 'Hierarchical Data Format HDF5 ( .h5 )'},
          // {value: 'excel', name: 'Microsoft Excel Spreadsheet ( .xlsx )'},
          // {value: 'feather', name: 'Apache Feather Format ( .feather )'},
          // {value: 'parquet', name: 'Apache Parquet Format ( .pq )'},
          // {value: 'arff', name: 'Attribute-Relation File Format ( .arff )'},
          // {value: 'msgpack', name: 'MessagePack Serialization Format ( .msgpack )'},
        ],
        settings: {
          maxItems: 1,
          valueField: 'value',
        },
      },
      mimeTypes: {
        // 'csv': 'text/csv',
        // 'json': 'application/json',
        'tsv': 'text/tsv',
        // 'html': 'text/html',
        // 'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        // 'pq': 'application/parquet',
        // 'feather': 'application/feather',
        // 'pkl': 'application/pickle',
        // 'msgpack': 'application/msgpack',
        // 'dta': 'application/stata',
        // 'arff': 'application/arff',
        // 'sql': 'application/sqlite',
        // 'h5': 'application/hdf5',
      },
      options: {
        fileformat: 'tsv',
        gzip: false,
      },
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
    columnIndicesFile () {
      return this.$store.state.columnIndicesFile;
    },
    columnNamesFile () {
      return this.$store.state.columnNamesFile;
    },
    filters () {
      return this.$store.state.filters;
    },
    dataset () {
      return this.$store.state.dataset;
    },
    selectedFeatures () {
      return this.$store.state.selectedFeatures;
    },
    selectedSets () {
      return this.$store.state.selectedSets;
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
  },
  created () {
    const filters = this.$store.state.filters;
    if (!filters) {
      const newPath = this.$route.fullPath.replace(/\/download.*/, '');
      router.replace(newPath);
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
      if (this.numDataPoints <= this.$store.state.maxDataPoints) {
        this.$store.commit('downloadStatus', 'creating');
        const query = {
          sampleFile: this.sampleFile,
          columnIndicesFile: this.columnIndicesFile,
          columnNamesFile: this.columnNamesFile,
        };
        console.log(query);
        this.$http.post(`/api/datasets/${this.$route.params.dataset}/download`, query).then(response => {
          const downloadPath = response.data.downloadPath;
          console.log(downloadPath);
          this.getDownload(downloadPath);
        }, response => {
          console.log('error');
        });
      } else {
        this.$store.commit('downloadStatus', 'datapointError');
        this.$store.commit('addAlert', {
          variant: 'danger',
          message: 'Too many datapoints selected.\nPlease add more filters or remove features\nto fit your data within ' +
          this.$store.state.maxDataPoints + ' data points (currently requesting ' + this.numDataPoints +
          ' data points).',
          show: 15,
        });
      }
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
    getQuery () {
      const filteredFeatures = this.getFilteredFeatures();
      return {
        sampleFile: this.sampleFile,
        features: filteredFeatures.features,
        groups: filteredFeatures.groups,
      };
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
