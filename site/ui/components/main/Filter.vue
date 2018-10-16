<template>

  <div class="filter top row justify-content-center" v-if="groups">
    <div class="col-sm-6">
      <h1>Filter Samples</h1>
      <div v-for="key in Object.keys(groups)" class="spacer" :key="key">
        <b-row>
          <b-col cols="3"><h4 class="variables">{{key}}:</h4></b-col>
          <b-col cols="9">
            <selectize
            :options="groups[key]"
            :value="option"
            placeholder="Variables"
            @updated="x => selectVariable(x, key)"
            :settings="variableSettings(key)"
            id="meta-types"></selectize>
          </b-col>
          </b-row>
      </div>
        <div v-if="currentVariables.length> 0">
          <div class="spacer"></div>
          <div class="line"></div>
          <div class="spacer"></div>
          <div v-for="variable in currentVariables" :key="variable">
            <div class="spacer"></div>
            <div v-if="options[variable].options !== 'continuous'">
              <h4>
                <button
                  class="btn btn-sm btn-danger"
                  @click="removeFilter(variable)">
                  <i class="fa fa-minus" aria-hidden="true"></i>
                </button>
                {{variable.replace('_', ': ')}}
              </h4>
              <selectize
              :options="options[variable].options"
              :value="getValues(variable)"
              @updated="x => updateSelectedFilters(variable, x)"
              placeholder="Select value(s) to include - begin typing to see more results"
              :settings="getSelectizeSettings(variable)"
              :id="variable"></selectize>
            </div>
          <div v-else>
            <h4>
              <button
                class=" btn btn-sm btn-danger"
                  @click="removeFilter(variable)">
                <i class="fa fa-minus" aria-hidden="true"></i>
              </button>
                {{variable.replace(sep, ': ')}}<h6><br>(min: {{variableMin(variable).toFixed(2)}} - max: {{variableMax(variable).toFixed(2)}})</h6>
            </h4>
              <!-- {{selectVariable[variable]}} -->
              <div class="logic-set row" v-for="(logicSet, index) in selectedFilters[variable]" :key="logicSet.randomKey">

                <div class="form-group col" :class="{'has-danger': errors.has(variable + '_' + index + '_operator')}">
                <selectize
                  :options="operatorList"
                  :value="logicSet.operator"
                  placeholder="Select Operator"
                    @updated="x => updateSelectedFilters(variable, x, index, 'operator')"
                  :settings="settings.logicOperators"></selectize>
              </div>

                <div class="form-group col" :class="{'has-danger': errors.has(variable + '_' + index + '_value')}">
                <input
                  type="number"
                  class="form-control"
                  :value="logicSet.value"
                    :min="variableMin(variable)"
                    :max="variableMax(variable)"
                    :name="variable + '_' + index + '_value'"
                    v-validate="`required|min_value:${variableMin(variable)}|max_value:${variableMax(variable)}`"
                    @input="x => updateSelectedFilters(variable, Number(x.target.value), index, 'value')"
                    :class="{'form-control-danger': errors.has(variable + '_' + index + '_value')}">
              </div>
              <div class="pull-right">
                <button
                  class=" btn btn-sm btn-danger"
                  style="margin-top:5.5px"
                    @click="removeLogicSet(variable, index)">
                  <i class="fa fa-minus" aria-hidden="true"></i>
                </button>
              </div>
            </div>
              <button class="right-side btn btn-sm btn-success" @click="addLogicSet(variable)">
              <i class="fa fa-plus fa-lg" aria-hidden="true"></i>
              </button>
          </div>
        </div>
      </div>
      <div id="description" class="col-12 spacer">
        <div v-if="Object.keys(query).length > 0">
          <h2>Continue with these filters?</h2>
          <button @click="commit" class="btn btn-primary btn-lg confirm-btn">Confirm</button>
        </div>
        <div v-else>
          <h2>You have not selected any filters.</h2>
          <button @click="commit" class="btn btn-primary btn-lg confirm-btn">Continue</button>
        </div>
    </div>
  </div>
  </div>
</template>

<script>
import router from '../../router';
import Vue from 'vue';
import { mapGetters } from 'vuex';
const selectize = require('../shared/Selectize');

