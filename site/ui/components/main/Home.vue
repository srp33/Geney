<template>

  <div class="home top">
    <div class="logo">
      <img src="../../assets/geney-no-lamp.png">
    </div>
    <div class="row justify-content-center width-100">
      <div class="col-8">
        <h1>Please select a dataset</h1>
        
        <div class="row">
          <div class="form-group col-6">
            <input class="form-control" type="text" v-model="searchText" placeholder="Search">
          </div>

          <div class="form-group col-6">
            <select class="form-control"  v-model="sortField">
              <option value="uploadDate">Date Added</option>
              <option value="name">Dataset Name</option>
              <option value="numSamples">Number of Samples</option>
            </select>
          </div>
        </div>
        <div v-masonry transition-duration="0.3s" item-selector=".item" class="row">
          <div v-masonry-tile class="item col-xs-12 col-sm-6" v-for="(dataset, index) in datasets" :key="dataset.id">
            <dataset-detail :data="dataset" ></dataset-detail>
          </div>
        </div>

      </div>
    </div>
    
  </div>
</template>

<script>
import DatasetDetail from '../shared/DatasetDetail'
import Sifter from 'sifter'
import Vue from 'vue'

export default {
  name: 'home',
  components: { DatasetDetail },
  data () {
    return {
      searchText: '',
      sortField: 'uploadDate'
    }
  },
  updated () {
  },
  computed: {
    sifter () {
      return new Sifter(this.$store.state.datasets)
    },
    datasets () {
      // return this.$store.state.datasets
      if (this.sifter.items && this.sifter.items.length) {
        let result = this.sifter.search(this.searchText, {
          fields: ['name', 'description', 'id']
        })
        let datasets = []
        for (let item of result.items) {
          datasets.push(this.sifter.items[item.id])
        }
        datasets.sort(this.dynamicSort(this.sortField))
        this.reloadMasonry()
        return datasets
      }
      return []
    }
  },
  methods: {
    reloadMasonry () {
      setTimeout(() => {
        Vue.redrawVueMasonry()
      }, 50)
    },
    dynamicSort (property) {
      var sortOrder = 1
      if (property[0] === '-') {
        sortOrder = -1
        property = property.substr(1)
      }
      return function (a, b) {
        var result = (a[property] < b[property]) ? -1 : (a[property] > b[property]) ? 1 : 0
        return result * sortOrder
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.item {
  padding: 15px;
}
.padding-right-0 {
  padding-right: 0px;
}
.width-100 {
  max-width: 100%;
}
</style>
