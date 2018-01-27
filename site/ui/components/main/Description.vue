<template>

  <div class="description top" v-if="dataset">
    <img class="logo" src="../../assets/geney-no-lamp.png">
    <h1 id="dataset-name">{{ dataset.title }}</h1>
    <h4 id="dataset-description">
      <vue-markdown :source="dataset.description"></vue-markdown>
    </h4>
    <ul class="meta-types">
      <li>
        <i class="fa fa-2x fa-align-justify" aria-hidden="true"></i>
        <br>
        <span id="dataset-num-samples">{{ dataset.numSamples }} Samples</span>
      </li>
      <li>
        <i class="fa fa-2x fa-flask" aria-hidden="true"></i>
        <br>
        <span id="dataset-num-features">{{ dataset.numFeatures }} {{ dataset.featureDescriptionPlural | capitalize }}</span>
      </li>
      <li>
        <i class="fa fa-2x fa-gears" aria-hidden="true"></i>
        <br>
        <span id="dataset-num-meta-types">{{ dataset.numMetaTypes }} Meta Data Variables</span>
      </li>
    </ul>
    <router-link :to="'/dataset/' + dataset.id + '/filter'" class="btn btn-primary btn-lg" id="dataset-next-btn">Select Samples</router-link>
  </div>
</template>

<script>
import VueMarkdown from 'vue-markdown';

export default {
  name: 'description',
  components: { VueMarkdown },
  data () {
    return {
    };
  },
  computed: {
    dataset () {
      return this.$store.state.dataset;
    },
  },
};
</script>

<style lang="scss" scoped>

.meta-types {
  list-style-type: none;
  padding: 0;
  margin-top: 25px;
  margin-bottom: 50px;
  li {
    // display: inline-block;
    margin: 15px 10px;
    font-size: 1.25em;
  }
}
#dataset-description {
  text-align: left;
  padding: 0 50px;
}
</style>
