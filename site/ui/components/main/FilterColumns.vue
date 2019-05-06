<template>
  <div>
    <div class="download top row justify-content-center" v-if="filters">
      <div class="col-12">
        <h1>Filter Features</h1>
        <div v-if="numSamples != null">
          <h3 v-if="numSamples > 0" id="num-samples-selected">You have selected {{ numSamples }} samples.</h3>
          <span v-else-if="numSamples === 0" id="num-samples-selected">
            <h3>Uh oh. Your filters didn't match any samples!</h3>
            <h4>Click <router-link :to="'/dataset/' + dataset.id + '/filter'">here</router-link> to edit your filters</h4>
          </span>
          <h3 v-else id="num-samples-error">Unable to retreive number of samples.</h3>
        </div>
        <h2>Select Features:</h2>
        <div class="col-lg-6 offset-sm-3 column-selection">
          <b-table bordered :fields="fields" :items="items" v-if="items && items !== {}">
            <template slot="name" slot-scope="data">
              {{data.value.replace(/_/g, ' ')}}
            </template>
            <template slot="Features" slot-scope="data">
              <b-form-select v-model="selected[data.item.name].value" @change="x => selectFeatures(data.item.name, x)" :options="selectionOptions"></b-form-select>
            </template>
            <template slot="row-details" slot-scope="data">
              <selectize class="top-cushion"
                  :options="groups[data.item.name]"
                  :value="getValues(data.item.name)"
                  @updated="x => updateFeatures(data.item.name, x)"
                  :placeholder="'Begin typing to see more results or leave blank for none'"
                  :settings="getSelectizeSettings(data.item.name)"
                  :errorMessage="'Please select some features or click \'Download all (' + data.item.name +')\''"
                  :id="data.item.name + '-feature-select'"></selectize>
            </template>
          </b-table>
        </div>
        <div class="col-lg-6 offset-sm-3 column-selection pathways" id="gene-sets" v-if="pathways">
          <b-row align-h="between">
            <b-col cols="1">
              <h5>Pathways:</h5>
            </b-col>

            <b-col cols="auto">
              <selectize class="top-cushion"
                :options="pathways"
                :value="selectedPathways"
                @updated="x => updatePathways(x)"
                :placeholder="'Begin typing to see more results or leave blank for none'"
                :settings="pathwaySettings"
                errorMessage="Please select some pathways or leave blank for none"
                id="pathways-select"></selectize>
            </b-col>
          </b-row>
          *Information about pathways can be found on the Pathway Commons <a href="http://www.pathwaycommons.org/" target="_blank">website</a>.
                  <h5>Total Number of Features Selected: 5</h5>

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
      pathways: null,
      selected: {},
      selectionOptions: [
        { value: 'all', text: 'Download all columns in group' },
        { value: 'none', text: 'Download none of the columns in group' },
        { value: 'selected', text: 'Download select columns from group' },
      ],
      pathwaySettings: {
        labelField: 'name',
        valueField: 'name',
      },
      emailForm: {
        email: '',
        name: '',
        checked: [],
      },
      fields: [
        { key: 'name', label: 'Group' },
        'Features',
      ],
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
    selectedPathways () {
      return this.$store.state.selectedPathways;
    },
    items () {
      if (!this.selected) {
        return [];
      } else {
        return Object.keys(this.selected).map(group => {
          if (this.selected[group].value === 'all') {
            return {name: group, _rowVariant: 'success'};
          } else if (this.selected[group].value === 'none') {
            return {name: group, _rowVariant: 'warning'};
          } else {
            return {name: group, _showDetails: true, _rowVariant: 'success'};
          }
        });
      }
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
  },
  created () {
    const filters = JSON.parse(JSON.stringify(this.$store.state.filters));
    this.selected = JSON.parse(JSON.stringify(this.selectedFeatures));
    if (!filters || !this.selected) {
      const newPath = this.$route.fullPath.replace(/\/columns.*/, '');
      router.replace(newPath);
    } else {
      this.getPathways();
      this.$http.post(`/api/datasets/${this.$route.params.dataset}/samples`, filters).then(response => {
        this.$store.commit('sampleData', response.data);
      }, response => {
        this.$store.commit('numSamples', -1);
      });
    }
  },
  methods: {
    getValues (group) {
      const selected = this.selected[group].selected;
      // var values = [];
      // for (var i in selected) {
      //   values = values.concat(selected[i].value);
      // }
      // console.log(values);
      // return values;
      return selected;
    },
    selectFeatures (group, selection) {
      this.$store.commit('selectedFeatures', {group: group, value: selection});
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
      const baseSettings = {labelField: 'name', valueField: 'value'};
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
        if (this.selected[group].value === 'all') {
          groups = groups.concat(group);
        } else if (this.selected[group].value === 'selected') {
          for (var i in this.selectedFeatures[group].selected) {
            features.push(this.selectedFeatures[group].selected[i].value[0]);
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
      // console.log(group, features);
      var selected = [];
      if (!features) {
        features = [];
      }
      for (let i in features) {
        if (typeof features[i] === 'string') {
          const value = features[i].split(',');
          selected = selected.concat({name: value[1], value: value});
        } else {
          selected = selected.concat(features[i]);
        }
      }
      this.$store.commit('selectedFeatures', {group: group, selected: selected});
      this.$set(this.selected[group], 'selected', selected);
      this.formErrors = this.getFormErrors();
      this.$forceUpdate();
    },
    updatePathways (pathways) {
      if (!pathways) {
        pathways = [];
      }
      this.$store.commit('selectedPathways', pathways);
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
      this.$http.post(`/api/datasets/${this.$route.params.dataset}/columns`, query).then(response => {
        this.$store.commit('columnData', response.data);
        this.download();
      }, response => {
        console.error('error');
      });
    },
    download () {
      if (this.numDataPoints <= this.$store.state.maxDataPoints) {
        if (this.formErrors !== null) {
          this.triggerErrorState();
          // return;
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
        pathways: this.selectedPathways,
      };
    },
    getPathways () {
      this.$http.get(`/api/datasets/${this.$route.params.dataset}/pathways`).then(response => {
        const items = response.data.map(item => {
          return {name: item[0], numGenes: item[1]};
        });
        this.pathways = items;
      }, response => {
        console.error('Could not retrieve pathways');
      });
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
.pathways {
  text-align: left;
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
