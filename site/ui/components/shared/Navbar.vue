<template>
  <div>
    <b-navbar toggleable type="inverse" variant="success">

      <b-nav-toggle target="nav_collapse"></b-nav-toggle>

      <b-link class="navbar-brand" to="/">
        <span>Geney</span>
      </b-link>

      <b-collapse is-nav id="nav_collapse">


        <b-nav is-nav-bar class="ml-auto" right-alignment>

          <b-nav-item-dropdown v-if="authenticated" right-alignment right :text="name">
            <b-dropdown-item to="/admin">Admin</b-dropdown-item>
            <b-dropdown-item @click="logout">Logout</b-dropdown-item>
          </b-nav-item-dropdown>

          <b-nav-item v-else to="/login">Login</b-nav-item>

        </b-nav>

      </b-collapse>


    </b-navbar>


    <b-navbar v-if="admin" toggleable class="no-z-index" style="background-color: #dedede;">

      <b-nav-toggle target="nav_collapse2"></b-nav-toggle>

      <b-collapse is-nav id="nav_collapse2">


        <b-nav is-nav-bar class="mx-auto">


          <b-nav-item to="/admin/datasets/">Datasets</b-nav-item>

          <b-nav-item >&nbsp;</b-nav-item>

          <b-nav-item to="/admin/users/">Users</b-nav-item>


        </b-nav>



      </b-collapse>


    </b-navbar>

    <div class="alerts-container">
      <transition v-for="(alert, index) in alerts">
        <div>
          <b-alert
            :variant="alert.variant"
            dismissible
            :show="alert.show">
            {{ alert.message }}
          </b-alert>
        </div>
      </transition>
    </div>

  </div>
</template>



<script>
import router from '../../router'

export default {
  name: 'navbar',
  data: function () {
    return {
      adminLinks: {
        datasets: {
          name: 'Manage Datasets',
          icon: '',
          options: [
            {
              description: 'Edit Datasets',
              name: 'ManageDatasets',
              path: '/admin/datasets/manage'
            },
            {
              description: 'Add Dataset',
              name: 'AddDatasets',
              path: '/admin/datasets/add'
            }
          ],
          privileges: ['datasets']
        },
        users: {
          name: 'Manage Users',
          icon: '',
          options: [
            {
              description: 'Edit/Remove Users',
              name: 'ManageUsers',
              path: '/admin/manage-users'
            },
            {
              description: 'Add User',
              name: 'AddUser',
              path: '/admin/add-user'
            }
          ],
          privileges: ['users']
        }
      }
    }
  },
  computed: {
    breadcrumbs () {
      var crumbs = []
      if (!this.admin) {
        crumbs.push({link: '/', text: 'Select Dataset', route: 'Home'})
        if (this.$store.state.dataset.id) {
          var datasetPath = '/dataset/' + this.$store.state.dataset.id + '/'
          crumbs.push({link: datasetPath, text: this.$store.state.dataset.name, route: 'Description'})
          if (this.$route.path.indexOf('filter') >= 0) {
            crumbs.push({link: datasetPath + 'filter', text: 'Filter', route: 'Filter'})
          }
          if (this.$route.path.indexOf('download') >= 0) {
            crumbs.push({link: datasetPath + 'download', text: 'Download', route: 'Download'})
          }
        }
      }
      crumbs[crumbs.length - 1].active = true
      return crumbs
    },
    currentRoute () {
      return this.$route.name
    },
    authenticated () {
      return this.$store.state.user && this.$store.state.user.username
    },
    name () {
      var user = this.$store.state.user
      if (user) {
        return user.firstname + ' ' + user.lastname
      }
      return null
    },
    admin () {
      for (var match of this.$route.matched) {
        if (match.name === 'Admin') {
          return true
        }
      }
      return false
    },
    alerts () {
      return this.$store.state.alerts
    }
  },
  methods: {
    logout () {
      this.$store.dispatch('logout')
      if (this.admin) {
        router.push('/')
      }
    },
    authorized (requiredPrivileges) {
      if (this.authenticated) {
        for (let privilege of requiredPrivileges) {
          if (this.$store.state.user.privileges.indexOf(privilege) === -1) {
            return false
          }
        }
        return true
      }
      return false
    }
  }
}
</script>

<style lang="scss" scoped>
.navbar {
  z-index: 1020;
}

.navbar-brand {
    img {
        height: 50px;
        margin-top: -15px;
    }
}
.navbar-right {
  z-index: 1020;
}

.no-z-index {
  z-index: 0 !important;
}

.alerts-container {
  display: table;
  position: fixed;
  top: 60px;
  right: 0px;
  z-index: 2400;
  clear: both;
  div {
    display: table-row;
    .alert {
      float: right;
      height: 50px;
    }
  }
}

</style>
