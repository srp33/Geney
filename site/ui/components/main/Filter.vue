<template>

  <div class="filter top row justify-content-center" v-if="metaData">
    <div class="col-sm-6">
      <h1>Filter Samples</h1>
      <selectize
        :options="metaTypes"
        :value="currentMetaType"
        placeholder="Select metadata variables to filter on - begin typing to see more results"
        @updated="selectMetaType"
        :settings="metaTypeSettings"
        id="meta-types"></selectize>

      <div class="spacer"></div>
      <div id="filter" v-if="currentMetaType && currentMeta">

        <selectize v-if="currentMeta.options !== 'continuous'"
          :options="currentMeta.options"
          :value="currentSelectedMeta"
          @updated="x => updateSelectedMeta(x)"
          placeholder="Select value(s) to include - begin typing to see more results"
          :settings="getSelectizeSettings(currentMetaType, currentMeta)"
          id="current-meta-type"></selectize>

        <div v-else>
          <h6>This meta type is continuous. Please select the range of numbers you would like to select.</h6>
          <h6>Min: {{metaDataMin}}</h6>
          <h6>Max: {{metaDataMax}}</h6>
          <div class="logic-set row" v-for="(logicSet, index) in selectedMeta[this.currentMetaType]" :key="logicSet.randomKey">

            <div class="form-group col" :class="{'has-danger': errors.has(currentMetaType + '_' + index + '_operator')}">
              <selectize
                :options="operatorList"
                :value="logicSet.operator"
                placeholder="Select Operator"
                @updated="x => updateSelectedMeta(x, index, 'operator')"
                :settings="settings.logicOperators"></selectize>
            </div>

            <div class="form-group col" :class="{'has-danger': errors.has(currentMetaType + '_' + index + '_value')}">
              <input
                type="number"
                class="form-control"
                :value="logicSet.value"
                :min="metaDataMin"
                :max="metaDataMax"
                :name="currentMetaType + '_' + index + '_value'"
                v-validate="`required|min_value:${metaDataMin}|max_value:${metaDataMax}`"
                @input="x => updateSelectedMeta(Number(x.target.value), index, 'value')"
                :class="{'form-control-danger': errors.has(currentMetaType + '_' + index + '_value')}">
            </div>
            <div class="pull-right">
              <button
                class=" btn btn-sm btn-danger"
                style="margin-top:5.5px"
                @click="removeLogicSet(index)">
                <i class="fa fa-minus" aria-hidden="true"></i>
              </button>
            </div>

          </div>

          <button class="pull-right btn btn-sm btn-success add-logic-set" @click="addLogicSet">
            <i class="fa fa-plus fa-lg" aria-hidden="true"></i>
          </button>
        </div>
      </div>

    </div>
    <div id="description" class="col-12 spacer">
      <div v-if="numKeys > 0">
        <h2>Let me get this right...</h2>
        <h3>You're looking for <strong>SAMPLES</strong> that have:</h3>
        <h4 v-for="(values,metaType,num) in metaQuery" :key="metaType">

          <span v-if="optionsType(metaType) === 'array'">
            <span v-for="(value, index) in values" v-if="index < 3" :key="index">
              "{{value}}"
              <strong v-if="index == values.length - 2 && values.length <= 3"> OR </strong>
            </span>
            <span v-if="values.length > 3"> (among others)</span>
          </span>

          <span v-else-if="optionsType(metaType) === 'continuous'">
            values
            <span v-for="(logicSet, index) in values" :key="index + logicSet.operator + logicSet.value">
              {{operators[logicSet.operator].toLowerCase()}}
              "{{logicSet.value}}"
              <span v-if="index < (values.length - 1)"> and <br></span>

            </span>
          </span>

          in the "{{metaType}}" column

          <h4 v-if="num < numKeys - 1"><strong>AND</strong></h4>
        </h4>
        <!-- <div v-if="selectedFeatures && selectedFeatures.length">
          <h3>And you want only the
            <strong>{{ selectedFeatures.length }}</strong>
            <span v-if="selectedFeatures.length > 1">{{ dataset.featureDescriptionPlural }}</span>
            <span v-else>{{ dataset.featureDescription }}</span>
            listed above.</h3>
        </div> -->
        <!-- <h3 v-else>And you want <strong>ALL</strong> of the {{ dataset.featureDescriptionPlural }}.</h3> -->

        <h2>Is that correct?</h2>
        <button @click="commit" class="btn btn-primary btn-lg confirm-btn">Confirm</button>
      </div>
      <div v-else>
        <h2>You have not selected any filters.</h2>
        <button @click="commit" class="btn btn-primary btn-lg confirm-btn">Continue</button>
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
      currentMetaType: '',
      selectedMeta: {},
      currentMeta: null,
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
    currentSelectedMeta () {
      if (this.currentMetaType) {
        return this.selectedMeta[this.currentMetaType];
      }
      return {};
    },
    metaDataMin () {
      if (this.currentMeta.options === 'continuous') {
        return this.currentMeta.min;
      }
      return 0;
    },
    metaDataMax () {
      if (this.currentMeta.options === 'continuous') {
        return this.currentMeta.max;
      }
      return 0;
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
      const baseSettings = { maxItems: 1 };
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
    selectMetaType (metaType) {
      this.$set(this, 'currentMetaType', metaType);
      if (metaType) {
        if (this.metaData && this.metaData.meta === null) {
          if (!this.cachedMeta[metaType]) { // not in cache so request it from the server
            this.getVariableMetadata(metaType).then(metaData => {
              this.$store.commit('cachedMeta', {
                dataset: this.dataset.id,
                metaType: metaType,
                value: metaData,
              });
              this.updateCurrentMeta();
              this.initializeContinuousType(metaType);
            });
          }
        } else {
          this.initializeContinuousType(metaType);
        }
      }
      this.updateCurrentMeta();
    },
    updateCurrentMeta () {
      if (this.currentMetaType) {
        if (this.cachedMeta[this.currentMetaType]) {
          this.$set(this, 'currentMeta', this.cachedMeta[this.currentMetaType]);
          return;
        }
        if (this.metaData.meta && this.metaData.meta[this.currentMetaType]) {
          this.$set(this, 'currentMeta', this.metaData.meta[this.currentMetaType]);
          return;
        }
      }
      this.$set(this, 'currentMeta', null);
    },
    updateSelectedMeta (value, index, key = false) {
      if (value) {
        this.$store.commit('lastMetaType', this.currentMetaType);
      }
      if (key === false) {
        this.$set(this.selectedMeta, this.currentMetaType, value);
      } else {
        this.$set(this.selectedMeta[this.currentMetaType][index], key, value);
      }
      this.updateMetaQuery();
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
    addLogicSet () {
      const list = this.selectedMeta[this.currentMetaType].slice();
      list.push({
        operator: null,
        value: null,
        randomKey: Math.random(),
      });
      this.updateSelectedMeta(list);
      this.$forceUpdate();
    },
    removeLogicSet (index) {
      console.log('before', this.selectedMeta[this.currentMetaType], index);
      const list = this.selectedMeta[this.currentMetaType].slice();
      list.splice(index, 1);
      console.log('after', list);
      this.updateSelectedMeta(list);
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
          this.addLogicSet();
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
.spacer, .logic-set, .add-logic-set {
  margin-top: 15px;
}
.confirm-btn {
  margin-bottom: 50px;
}
</style>
