import Vue from 'vue';
import Download from 'ui/components/main/Download';
import Vuex from 'vuex';
import VueRouter from 'vue-router';
import VueResource from 'vue-resource';
import chai, { expect } from 'chai';
import { stub, spy } from 'sinon';
import sinonChai from 'sinon-chai';
import { mount } from 'avoriaz';
import { expectShallowEqual } from 'test/helpers.js';

chai.use(sinonChai);

Vue.use(Vuex);
Vue.use(VueRouter);
Vue.use(VueResource);

describe('Download.vue', () => {
  let router;
  let storeData;
  let store;
  let wrapper;
  // let component;

  beforeEach(() => {
    router = new VueRouter({
      routes: [
        {
          path: '/dataset/:dataset',
        },
      ],
    });
  });

  describe('with valid filters', () => {
    beforeEach(() => {
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
      router.push('/dataset/bestdatasetevar');
      stub(Vue.http, 'post').withArgs('/api/datasets/bestdatasetevar/samples', storeData.state.filters.meta);
    });

    afterEach(() => {
      window.history.replaceState({}, '', '/');
      Vue.http.post.restore();
    });

    describe('querying for number of samples', () => {
      it('valid response should show the number of samples', done => {
        Vue.http.post.resolves({body: 1234});
        wrapper = mount(Download, { store, router });

        Vue.nextTick(() => {
          console.log(wrapper.find('#num-samples-selected'));
          expect(wrapper.find('#num-samples-selected').length).to.equal(1);
          expect(wrapper.find('#num-samples-error').length).to.equal(0);
          done();
        });
      });

      it('invalid response should show error message', done => {
        Vue.http.post.rejects();
        wrapper = mount(Download, { store, router });

        Vue.nextTick(() => {
          expect(wrapper.find('#num-samples-selected').length).to.equal(0);
          expect(wrapper.find('#num-samples-error').length).to.equal(1);
          done();
        });
      });
    });

    describe('download', () => {
      beforeEach(() => {
        Vue.http.post.resolves({body: 1234});
        wrapper = mount(Download, { store, router });
      });

      it('should create a form and submit it', () => {
        const formMock = {
          setAttribute: spy(),
          submit: spy(),
          appendChild: spy(),
        };
        const inputMock = {
          setAttribute: spy(),
        };
        stub(document, 'createElement')
          .withArgs('form').returns(formMock)
          .withArgs('input').returns(inputMock);
        stub(document.body, 'appendChild');
        wrapper.vm.download();

        expect(document.createElement).to.have.been.calledTwice;

        expect(formMock.submit).to.have.been.calledOnce;
        expect(formMock.setAttribute).to.have.been.calledWithExactly('method', 'post');
        expect(formMock.setAttribute).to.have.been.calledWithExactly('action', '/api/datasets/bestdatasetevar/download');
        expect(formMock.setAttribute).to.have.been.calledWithExactly('target', '_blank');
        expect(formMock.appendChild).to.have.been.calledWithExactly(inputMock);

        expect(inputMock.setAttribute).to.have.been.calledWithExactly('type', 'hidden');
        expect(inputMock.setAttribute).to.have.been.calledWithExactly('name', 'query');

        const payloadCall = inputMock.setAttribute.getCall(2);
        expect(payloadCall.args[0]).to.equal('value');
        const payload = JSON.parse(payloadCall.args[1]);
        expectShallowEqual(wrapper.vm.$data.options, payload.options);

        // remove the options key, since the rest of the payload should be the same as the filters
        delete payload.options;
        expectShallowEqual(storeData.state.filters, payload);

        document.createElement.restore();
        document.body.appendChild.restore();
      });
    });
  });
});
