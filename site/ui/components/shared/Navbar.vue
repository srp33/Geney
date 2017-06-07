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

          <b-nav-item v-for="privilege in privileges" class="privilege" :to="'/admin/' + privilege" v-if="">{{privilege | capitalize}}</b-nav-item>

        </b-nav>



      </b-collapse>


    </b-navbar>

    <div class="alerts-container">
      <div v-for="(alert, index) in alerts" :key="index">
        <b-alert
          :variant="alert.variant"
          dismissible
          :show="alert.show">
          {{ alert.message }}
        </b-alert>
      </div>
    </div>

  </div>
</template>



<script>
import router from '../../router'

export default {
  name: 'navbar',
  data () {
    return { }
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
    },
    privileges () {
      if (this.authenticated) {
        return this.$store.state.user.privileges
      }
      return []
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
  },
  filters: {
    capitalize: function (value) {
      if (!value) return ''
      value = value.toString()
      return value.charAt(0).toUpperCase() + value.slice(1)
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

.privilege {
  margin-left: 10px;
  margin-right: 10px;
}
</style>
