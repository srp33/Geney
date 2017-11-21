<template>
  <div class="card">
    <div class="card-block row justify-content-center">
      <h2 class="card-title col-12"><router-link :to="'/dataset/' + data.id">{{data.name}}</router-link></h2>
      <vue-markdown class="card-text" :class="{'truncated': hidden}" :source="data.description"></vue-markdown>
      <small class="change-size col-12" @click="toggleText()">
        <span v-if="hidden && truncated">Show More</span>
        <span v-if="!truncated && !hidden">Show Less</span>
      </small>

      <router-link :to="'/dataset/' + data.id" class="btn btn-primary margin-top-15">View</router-link>
    </div>
    <div class="card-footer">
      <!--<router-link :to="'/dataset/' + data.id" class="btn btn-primary">View</router-link>-->
      <small class="text-muted">Uploaded on {{ uploadDate }}</small>
    </div>
  </div>
</template>


<script>
import VueMarkdown from 'vue-markdown';
import Vue from 'vue';
import $ from 'jquery';

export default {
  name: 'dataset-detail',
  props: ['data'],
  components: { VueMarkdown },
  data () {
    return {
      truncated: true,
      hidden: true,
    };
  },
  computed: {
    uploadDate () {
      let date = new Date(this.data.uploadDate * 1000);
      return date.toLocaleDateString();
    },
  },
  mounted () {
    this.checkTruncated();
  },
  methods: {
    toggleText () {
      this.$set(this, 'hidden', !this.hidden);
      // wait one tick to reset masonry
      this.$nextTick(() => {
        Vue.redrawVueMasonry();
        this.checkTruncated();
      });
    },
    checkTruncated () {
      let elem = $(this.$el);
      let cardText = elem.find('.card-text');
      let textHeight = 0;
      cardText.children().each(function () {
        textHeight += $(this).height();
      });
      this.$set(this, 'truncated', this.hidden && (cardText.height() < textHeight));
    },
  },
  watch: {
    data () {
      this.$set(this, 'hidden', true);
      this.$nextTick(() => {
        this.checkTruncated();
      });
    },
  },
};
</script>

<style lang="scss" scoped>

.change-size {
  cursor: pointer;
  color: #0275D8;
}
.truncated {
  max-height: 150px;
  text-overflow: ellipsis;
  overflow: hidden;
}
.card-title {
  a {
    color: inherit;
    text-decoration: none;
  }
}
.margin-top-15 {
  margin-top: 15px;
}
.card-text {
  width: 100%;
  text-align: left;
  padding: 0px 5px 0px 5px;
}

</style>
