<template>

  <div class="filter top row justify-content-center" v-if="metaData">
    <div class="col-sm-6">
      <h1>Filter Samples</h1>
      <div class="spacer"></div>
      <b-row>
        <b-col cols="3"><h4 class="variables">Variables:</h4></b-col>
        <b-col cols="9">
          <selectize
          :options="metaTypes"
          :value="option"
          placeholder="Variables"
          @updated="selectMetaType"
          :settings="metaTypeSettings"
          id="meta-types"></selectize>
        </b-col>
      </b-row>
      <div v-if="currentMetaTypes.length> 0">
        <div class="spacer"></div>
        <div class="line"></div>
        <div class="spacer"></div>
        <div v-for="metaType in currentMetaTypes" :key="metaType">
          <div class="spacer"></div>
          <div v-if="getOptions(metaType).options !== 'continuous'">
            <h4>
              <button
                class="btn btn-sm btn-danger"
                @click="removeFilter(metaType)">
                <i class="fa fa-minus" aria-hidden="true"></i>
              </button>
              {{metaType}}
            </h4>
            <selectize
            :options="getOptions(metaType).options"
            :value="getValues(metaType)"
            @updated="x => updateSelectedMeta(metaType, x)"
            placeholder="Select value(s) to include - begin typing to see more results"
            :settings="getSelectizeSettings(metaType, getOptions(metaType))"
            :id="metaType"></selectize>
          </div>

          <div v-else>
            <h4>
              <button
                class=" btn btn-sm btn-danger"
                @click="removeFilter(metaType)">
                <i class="fa fa-minus" aria-hidden="true"></i>
              </button>
              {{metaType}}<h6><br>(min: {{metaDataMin(metaType)}} - max: {{metaDataMax(metaType)}})</h6>
            </h4>
            {{selectMetaType[metaType]}}
            <div class="logic-set row" v-for="(logicSet, index) in selectedMeta[metaType]" :key="logicSet.randomKey">

              <div class="form-group col" :class="{'has-danger': errors.has(metaType + '_' + index + '_operator')}">
                <selectize
                  :options="operatorList"
                  :value="logicSet.operator"
                  placeholder="Select Operator"
                  @updated="x => updateSelectedMeta(metaType, x, index, 'operator')"
                  :settings="settings.logicOperators"></selectize>
              </div>

              <div class="form-group col" :class="{'has-danger': errors.has(metaType + '_' + index + '_value')}">
                <input
                  type="number"
                  class="form-control"
                  :value="logicSet.value"
                  :min="metaDataMin(metaType)"
                  :max="metaDataMax(metaType)"
                  :name="metaType + '_' + index + '_value'"
                  v-validate="`required|min_value:${metaDataMin(metaType)}|max_value:${metaDataMax(metaType)}`"
                  @input="x => updateSelectedMeta(metaType, Number(x.target.value), index, 'value')"
                  :class="{'form-control-danger': errors.has(metaType + '_' + index + '_value')}">
              </div>
              <div class="pull-right">
                <button
                  class=" btn btn-sm btn-danger"
                  style="margin-top:5.5px"
                  @click="removeLogicSet(metaType, index)">
                  <i class="fa fa-minus" aria-hidden="true"></i>
                </button>
              </div>
            </div>
            <button class="right-side btn btn-sm btn-success" @click="addLogicSet(metaType)">
              <i class="fa fa-plus fa-lg" aria-hidden="true"></i>
              </button>
          </div>
        </div>
      </div>
      <div id="description" class="col-12 spacer">
        <div v-if="Object.keys(metaQuery).length > 0">
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
const selectize = require('../shared/Selectize');

