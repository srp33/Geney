<template>

  <div class="home top">
    <div class="logo">
      <img src="../../assets/geney-no-lamp.png">
    </div>
    <div class="row justify-content-center width-100">
      <div class="col-8">
        <h1>Please select a dataset</h1>

        <div class="row" style="margin-bottom:1rem;">
          <div class="form-group col-md-6 col-sm-12 text-left" style="margin-bottom:0px;">
            <!-- <label>Search</label> -->
            <input class="form-control" type="text" v-model="searchText" placeholder="Search">
          </div>

          <div class="form-group col-md-6 col-sm-12 text-left">
            <!-- <label>Sort</label> -->
            <div class="input-group">
              <selectize
                :options="sort.options"
                :value="sort.selected"
                @updated="x => sort.selected = x"
                :settings="sort.settings"></selectize>

                <span class="input-group-btn">
                  <button class="btn btn-primary" type="button" @click="() => sort.descending = !sort.descending">
                    <i class="fa fa-arrow-down" aria-hidden="true" v-if="sort.descending"></i>
                    <i class="fa fa-arrow-up" aria-hidden="true" v-if="!sort.descending"></i>
                  </button>
                </span>
            </div>
          </div>

          <!-- <div class="input-group col-6">
            <input class="form-control" type="text" placeholder="Search">
              <span class="input-group-btn">
                <button class="btn btn-primary" type="button"><i class="fa fa-arrow-down" aria-hidden="true"></i></button>
              </span>
          </div> -->

        </div>
        <div v-masonry transition-duration="0.3s" item-selector=".dataset-item" class="row">
          <div v-masonry-tile class="dataset-item col-xs-12 col-sm-6" v-for="(dataset, index) in datasets" :key="dataset.id">
            <dataset-detail :data="dataset" ></dataset-detail>
          </div>
        </div>

      </div>
    </div>

  </div>
</template>

<script>
import DatasetDetail from '../shared/DatasetDetail';
import Sifter from 'sifter';
import Vue from 'vue';
import selectize from '../shared/Selectize';

export default {
  name: 'home',
  components: { DatasetDetail, selectize },
  data () {
    return {
      searchText: '',
      sort: {
        options: [
          {
            value: 'uploadDate',
            label: 'Date Added',
          },
          {
            value: 'name',
            label: 'Dataset Name',
          },
          {
            value: 'numSamples',
            label: 'Number of Samples',
          },
        ],
        settings: {
          maxItems: 1,
          valueField: 'value',
          labelField: 'label',
          render: {
            item (item, escape) {
              return `<div class='item' data-value='${item.value}'>${escape('Sort by: ' + item.label)}</div>`;
            },
          },
        },
        selected: 'uploadDate',
        descending: true,
      },
    };
  },
  updated () {
  },
  computed: {
    sifter () {
      const datasets = this.$store.state.datasets || {};
      return new Sifter(Object.values(datasets));
    },
    datasets () {
      if (this.sifter.items && this.sifter.items.length) {
        let result = this.sifter.search(this.searchText, {
          fields: ['name', 'description', 'id'],
        });
        let datasets = [];
        for (let item of result.items) {
          datasets.push(this.sifter.items[item.id]);
        }
        datasets.sort(
          this.dynamicSort(
            this.sort.descending ? '-' + this.sort.selected : this.sort.selected
          )
        );
        this.reloadMasonry();
        return datasets;
      }
      return [];
    },
  },
  methods: {
    reloadMasonry () {
      setTimeout(() => {
        Vue.redrawVueMasonry();
      }, 50);
    },
    dynamicSort (property) {
      let sortOrder = 1;
      if (property[0] === '-') {
        sortOrder = -1;
        property = property.substr(1);
      }
      return (a, b) => {
        const result = (a[property] < b[property]) ? -1 : (a[property] > b[property]) ? 1 : 0;
        return result * sortOrder;
      };
    },
  },
};
</script>

<style lang="scss" scoped>
.dataset-item {
  padding: 15px;
}
.padding-right-0 {
  padding-right: 0px;
}
.width-100 {
  max-width: 100%;
}
</style>
