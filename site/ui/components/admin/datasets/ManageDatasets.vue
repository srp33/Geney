<template>

  <div class="manage-datasets">

    <h1>Datasets</h1>
    <div class="row">

      <b-form-fieldset horizontal label="Rows per page" class="col-4" :label-cols="6">
        <b-form-select :options="[{text:5,value:5},{text:10,value:10},{text:15,value:15}]" v-model="perPage">
        </b-form-select>
      </b-form-fieldset>

      <b-form-fieldset horizontal label="Filter" class="col-6" :label-cols="2">
        <b-form-input v-model="filter" placeholder="Type to Search"></b-form-input>
      </b-form-fieldset>

      <div class="col">
        <label>Add Dataset &nbsp;</label>
        <router-link to="/admin/datasets/add" class="btn btn-success"><i class="fa fa-plus-square-o fa-lg" aria-hidden="true"></i></router-link>
      </div>


    </div>

    <b-table hover :fields="labels" :items="datasets" :current-page="currentPage" :per-page="perPage" :filter="filter">
      <template slot="uploadDate" scope="item">
        {{ (new Date(item.item.uploadDate)).toLocaleDateString() }}
      </template>
      <template slot="actions" scope="item">
        <router-link class="btn btn-sm btn-success" :to="'/admin/datasets/' + item.item.id"><i class="fa fa-edit fa-lg" aria-hidden="true"></i></router-link>
      </template>
    </b-table>

    <div class="justify-content-center row my-1">
      <b-pagination size="md" :total-rows="this.datasets && this.datasets.length" :per-page="perPage" v-model="currentPage" />
    </div>

  </div>
</template>


<script>
export default {
  name: 'manage_datasets',
  data () {
    return {
      labels: {
        name: {
          label: 'Name',
          sortable: true
        },
        id: {
          label: 'ID',
          sortable: true
        },
        uploadDate: {
          label: 'Upload Date',
          sortable: true
        },
        actions: {
          label: 'Edit'
        }
      },
      currentPage: 1,
      perPage: 5,
      filter: null
    };
  },
  mounted () {

  },
  computed: {
    datasets () {
      return this.$store.state.datasets;
    }
  },
  methods: {
  }
};
</script>

<style lang="scss" scoped>

</style>
