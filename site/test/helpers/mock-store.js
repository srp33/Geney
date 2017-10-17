import Vue from 'vue';
import Vuex from 'vuex';
// import sinon from 'sinon';
import BaseState from 'ui/store/state';
import BaseMutations from 'ui/store/mutations';
import BaseActions from 'ui/store/actions';

Vue.use(Vuex);

function getMockedStore (mockState, mockActions) {
  let newState;
  let newActions;
  if (mockState) {
    newState = Object.assign(BaseState, mockState);
  }
  if (mockActions) {
    if (Array.isArray(mockActions)) {
      for (let action of BaseActions) {
        if (mockActions.indexOf(action) === -1) {
          BaseActions[action] = sinon.spy();
        }
      }
    } else if (typeof mockActions === 'object') {
      newActions = Object.assign(BaseActions, mockActions);
    }
  } else {
    // for (let action of BaseActions) {
    //   BaseActions[action] = sinon.spy();
    // }
  }

  // console.info(newState);
  return new Vuex.Store({
    state: newState || BaseState,
    mutations: BaseMutations,
    actions: newActions || BaseActions,
  });
}

export {
  getMockedStore
};
