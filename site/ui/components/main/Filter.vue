<template>

  <div class="filter top row justify-content-center" v-if="metaData">
    <div class="col-sm-6">
      <h1>Filter Samples</h1>
      <selectize
        :options="metaTypes"
        :value="currentMetaType"
        placeholder="Select meta type to filter"
        @updated="selectMetaType"
        :settings="settings.oneItem"
        id="meta-types"></selectize>

      <div class="spacer"></div>
      <div id="filter" v-if="currentMetaType">

        <selectize v-if="currentMeta.options !== 'continuous'"
          :options="currentMeta.options"
          :value="currentSelectedMeta"
          @updated="x => updateSelectedMeta(x)"
          placeholder="Filter Meta"
          :settings="getSelectizeSettings(currentMetaType, currentMeta)"
          id="current-meta-type"></selectize>

        <div v-else>
          <h6>This meta type is continuous. Please select the range of numbers you would like to select.</h6>
          <h6>Min: {{metaDataMin}}</h6>
          <h6>Max: {{metaDataMax}}</h6>
          <div class="logic-set row" v-for="(logicSet, index) in selectedMeta[this.currentMetaType]" :key="currentMetaType + '_' + index">

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
                @click="removeLogicSet(index)"
                :disabled="currentSelectedMeta.length === 1">
                <i class="fa fa-minus" aria-hidden="true"></i>
              </button>
            </div>

          </div>

          <button class="pull-right btn btn-sm btn-success add-logic-set" @click="addLogicSet">
            <i class="fa fa-plus fa-lg" aria-hidden="true"></i>
          </button>
        </div>
      </div>

      <h1 style="margin-top:25px;">Select Genes</h1>
      <selectize
        :options="metaData.genes.options"
        :value="selectedGenes"
        @updated="updateGenes"
        placeholder="All Genes"
        :settings="getSelectizeSettings('genes', metaData.genes)"
        id="genes"></selectize>

    </div>
    <div id="description" class="col-12 spacer">
      <div v-if="numKeys > 0">
        <h2>Let me get this right...</h2>
        <h3>You're looking for <strong>ROWS</strong> that have:</h3>
        <h4 v-for="(values,metaType,num) in metaQuery.meta" :key="metaType">

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
        <div v-if="selectedGenes && selectedGenes.length">
          <h3>And you want only the <strong>COLUMNS</strong> with the genes listed above.</h3>
        </div>
        <h3 v-else>And you want <strong>ALL</strong> of the <strong>COLUMNS</strong>.</h3>

        <h2>Is that correct?</h2>
        <button @click="commit" class="btn btn-primary btn-lg confirm-btn">Confirm</button>
      </div>
      <div v-else>
        <h2>Please select some filters so we can grant your wish.</h2>
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
      selectedGenes: [],
      currentMetaType: '',
      selectedMeta: {},
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
      } else {
        return false;
      }
    },
    metaData () {
      return this.$store.state.metaData;
    },
    currentMeta () {
      if (this.currentMetaType) {
        return this.$store.state.metaData.meta[this.currentMetaType];
      }
      return {};
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
  },
  methods: {
    selectMetaType (metaType) {
      this.$set(this, 'currentMetaType', metaType);
      if (metaType) {
        if (this.metaData.meta[metaType].options === 'continuous') {
          if (!this.selectedMeta[metaType]) {
            this.selectedMeta[metaType] = [];
            this.addLogicSet();
          }
        }
      }
    },
    updateGenes (genes) {
      this.$set(this, 'selectedGenes', genes);
    },
    updateSelectedMeta (value, index, key = false) {
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
              list.push(item);
            }
          }
          if (list.length === 0) {
            delete query[metaType];
          } else {
            query[metaType] = list;
          }
        }
      }
      this.$set(this, 'metaQuery', {meta: query});
      // return q;
    },
    commit () {
      this.$store.commit('filters', {meta: this.metaQuery, genes: this.selectedGenes});
      router.push('/dataset/' + this.$route.params.dataset + '/filter/download');
    },
    addLogicSet () {
      const list = this.selectedMeta[this.currentMetaType];
      list.push({
        operator: null,
        value: null,
      });
      this.updateSelectedMeta(list);
      this.$forceUpdate();
    },
    removeLogicSet (index) {
      this.currentSelectedMeta.splice(index, 1);
      this.$forceUpdate();
      Vue.nextTick(() => {
        this.$validator.validateAll();
      });
    },
    optionsType (metaType) {
      if (this.metaData && this.metaData.meta) {
        const meta = this.metaData.meta[metaType];
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
      const meta = this.metaData.meta[metaType];
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
          if (query.length === 0) {
            return callback();
          }
          this.$http.get(
            `/api/datasets/${this.$route.params.dataset}/meta/${metaType}/search/${query}`
          ).then(response => {
            callback(response.data.map(item => {
              return {name: item};
            }));
          }, failedResponse => {
            console.log(failedResponse);
            callback();
          });
        };
        settings.load = loadfn.bind(this);
      }
      return settings;
    },
  },
  created () {
    if (this.$store.state.filters) {
      this.selectedGenes = this.$store.state.filters.genes;
      this.selectedMeta = this.$store.state.filters.meta;
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