export default {
  name: 'filter',
  components: {
    selectize,
  },
  data () {
    return {
      selectedMetaTypes: [],
      selectedVariables: [],
      selectedMeta: {},
      selectedFilters: {},
      currentMeta: null,
      option: '',
      settings: {
        oneItem: {
          maxItems: 1,
        },
        logicOperators: {
          maxItems: 1,
          labelField: 'label',
          valueField: 'operator',
          required: true,
        },
      },
      operators: {
        '<': 'Less Than',
        '<=': 'Less Than Or Equal To',
        '>': 'Greater Than',
        '>=': 'Greater Than Or Equal To',
        '==': 'Equal To',
        '!=': 'Not Equal To',
      },
      query: {},
    };
  },
  computed: {
    ...mapGetters({
      options: 'getOptions',
    }),
    currentVariables () {
      const list = [];
      for (var variable in this.query) {
        list.push(variable);
      }
      for (var i in this.selectedVariables) {
        if (list.indexOf(this.selectedVariables[i]) === -1) {
          list.push(this.selectedVariables[i]);
        }
      }
      return list.sort();
    },
    metaData () {
      return this.$store.state.metaData;
    },
    groups () {
      return this.$store.state.groups;
    },
    operatorList () {
      const list = [];
      for (let operator in this.operators) {
        const label = this.operators[operator];
        list.push({
          operator: operator,
          label: label,
        });
      }
      return list;
    },
    dataset () {
      return this.$store.state.dataset;
    },
    cachedMeta () {
      return this.$store.state.cachedMeta[this.dataset.id];
    },
    sep () {
      return this.$store.state.sep;
    },
  },
  methods: {
    variableSettings (group) {
      const baseSettings = { maxItems: 1, clearValue: false };
      if (this.groups && this.groups[group] === null) {
        const loadfn = function (query, callback) {
          this.$http.get(
            `/api/datasets/${this.$route.params.dataset}/groups/${group}/search/${query}`
          ).then(response => {
            const items = response.data.map(item => {
              return {name: item.replace(group + this.sep, '')};
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
    variableMin (variable) {
      if (this.options[variable].options === 'continuous') {
        return this.options[variable].min;
      }
      return 0;
    },
    variableMax (variable) {
      if (this.options[variable].options === 'continuous') {
        return this.options[variable].max;
      }
      return 0;
    },
    getValues (variable) {
      return this.query[variable];
    },
    removeFilter (variable) {
      delete this.selectedFilters[variable];
      delete this.query[variable];
      var index = this.selectedVariables.indexOf(variable);
      this.selectedVariables = this.selectedVariables.splice(0, index).concat(this.selectedVariables.splice(index + 1));
      this.$forceUpdate();
    },
    getOptions (variable) {
      return Vue.http.get(`/api/datasets/${this.$route.params.dataset}/options/${variable}`).then(response => {
        const data = response.body;
        if (Array.isArray(data.options)) {
          data.options = data.options.map(val => ({ name: val }));
        }
        return data;
      }).catch(err => {
        console.error(err);
      });
    },
    selectMetaType (metaType) {
      console.log('selected ' + metaType);
      if (metaType && metaType !== undefined && this.selectedMetaTypes.indexOf(metaType) === -1) {
        this.selectedMetaTypes.push(metaType);
      }
      this.option = null;
      if (metaType) {
        if (this.metaData && this.metaData.meta === null) {
          if (!this.cachedMeta[metaType]) { // not in cache so request it from the server
            this.getVariableMetadata(metaType).then(metaData => {
              this.$store.commit('cachedMeta', {
                dataset: this.dataset.id,
                metaType: metaType,
                value: metaData,
              });
              this.initializeContinuousType(metaType);
            });
          }
        } else {
          this.initializeContinuousType(metaType);
        }
      }
    },
    selectVariable (variable, group = null) {
      if (variable && variable !== undefined && variable !== '' && this.selectedVariables.indexOf(variable) === -1) {
        if (group) {
          variable = group + this.sep + variable;
        }
        this.getOptions(variable).then(options => {
          if (options) {
            this.$store.commit('options', {'variable': variable, 'options': options});
            this.selectedVariables.push(variable);
            this.initializeContinuousType(variable);
          }
        });
        this.option = null;
      }
    },
    updateSelectedMeta (metaType, value, index, key = false) {
      if (value && value !== undefined && metaType !== undefined) {
        this.$store.commit('lastMetaType', metaType);
        if (key === false) {
          this.$set(this.selectedMeta, metaType, value);
        } else {
          this.$set(this.selectedMeta[metaType][index], key, value);
        }
        this.updateQuery();
      }
    },
    updateSelectedFilters (variable, value, index, key = false) {
      if (value && value !== undefined && variable !== undefined) {
        // this.$store.commit('lastMetaType', variable);
        if (key === false) {
          this.$set(this.selectedFilters, variable, value);
        } else {
          this.$set(this.selectedFilters[variable][index], key, value);
        }
        this.updateQuery();
      }
    },
    updateQuery () {
      // basically just removes any null elements from the selectedMeta object
      // they become null when you remove all filters from a meta type
      const filters = JSON.parse(JSON.stringify(this.selectedFilters));
      for (let variable in filters) {
        if (!filters[variable]) {
          delete filters[variable];
        } else if (this.options[variable].options === 'continuous') {
          const list = [];
          for (let item of filters[variable]) {
            if (this.validLogicSet(variable, item)) {
              list.push({
                operator: item.operator,
                value: item.value,
              });
            }
          }
          if (list.length === 0) {
            delete filters[variable];
          } else {
            filters[variable] = list;
          }
        }
      }
      this.$set(this, 'query', filters);
    },
    commit () {
      this.$store.commit('filters', this.query);
      router.push('/dataset/' + this.$route.params.dataset + '/filter/download');
    },
    addLogicSet (variable) {
      const list = this.selectedFilters[variable].slice();
      list.push({
        operator: null,
        value: null,
        randomKey: Math.random(),
      });
      this.updateSelectedFilters(variable, list);
      this.$forceUpdate();
    },
    removeLogicSet (variable, index) {
      const list = this.selectedFilters[variable].slice();
      list.splice(index, 1);
      this.updateSelectedFilters(variable, list);
      this.$forceUpdate();
      Vue.nextTick(() => {
        this.$validator.validateAll();
      });
    },
    optionsType (metaType) {
      if (this.metaData && this.metaData.meta !== undefined) {
        const meta = this.getMeta(metaType);
        if (!meta) {
          return;
        }
        if (Array.isArray(meta.options) || meta.options === null) {
          return 'array';
        } else if (meta.options === 'continuous') {
          return 'continuous';
        } else {
          throw new Error(`Unknown options type. Given ${meta.options}`);
        }
      }
    },
    validLogicSet (variable, logicSet) {
      if (!logicSet.operator) {
        return false;
      }
      const meta = this.options[variable];
      if (!meta) {
        return false;
      }
      if (typeof logicSet.value !== 'number' ||
          logicSet.value > meta.max ||
          logicSet.value < logicSet.min) {
        return false;
      }
      return true;
    },
    getSelectizeSettings (variable) {
      const settings = {};
      if (this.options[variable].options === null) {
        const loadfn = function (query, callback) {
          this.$http.get(
            `/api/datasets/${this.$route.params.dataset}/options/${variable}/search/${query}`
          ).then(response => {
            const items = response.data.map(item => {
              return {name: item};
            });
            callback(items);
          }, failedResponse => {
            callback();
          });
        };
        settings.load = loadfn.bind(this);
      }
      return settings;
    },
    getVariableMetadata (metaType) {
      return Vue.http.get(`/api/datasets/${this.dataset.id}/meta/${metaType}`).then(response => {
        const data = response.body;
        if (Array.isArray(data.options)) {
          data.options = data.options.map(val => ({ name: val }));
        }
        return data;
      }).catch(err => {
        console.error(err);
      });
    },
    getMeta (metaType) {
      return this.metaData.meta ? this.metaData.meta[metaType] : this.cachedMeta[metaType];
    },
    initializeContinuousType (variable) {
      const options = this.options[variable];
      if (options && options.options === 'continuous') {
        if (!this.selectedFilters[variable] || this.selectedFilters[variable].length === 0) {
          this.selectedFilters[variable] = [];
          this.addLogicSet(variable);
        }
      }
    },
  },
  created () {
    if (this.$store.state.filters) {
      const filters = JSON.parse(JSON.stringify(this.$store.state.filters));
      this.$set(this, 'selectedFilters', filters);
      // this.$set(this, 'selectedFeatures', filters.features);
      if (this.$store.state.lastMetaType) {
        this.selectVariable(this.$store.state.lastMetaType);
      } else {
        this.selectVariable(Object.keys(filters)[0]);
      }
      this.updateQuery();
    }
  },
};
</script>

<style lang="scss" scoped>
h1, h2, h3 {
  font-weight: normal;
}

h4 {
  text-align: left;
}

h6 {
  display: inline;
}
.spacer, .logic-set, .add-logic-set {
  margin-top: 15px;
}
.confirm-btn {
  margin-bottom: 50px;
}

.line {
  border-bottom: 2px solid black;
}

.variables {
  margin-top: 5px;
}

.right-side {
  margin-right: -17px;
  float: right;
}
</style>
