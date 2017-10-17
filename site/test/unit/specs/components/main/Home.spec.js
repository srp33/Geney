import Vue from 'vue';
import Home from 'ui/components/main/Home';
import Vuex from 'vuex';
import VueRouter from 'vue-router';
import VueMasonryPlugin from 'vue-masonry';
import { expect } from 'chai';
import { mount } from 'avoriaz';
import mockDatasets from 'ui/api/datasets.json';

Vue.use(Vuex);
Vue.use(VueMasonryPlugin);
Vue.use(VueRouter);

describe('Home.vue', () => {
  let store;
  let router;
  let component;
  let wrapper;

  beforeEach(() => {
    router = new VueRouter({});
  });

  describe('without datasets', () => {
    beforeEach(() => {
      store = new Vuex.Store({
        state: {
          datasets: [],
        },
        actions: {},
      });

      wrapper = mount(Home, { store, router });
      component = wrapper.vm;
    });

    it('should not render any datasets', () => {
      expect(component.datasets).to.be.a('array');
      expect(component.datasets.length).to.equal(0);

      const datasets = wrapper.find('.dataset-item');
      expect(datasets.length).to.equal(0);
    });
  });

  describe('with datasets', () => {
    beforeEach(() => {
      store = new Vuex.Store({
        state: {
          datasets: mockDatasets,
        },
        actions: {},
      });

      wrapper = mount(Home, { store, router });
      component = wrapper.vm;
    });

    it('should create a sifter with ALL of the datasets', () => {
      expect(component.sifter.items).to.be.a('array');
      expect(component.sifter.items.length).to.equal(5);
    });

    it('should show all datasets without a filter', () => {
      expect(component.datasets).to.be.a('array');
      expect(component.datasets.length).to.equal(5);

      const datasets = wrapper.find('.dataset-item');
      expect(datasets.length).to.equal(5);
    });

    describe('sorting datasets', () => {
      const sortingKeys = ['uploadDate', 'name', 'numSamples'];
      const sortingOrders = ['ascending', 'descending'];

      function testFunc () {
        component.sort.selected = this.key;
        component.sort.descending = this.descending;
        wrapper.update();
        const datasets = component.datasets;
        for (let i = 1; i < datasets.length; i++) {
          const dataset = datasets[i];
          const lastDataset = datasets[i - 1];

          if (this.descending) {
            expect(dataset[this.key] <= lastDataset[this.key]).to.be.true;
          } else {
            expect(dataset[this.key] >= lastDataset[this.key]).to.be.true;
          }
        }
      }

      for (let key of sortingKeys) {
        for (let order of sortingOrders) {
          let descending = order === 'descending';
          let test = testFunc.bind({
            key: key,
            descending: descending,
          });
          it(`should work when sorting by ${key} ${order}`, test);
        }
      }
    });

    describe('searching', () => {
      it('should filter down list to relevant datasets', () => {
        wrapper.setData({searchText: 'code'});
        // Only one of the mock datasets contains the word 'code' in it.
        expect(component.datasets.length).to.equal(1);
      });
    });
  });
});
