import { expect } from 'chai';

function expectShallowEqual (data, expected) {
  for (let key of Object.keys(data)) {
    if (typeof data[key] === 'object') {
      expectShallowEqual(data[key], expected[key]);
    } else {
      expect(data[key]).to.equal(expected[key]);
    }
    delete expected[key];
  }
  expect(Object.keys(expected).length).to.equal(0);
}

export {
  expectShallowEqual
};
