<template>

  <div class="filter top row justify-content-center" v-if="groups">
    <div class="col-sm-6">
      <h1>Filter Samples</h1>
      <div v-for="key in Object.keys(groups)" class="spacer" :key="key">
          <h4 class="variables">{{key.replace(/_/g, ' ')}}:</h4>
            <selectize
            :options="groups[key]"
            :value="option"
            placeholder="Variables"
            @updated="x => selectVariable(x, key)"
            :settings="variableSettings(key)"
            id="meta-types"></selectize>
          <div v-if="currentVariablesByGroup[key].length > 0">
            <div class="spacer"></div>
            <div class="line"></div>
            <div class="spacer"></div>
            <div v-for="(variable, index) in currentVariablesByGroup[key]" :key="index">
              <div class="spacer"></div>
              <div v-if="options[variable.index].options !== 'continuous'">
                <b-row style="margin-left: 10px;">
                  <b-col col lg="1">
                    <button
                      class="btn btn-sm btn-danger"
                      @click="removeFilter(variable)">
                      <i class="fa fa-minus" aria-hidden="true"></i>
                    </button>
                  </b-col>
                  <b-col cols="1" md="auto">
                    <h5>{{variable.name}}:</h5>
                  </b-col>
                  <b-col cols="8">
                    <selectize
                    :options="options[variable.index].options"
                    :value="getValues(variable)"
                    @updated="x => updateSelectedFilters(variable, x)"
                    placeholder="Select value(s) to include - begin typing to see more results"
                    :settings="getSelectizeSettings(variable)"
                    :id="variable"></selectize>
                  </b-col>
                </b-row>
              </div>
            <div v-else>
              <h4>
                <button
                  class=" btn btn-sm btn-danger"
                    @click="removeFilter(variable)">
                  <i class="fa fa-minus" aria-hidden="true"></i>
                </button>
                  {{variable.name}}<h6><br>(min: {{variableMin(variable).toFixed(2)}} - max: {{variableMax(variable).toFixed(2)}})</h6>
              </h4>
                <div class="logic-set row" v-for="(logicSet, index) in filters[variable.index].value" :key="logicSet.randomKey">

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
      </div>
      <div id="description" class="col-12 spacer">
        <div v-if="Object.keys(filters).length > 0">
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
      selectedVariables: [],
      option: '',
      settings: {
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
      // query: {},
    };
  },
  computed: {
    ...mapGetters({
      options: 'getOptions',
    }),
    filters () {
      return this.$store.state.filters;
    },
    currentVariables () {
      const list = [];
      for (var variable in this.filters) {
        list.push(this.filters[variable].variable);
      }
      for (var i in this.selectedVariables) {
        if (!this.containsVariable(this.selectedVariables[i], list)) {
          list.push(this.selectedVariables[i]);
        }
      }
      return list.sort();
    },
    currentVariablesByGroup () {
      const vars = {};
      for (var i in Object.keys(this.groups)) {
        vars[Object.keys(this.groups)[i]] = [];
      }
      for (var j in this.currentVariables) {
        var group = this.currentVariables[j].group;
        vars[group] = vars[group].concat(this.currentVariables[j]);
      }
      return vars;
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
  },
  methods: {
    variableSettings (group) {
      const baseSettings = { maxItems: 1, clearValue: false, valueField: 'value' };
      if (this.groups && this.groups[group] === null) {
        const loadfn = function (query, callback) {
          this.$http.get(
            `/api/datasets/${this.$route.params.dataset}/groups/${group}/search/${query}`
          ).then(response => {
            const items = response.data.map(item => {
              return {
                name: item[1],
                value: item,
              };
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
      if (this.options[variable.index].options === 'continuous') {
        return this.options[variable.index].min;
      }
      return 0;
    },
    variableMax (variable) {
      if (this.options[variable.index].options === 'continuous') {
        return this.options[variable.index].max;
      }
      return 0;
    },
    getValues (variable) {
      return this.filters[variable.index].value;
    },
    removeFilter (variable) {
      this.$store.commit('removeFilter', variable);
      var index = this.selectedVariables.indexOf(variable);
      this.selectedVariables = this.selectedVariables.splice(0, index).concat(this.selectedVariables.splice(index + 1));
      this.$forceUpdate();
    },
    getOptions (variable) {
      return Vue.http.get(`/api/datasets/${this.$route.params.dataset}/options/${variable.index}`).then(response => {
        const data = response.body;
        if (Array.isArray(data.options)) {
          data.options = data.options.map(val => ({ name: val }));
        }
        return data;
      }).catch(err => {
        console.error(err);
      });
    },
    selectVariable (variable, group = null) {
      if (variable && variable !== undefined && variable !== '') {
        variable = variable.split(',');
        variable = {group: group, index: variable[0], name: variable[1]};
        if (this.selectedVariables.indexOf(variable) === -1) {
          this.getOptions(variable).then(options => {
            if (options) {
              this.$store.commit('options', {'variable': variable.index, 'options': options});
              this.selectedVariables.push(variable);
              this.initializeContinuousType(variable);
            }
          });
          this.option = null;
        }
      }
    },
    updateSelectedFilters (variable, value, index, key = false) {
      if (value && value !== undefined && variable !== undefined) {
        this.$store.commit('addFilter', {
          variable: variable,
          value: value,
          index: index,
          key: key,
        });
      }
    },
    cleanFilters () {
      // basically just removes any null elements from the selectedVariables object
      // they become null when you remove all filters from a meta type
      const filters = JSON.parse(JSON.stringify(this.filters));
      console.log('filters', filters);
      for (let variable in filters) {
        if (!filters[variable].value || filters[variable].value.length < 1) {
          delete filters[variable];
        } else if (this.options[variable].options === 'continuous') {
          const list = [];
          for (let item of filters[variable].value) {
            if (this.validLogicSet(variable, item)) {
              list.push(item);
            }
          }
          if (list.length === 0) {
            delete filters[variable];
          } else {
            filters[variable].value = list;
          }
        }
      }
      this.$store.commit('filters', filters);
    },
    commit () {
      this.cleanFilters();
      router.push('/dataset/' + this.$route.params.dataset + '/filter/columns');
    },
    addLogicSet (variable) {
      const list = this.filters[variable.index].value.slice();
      list.push({
        operator: null,
        value: null,
        randomKey: Math.random(),
      });
      this.updateSelectedFilters(variable, list);
      this.$forceUpdate();
    },
    removeLogicSet (variable, index) {
      const list = this.filters[variable.index].value.slice();
      list.splice(index, 1);
      this.updateSelectedFilters(variable, list);
      this.$forceUpdate();
      Vue.nextTick(() => {
        this.$validator.validateAll();
      });
      if (this.filters[variable.index].value.length === 0) {
        this.removeFilter(variable);
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
      if (this.options[variable.index].options === null) {
        const loadfn = function (query, callback) {
          this.$http.get(
            `/api/datasets/${this.$route.params.dataset}/options/${variable.index}/search/${query}`
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
    initializeContinuousType (variable) {
      const options = this.options[variable.index];
      if (options && options.options === 'continuous') {
        if (!this.filters[variable.index] || this.filters[variable.index].length === 0) {
          this.$store.commit('addFilter', {
            variable: variable,
            value: [{
              operator: null,
              value: null,
              randomKey: Math.random(),
            }],
          });
        }
      } else {
        if (!this.filters[variable.index] || this.filters[variable.index].length === 0) {
          this.$store.commit('addFilter', {
            variable: variable,
            value: [],
          });
        }
      }
    },
    containsVariable (obj, list) {
      var i;
      for (i = 0; i < list.length; i++) {
        if (list[i].index === obj.index) {
          return true;
        }
      }
      return false;
    },
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

h5 {
  margin-top: 2px;
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
