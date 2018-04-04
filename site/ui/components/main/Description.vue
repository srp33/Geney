<template>

  <div class="description top" v-if="dataset">
    <img class="logo" src="../../assets/geney-no-lamp.png">
    <h1 id="dataset-name">{{ dataset.title }}</h1>
    <h4 id="dataset-description">
      <vue-markdown :class="{'truncated': hidden}" :source="dataset.description"></vue-markdown>
      <small class="change-size" @click="toggleText()">
        <span v-if="hidden && truncated">Show More</span>
        <span v-if="!truncated && !hidden">Show Less</span>
      </small>
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
      truncated: true,
      hidden: true,
    };
  },
  computed: {
    dataset () {
      return this.$store.state.dataset;
    },
  },
  methods: {
    toggleText () {
      this.$set(this, 'hidden', !this.hidden);
      this.$set(this, 'truncated', !this.truncated);
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

.change-size {
  cursor: pointer;
  color: #0275D8;
  padding: 0;
  display: block;
  text-align: center;
  margin-top: 5px;
}

.truncated {
  max-height: 120px;
  text-overflow: ellipsis;
  overflow: hidden;
}

#dataset-description {
  text-align: left;
  padding: 0 50px;
}
</style>
