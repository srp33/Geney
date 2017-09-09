import Vue from 'vue';
import Filter from 'ui/components/main/Filter';
import Selectize from 'ui/components/shared/Selectize';
import Vuex from 'vuex';
import VueRouter from 'vue-router';
import chai, { expect } from 'chai';
import { stub } from 'sinon';
import sinonChai from 'sinon-chai';
import { mount } from 'avoriaz';
import { expectShallowEqual } from 'test/helpers.js';

chai.use(sinonChai);

Vue.use(Vuex);
Vue.use(VueRouter);

describe('Filter.vue', () => {
  let router;
  let storeData;
  let store;
  let wrapper;
  let component;

  beforeEach(() => {
    router = new VueRouter({
      routes: [],
    });
  });

  describe('valid metadata', () => {
    beforeEach(() => {
      storeData = {
        state: {
          metaData: {
            meta: {
              type: [{name: 'type1'}, {name: 'type2'}, {name: 'type3'}],
              drug: [{name: 'drug1'}, {name: 'drug2'}, {name: 'drug3'}],
            },
            genes: [{name: 'geneA'}, {name: 'geneB'}, {name: 'geneC'}],
          },
        },
        mutations: {
          filters: stub(),
        },
      };

      store = new Vuex.Store(Object.assign({}, storeData));
      wrapper = mount(Filter, { store, router });
      component = wrapper.vm;
    });

    /*
     * this is a really complicated test, but essentially it goes through the following ui workflow
     *
     * 1. changes the meta data type to 'drug'
     * 2. selects a couple of genes
     * 3. selects some filters on the drug meta data type
     * 4. clicks the commit button to progress to the next screen
     *
     */
    it('should initialize selectizes correctly and respond properly to input', done => {
      let allSelectize = wrapper.find(Selectize);
      expect(allSelectize.length).to.equal(2);
      // make sure meta types have the correct options
      const metaTypeSelectize = allSelectize[0];
      expect(metaTypeSelectize.element.id).to.equal('meta-types');
      expectShallowEqual(metaTypeSelectize.vm.$props.options, [{name: 'type'}, {name: 'drug'}]);

      // make sure genes have the correct options
      const geneSelectize = allSelectize[1];
      expect(geneSelectize.element.id).to.equal('genes');
      expectShallowEqual(geneSelectize.vm.$props.options, [{name: 'geneA'}, {name: 'geneB'}, {name: 'geneC'}]);

      metaTypeSelectize.vm.$emit('updated', 'drug'); // set the meta type to "drug"
      geneSelectize.vm.$emit('updated', ['geneA', 'geneC']); // select some genes
      Vue.nextTick(() => { // wait for update
        expect(component.$data.currentMetaType).to.equal('drug');
        expectShallowEqual(component.$data.selectedGenes, ['geneA', 'geneC']);
        allSelectize = wrapper.find(Selectize);
        expect(allSelectize.length).to.equal(3);
        const metaFilterSelectize = allSelectize[2];
        // make sure meta type filters have the correct options
        expect(metaFilterSelectize.element.id).to.equal('current-meta-type');
        expectShallowEqual(metaFilterSelectize.vm.$props.options, [{name: 'drug1'}, {name: 'drug2'}, {name: 'drug3'}]);

        metaFilterSelectize.vm.$emit('updated', ['drug1', 'drug2']); // select some meta type filters
        Vue.nextTick(() => {
          expectShallowEqual(component.$data.selectedMeta.drug, ['drug1', 'drug2']);
          component.commit();
          expect(storeData.mutations.filters).to.have.been.calledOnce;
          expectShallowEqual(storeData.mutations.filters.getCall(0).args[1], { // make sure proper filters were set
            meta: {
              drug: ['drug1', 'drug2'],
            },
            genes: ['geneA', 'geneC'],
          });
          done();
        });
      });
    });

    it('should remove undefined keys from selectedMeta in the metaQuery', done => {
      component.$set(component, 'selectedMeta', {
        foo: 'bar',
        bar: null,
      });
      Vue.nextTick(() => {
        expectShallowEqual(component.metaQuery, {foo: 'bar'});
        done();
      });
    });
  });

  describe('invalid metadata', () => {
    it('should not render anything if metadata does not exist', () => {
      storeData = {
        state: {
        },
      };
      store = new Vuex.Store(Object.assign({}, storeData));
      wrapper = mount(Filter, { store, router });
      expect(wrapper.element.children).to.be.undefined;
      expect(wrapper.vm.metaTypes).to.be.false;
    });
  });

  describe('existing filters', () => {
    it('should apply filters if they exist', () => {
      storeData = {
        state: {
          filters: {
            meta: {
              foo: ['bar'],
            },
            genes: ['foo', 'bar'],
          },
        },
      };
      store = new Vuex.Store(Object.assign({}, storeData));
      wrapper = mount(Filter, { store, router });
      expectShallowEqual(wrapper.vm.$data.selectedGenes, storeData.state.filters.genes);
      expectShallowEqual(wrapper.vm.$data.selectedMeta, storeData.state.filters.meta);
    });
  });
});
