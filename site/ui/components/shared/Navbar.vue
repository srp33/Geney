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


    <!--TOP NAVBAR
    <nav class="navbar navbar-default">
      <div class="container-fluid">
        <div class="navbar-header">
          <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#bs-example-navbar-collapse-1"
            aria-expanded="false">
            <span class="sr-only">Toggle navigation</span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
        </button>
          <router-link class="navbar-brand" to="/">Geney</router-link>
        </div>

        <div class="collapse navbar-collapse" id="bs-example-navbar-collapse-1">

          <ul class="nav navbar-nav navbar-right">
            <li class="dropdown" v-if="authenticated">
              <a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">{{name}} <span class="caret"></span></a>
              <ul class="dropdown-menu">
                <li><router-link to="/admin">Admin</router-link></li>
                <li role="separator" class="divider"></li>
                <li><a @click="logout">Logout</a></li>
              </ul>
            </li>
            <li class="authentication" v-else>
              <router-link to="/login">Login</router-link>
            </li>
          </ul>
        </div>
      </div>

      <div class="navbar-form navbar-center">
        <b-breadcrumb :items="breadcrumbs" />
      </div>

    </nav>-->
    <!--SIDE ADMIN NAVBAR-->
    <!--<div v-if="admin" class="side-menu">

      <nav class="navbar navbar-default" role="navigation">

        <div class="side-menu-container">
          <ul class="nav navbar-nav">-->

            <!--<li v-for="link in adminLinks" :class="{ active: currentRoute === link.name }">
              <router-link :to="link.path">{{link.name}}</router-link>
            </li>-->
<!--
            <li class="panel panel-default" id="dropdown" v-for="(value, key) in adminLinks" v-if="authorized(value.privileges)">
              <a data-toggle="collapse" :href="'#' + key">
                <i class="fa fa-table fa-lg" aria-hidden="true"></i> {{value.name}} <span class="caret"></span>
              </a>

              <div :id="key" class="panel-collapse collapse">
                <div class="panel-body">
                  <ul class="nav navbar-nav">
                    <li v-for="link in value.options" :class="{active: $route.path === link.path}">
                      <router-link :to="link.path">{{link.description}}</router-link>
                    </li>
                  </ul>
                </div>
              </div>
            </li>

          </ul>
        </div>
      </nav>

    </div>-->

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


</style>