export default {
  name: 'filter',
  components: {
    selectize,
  },
  data () {
    return {
      selectedMetaTypes: [],
      selectedMeta: {},
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
      metaQuery: {},
    };
  },
  computed: {
    currentMetaTypes () {
      const list = [];
      for (var metaType in this.metaQuery) {
        list.push(metaType);
      }
      for (var i in this.selectedMetaTypes) {
        if (list.indexOf(this.selectedMetaTypes[i]) === -1) {
          list.push(this.selectedMetaTypes[i]);
        }
      }
      return list.sort();
    },
    numKeys () {
      return Object.keys(this.metaQuery).length;
    },
    metaTypes () {
      if (this.metaData && this.metaData.meta) {
        return Object.keys(this.metaData.meta).map(x => ({'name': x}));
      } else if (this.$store.state.filters) {
        return Object.keys(this.$store.state.filters).map(val => ({ name: val }));
      } else {
        return [];
      }
    },
    metaData () {
      return this.$store.state.metaData;
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
    metaTypeSettings () {
      const baseSettings = { maxItems: 1, clearValue: true };
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
            callback();
          });
        };
        baseSettings.load = loadfn.bind(this);
        return baseSettings;
      } else {
        return baseSettings;
      }
    },
    cachedMeta () {
      return this.$store.state.cachedMeta[this.dataset.id];
    },
  },
  methods: {
    metaDataMin (metaType) {
      if (this.metaData.meta[metaType].options === 'continuous') {
        return this.metaData.meta[metaType].min;
      }
      return 0;
    },
    metaDataMax (metaType) {
      if (this.metaData.meta[metaType].options === 'continuous') {
        return this.metaData.meta[metaType].max;
      }
      return 0;
    },
    getValues (metaType) {
      return this.metaQuery[metaType];
    },
    removeFilter (metaType) {
      delete this.selectedMeta[metaType];
      delete this.metaQuery[metaType];
      var index = this.selectedMetaTypes.indexOf(metaType);
      this.selectedMetaTypes = this.selectedMetaTypes.splice(0, index).concat(this.selectedMetaTypes.splice(index + 1));
      this.$forceUpdate();
    },
    getOptions (metaType) {
      return this.$store.state.metaData.meta[metaType];
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
    updateSelectedMeta (metaType, value, index, key = false) {
      if (value && value !== undefined && metaType !== undefined) {
        this.$store.commit('lastMetaType', metaType);
        if (key === false) {
          this.$set(this.selectedMeta, metaType, value);
        } else {
          this.$set(this.selectedMeta[metaType][index], key, value);
        }
        this.updateMetaQuery();
      }
    },
    updateMetaQuery () {
      // basically just removes any null elements from the selectedMeta object
      // they become null when you remove all filters from a meta type
      const query = JSON.parse(JSON.stringify(this.selectedMeta));
      for (let metaType in query) {
        if (!query[metaType]) {
          delete query[metaType];
        } else if (this.optionsType(metaType) === 'continuous') {
          const list = [];
          for (let item of query[metaType]) {
            if (this.validLogicSet(metaType, item)) {
              list.push({
                operator: item.operator,
                value: item.value,
              });
            }
          }
          if (list.length === 0) {
            delete query[metaType];
          } else {
            query[metaType] = list;
          }
        }
      }
      this.$set(this, 'metaQuery', query);
    },
    commit () {
      this.$store.commit('filters', this.metaQuery);
      router.push('/dataset/' + this.$route.params.dataset + '/filter/download');
    },
    addLogicSet (metaType) {
      const list = this.selectedMeta[metaType].slice();
      list.push({
        operator: null,
        value: null,
        randomKey: Math.random(),
      });
      this.updateSelectedMeta(metaType, list);
      this.$forceUpdate();
    },
    removeLogicSet (metaType, index) {
      const list = this.selectedMeta[metaType].slice();
      list.splice(index, 1);
      this.updateSelectedMeta(metaType, list);
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
    validLogicSet (metaType, logicSet) {
      if (!logicSet.operator) {
        return false;
      }
      const meta = this.getMeta(metaType);
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
    initializeContinuousType (metaType) {
      const meta = this.getMeta(metaType);
      if (meta && meta.options === 'continuous') {
        if (!this.selectedMeta[metaType] || this.selectedMeta[metaType].length === 0) {
          this.selectedMeta[metaType] = [];
          this.addLogicSet(metaType);
        }
      }
    },
  },
  created () {
    if (this.$store.state.filters) {
      const filters = JSON.parse(JSON.stringify(this.$store.state.filters));
      this.$set(this, 'selectedMeta', filters);
      // this.$set(this, 'selectedFeatures', filters.features);
      if (this.$store.state.lastMetaType) {
        this.selectMetaType(this.$store.state.lastMetaType);
      } else {
        this.selectMetaType(Object.keys(filters)[0]);
      }
      this.updateMetaQuery();
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
