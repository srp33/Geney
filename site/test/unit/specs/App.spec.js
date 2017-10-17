import Vue from 'vue';
import App from 'ui/App';
import Vuex from 'vuex';
import VueRouter from 'vue-router';
import VueMasonryPlugin from 'vue-masonry';
import BootstrapVue from 'bootstrap-vue';
import chai, { expect } from 'chai';
import { stub } from 'sinon';
import { mount } from 'avoriaz';
import sinonChai from 'sinon-chai';

chai.use(sinonChai);

Vue.use(Vuex);
Vue.use(VueMasonryPlugin);
Vue.use(VueRouter);
Vue.use(BootstrapVue);

describe('App.vue', () => {
  let store;
  let storeData;
  let router;
  let component;
  let wrapper;

  describe('changing routes', () => {
    beforeEach(() => {
      router = new VueRouter({
        routes: [
          {
            path: '/dataset/:dataset',
          },
        ],
      });

      storeData = {
        state: {
          dataset: {},
          datasets: {
            'bestdatasetevar': {
              foo: 'bar',
            },
            'anotherdataset': {
              bar: 'foo',
            },
          },
        },
        mutations: {
          filters: stub(),
        },
        actions: {
          getDatasets: stub(),
          getUser: stub(),
          setDataset: stub(),
        },
      };
      store = new Vuex.Store(Object.assign({}, storeData));

      wrapper = mount(App, { store, router });
      component = wrapper.vm;
    });

    afterEach(() => {
      window.history.replaceState({}, '', '/');
    });

    it('should set correct dataset when it exists', done => {
      router.push('/dataset/bestdatasetevar', () => {
        Vue.nextTick(() => {
          expect(storeData.mutations.filters).to.have.been.calledWith(component.$store.state, null);
          const setDatasetCall = storeData.actions.setDataset.getCall(0);
          expect(setDatasetCall.args[1]).to.equal(storeData.state.datasets['bestdatasetevar']);
          done();
        });
      });
    });

    it('should set empty dataset when it does not exists', done => {
      router.push('/dataset/nonexistentdataset', () => {
        Vue.nextTick(() => {
          expect(storeData.mutations.filters).to.have.been.calledWith(component.$store.state, null);
          const setDatasetCall = storeData.actions.setDataset.getCall(0);
          // expect an empty object to have been set
          // because chai is making sure they're exactly the same object
          // we have to make sure there are just no keys on the object
          expect(Object.keys(setDatasetCall.args[1]).length).to.be.equal(0);
          done();
        });
      });
    });

    it('should do nothing if dataset did not change', done => {
      router.push('/other/route', () => {
        Vue.nextTick(() => {
          expect(storeData.mutations.filters).to.not.have.been.called;
          expect(storeData.actions.setDataset).to.not.have.been.called;
          done();
        });
      });
    });
  });
});
