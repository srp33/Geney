<template>
  <div id="app">
    <navbar></navbar>

    <div id="content">
      <!--<transition :enter-active-class="enterTransition" :leave-active-class="leaveTransition" >-->
        <router-view></router-view>
      <!--</transition>-->
    </div>
  </div>
</template>

<script>
import Navbar from './components/shared/Navbar'
// import router from './router'

export default {
  name: 'app',
  components: {Navbar},
  data () {
    return {
      enterTransition: '',
      leaveTransition: ''
    }
  },
  watch: {
    // this handles the animations
    $route (to, from) {
      // check if they're changing datasets
      if (to.params.dataset !== from.params.dataset) {
        // remove any set filters
        this.$store.commit('filters', null)
        var dataset = {}
        // find dataset and set it in the store
        for (var x of this.$store.state.datasets) {
          if (x.id === to.params.dataset) {
            dataset = x
            break
          }
        }
        this.$store.dispatch('setDataset', dataset)
      }

      if (to.name === '404' || from.name === '404' || to.name === 'DatasetNotFound' || from.name === 'DatasetNotFound') {
        this.enterTransition = ''
        this.leaveTransition = ''
        return
      }

      // n => n is truthy when n.length > 0, so this filters out empty strings
      const toDepth = to.path.split('/').filter(n => n).length
      const fromDepth = from.path.split('/').filter(n => n).length
      if (toDepth < fromDepth) {
        this.enterTransition = 'animated slideInLeft'
        this.leaveTransition = 'animated slideOutRight'
      } else if (toDepth > fromDepth) {
        this.enterTransition = 'animated slideInRight'
        this.leaveTransition = 'animated slideOutLeft'
      } else {
        this.enterTransition = ''
        this.leaveTransition = ''
      }
    }
  },
  created () {
    // get all datasets when page loads
    this.$store.dispatch('getDatasets')
    this.$store.dispatch('getAuth')
  }
}

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
  // color: #2c3e50; // change page wide text color

  .logo {
    height: 250px;
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
      top: 0px;
      width: 100%;
    }
  }


/* Transitions from Animate.css */
.animated {
  animation-duration: 0.8s;
  animation-fill-mode: both;
}

$from: 300%;
$to: -50%;

@keyframes slideInRight {
  from {
    transform: translate3d($from, 0, 0);
    visibility: visible;
  }

  to {
    transform: translate3d($to, 0, 0);
  }
}
.slideInRight {
  animation-name: slideInRight;
}
@keyframes slideInLeft {
  from {
    transform: translate3d(-$from, 0, 0);
    visibility: visible;
  }

  to {
    transform: translate3d($to, 0, 0);
  }
}

.slideInLeft {
  animation-name: slideInLeft;
}
@keyframes slideOutLeft {
  from {
    transform: translate3d($to, 0, 0);
  }

  to {
    visibility: hidden;
    transform: translate3d(-$from, 0, 0);
  }
}

.slideOutLeft {
  animation-name: slideOutLeft;
}
@keyframes slideOutRight {
  from {
    transform: translate3d($to, 0, 0);
  }

  to {
    visibility: hidden;
    transform: translate3d($from, 0, 0);
  }
}

.slideOutRight {
  animation-name: slideOutRight;
}

}
</style>
