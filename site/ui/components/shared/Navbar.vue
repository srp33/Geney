<template>
  <div>
    <!--TOP NAVBAR-->
    <nav class="navbar navbar-default">
      <div class="container-fluid">
        <!-- Brand and toggle get grouped for better mobile display -->
        <div class="navbar-header">
          <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#bs-example-navbar-collapse-1"
            aria-expanded="false">
            <span class="sr-only">Toggle navigation</span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
        </button>
          <router-link class="navbar-brand" to="/">
            <!--<img alt="Brand" src="../assets/geney-square.png">-->
            Bio Geney
          </router-link>
        </div>

        <!-- Collect the nav links, forms, and other content for toggling -->
        <div class="collapse navbar-collapse" id="bs-example-navbar-collapse-1">
          <!--<ul class="nav navbar-nav">
            <li><router-link to="/" >Home</router-link></li>
          </ul>-->

          <ul class="nav navbar-nav navbar-right">
            <li v-if="authenticated"><router-link to="/admin">Admin</router-link></li>
            <li class="authentication">
              <router-link to="/login" v-if="!authenticated">Login</router-link>
              <a v-if="authenticated" @click="logout">Logout</a>
            </li>
          </ul>
        </div>
        <!-- /.navbar-collapse -->
      </div>
      <!-- /.container-fluid -->

      <div class="navbar-form navbar-center">
        <ol class="breadcrumb">
          <li v-for="crumb in breadcrumbs" :class="{ active: currentRoute === crumb.route }">
            <router-link v-if="currentRoute !== crumb.route" :to="crumb.path">{{crumb.name}}</router-link>
            <span v-else>{{crumb.name}}</span>
          </li>
        </ol>
      </div>

    </nav>
    <!--SIDE ADMIN NAVBAR-->
    <div v-if="admin" class="side-menu">

      <nav class="navbar navbar-default" role="navigation">

        <div class="side-menu-container">
          <ul class="nav navbar-nav">

            <!--<li v-for="link in adminLinks" :class="{ active: currentRoute === link.name }">
              <router-link :to="link.path">{{link.name}}</router-link>
            </li>-->

            <li class="panel panel-default" id="dropdown" v-for="(value, key) in adminLinks">
              <a data-toggle="collapse" :href="'#' + key">
                <i class="fa fa-table fa-lg" aria-hidden="true"></i> {{value.name}} <span class="caret"></span>
              </a>

              <div :id="key" class="panel-collapse collapse">
                <div class="panel-body">
                  <ul class="nav navbar-nav">
                    <li v-for="link in value.options">
                      <router-link :to="link.path">{{link.description}}</router-link>
                    </li>
                  </ul>
                </div>
              </div>
            </li>

          </ul>
        </div>
      </nav>

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
              description: 'Edit/Remove Datasets',
              name: 'ManageDatasets',
              path: '/admin/manage-datasets'
            },
            {
              description: 'Add Dataset',
              name: 'AddDatasets',
              path: '/admin/add-dataset'
            }
          ]
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
          ]
        }
      }
    }
  },
  computed: {
    breadcrumbs () {
      var crumbs = []
      if (!this.admin) {
        crumbs.push({path: '/', name: 'Select Dataset', route: 'Home'})
        if (this.$store.state.dataset.id) {
          var datasetPath = '/dataset/' + this.$store.state.dataset.id + '/'
          crumbs.push({path: datasetPath, name: this.$store.state.dataset.name, route: 'Description'})
          if (this.$route.path.indexOf('filter') >= 0) {
            crumbs.push({path: datasetPath + 'filter', name: 'Filter', route: 'Filter'})
          }
          if (this.$route.path.indexOf('download') >= 0) {
            crumbs.push({path: datasetPath + 'download', name: 'Download', route: 'Download'})
          }
        }
      }
      return crumbs
    },
    currentRoute () {
      return this.$route.name
    },
    authenticated () {
      return this.$store.state.user && this.$store.state.user.username
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
@media (min-width: 768px) {
  .navbar-form.navbar-center {
    position: absolute;
    left: 50%;
    transform: translateX(-50%);
    width: 75%;
    top: 0px;
    .form-group {
      min-width: 300px;
    }
  }

  .breadcrumb {
    background-color: inherit !important;
  }
}
@media (max-width: 768px) {
  .navbar-form.navbar-center {
    display: none;
  }
}

.authentication {
  cursor: pointer;
}

#loginmodal {
  padding-top: 15%;

  .modal-dialog {
    max-width: 400px;
  }
}


.side-menu {
  position: fixed;
  top: 50px !important;
  left: 0px !important;
  width: 200px;
  height: 100%;
  background-color: #f8f8f8;
  border-right: 1px solid #e7e7e7;
  z-index: 8;

  .navbar {
    border: none;
  }
  .navbar-header {
    width: 100%;
    border-bottom: 1px solid #e7e7e7;
  }
  .navbar-nav .active a {
    background-color: transparent;
    margin-right: -1px;
    border-right: 5px solid #42f46b;
  }
  .navbar-nav li {
    display: block;
    width: 100%;
    border-bottom: 1px solid #e7e7e7;

    a {
      padding: 15px;
      border-right: 5px solid #f8f8f8;
    }

  .glyphicon {
    padding-right: 10px;
  }

  }


  #dropdown {
    border: 0;
    margin-bottom: 0;
    border-radius: 0;
    background-color: transparent;
    box-shadow: none;

    .caret {
      float: right;
      margin: 9px 5px 0;
    }

    .indicator {
      float: right;
    }

    a {
      border-bottom: 1px solid #e7e7e7;
    }

    .panel-body {
      padding: 0;
      background-color: #f3f3f3;

      .navbar-nav {
        width: 100%;

        li {
          padding-left: 15px;
          border-bottom: 1px solid #e7e7e7;

          :last-child {
            border-bottom: none;
          }

        }

      }

      .panel > a {
        margin-left: -20px;
        padding-left: 35px;
      }

      .panel-body {
        margin-left: -15px;
        li {
          padding-left: 30px;

          :last-child {
            border-bottom: 1px solid #e7e7e7;
          }

        }

      }

    }
  }

}

/* small screen */
@media (max-width: 768px) {
  .side-menu {
    display: none;
  }
}


</style>
