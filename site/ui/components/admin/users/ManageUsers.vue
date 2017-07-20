<template>

  <div class="manage-users">

    <h1>Users</h1>
    <div class="row">

      <b-form-fieldset horizontal label="Rows per page" class="col-4" :label-cols="6">
        <b-form-select :options="[{text:5,value:5},{text:10,value:10},{text:15,value:15}]" v-model="perPage">
        </b-form-select>
      </b-form-fieldset>

      <b-form-fieldset horizontal label="Filter" class="col-6" :label-cols="2">
        <b-form-input v-model="filter" placeholder="Type to Search"></b-form-input>
      </b-form-fieldset>

      <div class="col">
        <label>Add User &nbsp;</label>
        <router-link to="/admin/users/add" class="btn btn-success"><i class="fa fa-plus-square-o fa-lg" aria-hidden="true"></i></router-link>
      </div>


    </div>

    <b-table hover :fields="labels" :items="users" :current-page="currentPage" :per-page="perPage" :filter="filter">
      <template slot="name" scope="item">
        {{ item.item.firstname + ' ' + item.item.lastname }}
      </template>
      <template slot="privileges" scope="item">
        {{ item.item.privileges | jsonArray }}
      </template>
      <template slot="actions" scope="item">
        <router-link class="btn btn-sm btn-success" :to="'/admin/users/' + item.item.username"><i class="fa fa-edit fa-lg" aria-hidden="true"></i></router-link>
      </template>
    </b-table>

    <div class="justify-content-center row my-1">
      <b-pagination size="md" :total-rows="this.users && this.users.length" :per-page="perPage" v-model="currentPage"></b-pagination>
    </div>


  </div>
</template>

<script>
export default {
  name: 'manage_users',
  data () {
    return {
      users: [],
      labels: {
        name: {
          label: 'Name',
          sortable: true
        },
        username: {
          label: 'Username',
          sortable: true
        },
        email: {
          label: 'Email',
          sortable: true
        },
        privileges: {
          label: 'Privileges'
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
  created () {
    this.$store.dispatch('getUsers').then(users => {
      this.$set(this, 'users', users)
    })
  },
  computed: {
  },
  methods: {
  },
  filters: {
    jsonArray: function (value) {
      if (!value) return ''
      const arr = JSON.parse(value)
      if (Array.isArray(arr)) {
        return arr.join(', ')
      }
      return ''
    }
  }
}
</script>

<style lang="scss" scoped>

</style>
