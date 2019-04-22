<template>
  <div id="app">
    <navbar></navbar>

    <div id="content">
      <router-view></router-view>
    </div>
  </div>
</template>

<script>
import Navbar from './components/shared/Navbar';
// import router from './router'

export default {
  name: 'app',
  components: {Navbar},
  data () {
    return {
      // enterTransition: '',
      // leaveTransition: '',
    };
  },
  watch: {
    // this handles the animations
    $route (to, from) {
      // check if they're changing datasets
      if (to.params.dataset !== from.params.dataset) {
        // remove any set filters
        this.$store.commit('filters', null);
        this.$store.commit('selectedPathways', []);
        // make sure we have datasets
        if (this.$store.state.datasets) {
          // find dataset and set it in the store
          const dataset = this.$store.state.datasets[to.params.dataset] || {};
          this.$store.dispatch('setDataset', dataset);
        }
      }
    },
  },
  created () {
    // get all datasets when page loads
    this.$store.dispatch('getDatasets');
    // this.$store.dispatch('getUser');
  },
};
</script>

<style lang="scss">
h1, h2, h3 {
  font-weight: normal;
}
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  min-width: 600px;
  // color: #2c3e50; // change page wide text color

  .logo {
    height: 250px;
    // top: -25px;
    img {
      max-height: 250px;
    }
  }

  #content {
    position: relative;
    .top {
      position: absolute;
      left: 50%;
      transform: translateX(-50%);
      top: 25px;
      width: 100%;
    }

    .loader {
    border: 16px solid #f3f3f3; /* Light grey */
    border-top: 16px solid #28a745; /* Blue */
    border-radius: 50%;
    width: 120px;
    height: 120px;
    margin: 5rem auto;
    animation: spin 2s linear infinite;
    }

  }

  
  
  @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
  }

}
</style>
