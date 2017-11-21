import Vue from 'vue';

Vue.filter('capitalize', value => {
  if (typeof value === 'string') {
    const words = value.split(/\s+/);
    for (let i = 0; i < words.length; i++) {
      words[i] = words[i].charAt(0).toUpperCase() + words[i].slice(1);
    }
    return words.join(' ');
  }
});

Vue.filter('uppercase', value => {
  if (typeof value === 'string') {
    return value.toUpperCase();
  }
});
