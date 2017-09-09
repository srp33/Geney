import Vue from 'vue';
import Description from 'ui/components/main/Description';
import Vuex from 'vuex';
import VueRouter from 'vue-router';
import { expect } from 'chai';
import { mount } from 'avoriaz';

Vue.use(Vuex);
Vue.use(VueRouter);

describe('Description.vue', () => {
  it('should render page with dataset info if dataset exists', () => {
    const router = new VueRouter({
      mode: 'history',
      routes: [],
    });

    const storeData = {
      state: {
        dataset: {
          name: 'Best Datset Evar',
          description: '<h1>I AM THE BEST DATASET TO EVAR EXIST</h1>',
          numSamples: 999999999999,
          numGenes: 22000,
          numMetaTypes: 500,
          id: 'bestdatasetevar',
        },
      },
    };

    const store = new Vuex.Store(Object.assign({}, storeData));
    const wrapper = mount(Description, { store, router });

    expect(wrapper.find('#dataset-name')[0].element.innerHTML).to.equal(storeData.state.dataset.name);
    expect(wrapper.find('#dataset-description')[0].element.children[0].innerHTML).to.equal(storeData.state.dataset.description);
    expect(wrapper.find('#dataset-num-samples')[0].element.innerHTML).to.equal(storeData.state.dataset.numSamples + ' Samples');
    expect(wrapper.find('#dataset-num-genes')[0].element.innerHTML).to.equal(storeData.state.dataset.numGenes + ' Genes');
    expect(wrapper.find('#dataset-num-meta-types')[0].element.innerHTML).to.equal(storeData.state.dataset.numMetaTypes + ' Meta Data Types');
    expect(wrapper.find('#dataset-next-btn')[0].element.href).to.match(/\/dataset\/bestdatasetevar\/filter/);
  });

  it('should not render anything if no dataset exists', () => {
    const router = new VueRouter({
      mode: 'history',
      routes: [],
    });

    const storeData = {
      state: {},
    };

    const store = new Vuex.Store(Object.assign({}, storeData));
    const wrapper = mount(Description, { store, router });
    expect(wrapper.element.children).to.be.undefined;
  });
});
