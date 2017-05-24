<template>

  <div class="manage-datasets">

    <h1>Datasets</h1>
    <!--<v-table :settings="tableSettings" :rows="datasets"></v-table>-->

    <div class="row">

      <b-form-fieldset horizontal label="Rows per page" class="col-4" :label-size="6">
        <b-form-select :options="[{text:5,value:5},{text:10,value:10},{text:15,value:15}]" v-model="perPage">
        </b-form-select>
      </b-form-fieldset>

      <b-form-fieldset horizontal label="Filter" class="col-6" :label-size="2">
        <b-form-input v-model="filter" placeholder="Type to Search"></b-form-input>
      </b-form-fieldset>

      <div class="col">
        <label>Add Dataset &nbsp;</label>
        <router-link to="/admin/datasets/add" class="btn btn-success"><i class="fa fa-plus-square-o fa-lg" aria-hidden="true"></i></router-link>
      </div>


    </div>

    <v-table hover :fields="labels" :items="datasets" :current-page="currentPage" :per-page="perPage" :filter="filter">
      <template slot="uploadDate" scope="item">
        {{ (new Date(item.item.uploadDate)).toLocaleDateString() }}
      </template>
      <template slot="actions" scope="item">
        <router-link class="btn btn-sm btn-success" :to="'/admin/datasets/' + item.item.id"><i class="fa fa-edit fa-lg" aria-hidden="true"></i></router-link>
      </template>
    </v-table>

    <div class="justify-content-center row my-1">
      <b-pagination size="md" :total-rows="this.datasets && this.datasets.length" :per-page="perPage" v-model="currentPage" />
    </div>
    
  </div>
</template>


<script>
import VTable from '../../shared/VTable'

export default {
  name: 'manage_datasets',
  components: {VTable},
  data () {
    return {
      mde: null,
      tableSettings: {
        cols: [
          {
            label: 'Name',
            prop: 'name'
          },
          {
            label: '# of Samples',
            prop: 'numSamples'
          },
          {
            label: '# of Genes',
            prop: 'numGenes'
          },
          {
            label: '# of Meta Types',
            prop: 'numMetaTypes'
          },
          {
            label: 'Edit',
            prop: null,
            btn: {
              class: 'btn btn-success',
              icon: 'fa fa-pencil'
            }
          }
        ]
      },
      items: [
        {
          isActive: true,
          age: 40,
          name: {
            first: 'Dickerson',
            last: 'Macdonald'
          }
        },
        {
          isActive: false,
          age: 21,
          name: {
            first: 'Larsen',
            last: 'Shaw'
          }
        },
        {
          isActive: false,
          age: 9,
          state: 'success',
          name: {
            first: 'Mitzi',
            last: 'Navarro'
          }
        },
        {
          isActive: false,
          age: 89,
          name: {
            first: 'Geneva',
            last: 'Wilson'
          }
        },
        {
          isActive: true,
          age: 38,
          name: {
            first: 'Jami',
            last: 'Carney'
          }

        },
        {
          isActive: false,
          age: 27,
          name: {
            first: 'Essie',
            last: 'Dunlap'
          }

        },
        {
          isActive: true,
          age: 40,
          name: {
            first: 'Dickerson',
            last: 'Macdonald'
          }

        },
        {
          isActive: false,
          age: 21,
          name: {
            first: 'Larsen',
            last: 'Shaw'
          }

        },
        {
          isActive: false,
          age: 26,
          name: {
            first: 'Mitzi',
            last: 'Navarro'
          }

        },
        {
          isActive: false,
          age: 22,
          name: {
            first: 'Geneva',
            last: 'Wilson'
          }

        },
        {
          isActive: true,
          age: 38,
          name: {
            first: 'Jami',
            last: 'Carney'
          }

        },
        {
          isActive: false,
          age: 27,
          name: {
            first: 'Essie',
            last: 'Dunlap'
          }
        }
      ],
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
    }
  },
  mounted () {

  },
  computed: {
    datasets () {
      return this.$store.state.datasets
    }
  },
  methods: {
  }
}
</script>

<style lang="scss" scoped>
.CodeMirror {
	max-height: 300px;
}
</style>
