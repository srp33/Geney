<template>
  <div>
    <b-navbar toggleable="md" type="inverse" variant="success">

    <div class="nav-item center-nav">
        <!-- <b-breadcrumb :items="breadcrumbs"/> -->
        <ol class="breadcrumb">
          <li class="breadcrumb-item" :class="{'active': breadcrumb.active}" v-for="(breadcrumb, index) in breadcrumbs" :key="index">
            <router-link :to="breadcrumb.link" v-if="!breadcrumb.active">{{breadcrumb.text}}</router-link>
            <span v-if="breadcrumb.active">{{breadcrumb.text}}</span>
          </li>
        </ol>
      </div>

      <b-navbar-brand class="above-breadcrumbs" to="/">
        Geney
      </b-navbar-brand>

        <!-- Commenting out the login section for now...  -->
        <!-- <b-nav is-nav-bar class="ml-auto" right-alignment>
          <div class="above-breadcrumbs">
            <b-nav-item-dropdown v-if="authenticated" right-alignment right :text="name">
              <b-dropdown-item to="/admin">Admin</b-dropdown-item>
              <b-dropdown-item @click="logout">Logout</b-dropdown-item>
            </b-nav-item-dropdown>

            <b-nav-item v-else to="/login">Login</b-nav-item>
          </div>
        </b-nav> -->



    </b-navbar>


    <b-navbar v-if="admin" toggleable class="no-z-index" style="background-color: #dedede;">

        <b-nav is-nav-bar class="mx-auto">

          <b-nav-item v-for="privilege in privileges" :key="privilege" class="privilege" :to="'/admin/' + privilege">{{privilege | capitalize}}</b-nav-item>

        </b-nav>

    </b-navbar>

    <div class="alerts-container">
      <transition-group
        name="custom-classes-transition"
        enter-active-class="animated slideInRight">
        <div v-for="(alert, index) in alerts" :key="index">
          <b-alert
            :variant="alert.variant"
            dismissible
            :show="alert.show">
            {{ alert.message }}
          </b-alert>
        </div>
      </transition-group>
    </div>

  </div>
</template>



<script>
import router from '../../router';

export default {
  name: 'navbar',
  data () {
    return { };
  },
  computed: {
    breadcrumbs () {
      const crumbs = [];
      if (!this.admin) {
        crumbs.push({link: '/', text: 'Select Dataset', route: 'Home'});
        if (this.$store.state.dataset.id) {
          let datasetPath = '/dataset/' + this.$store.state.dataset.id + '/';
          crumbs.push({link: datasetPath, text: this.$store.state.dataset.title, route: 'Description'});
          if (this.$route.path.indexOf('filter') >= 0) {
            crumbs.push({link: datasetPath + 'filter', text: 'Filter', route: 'Filter'});
          }
          if (this.$route.path.indexOf('download') >= 0) {
            crumbs.push({link: datasetPath + 'download', text: 'Download', route: 'Download'});
          }
        }
      }
      if (crumbs.length) {
        crumbs[crumbs.length - 1].active = true;
      }
      return crumbs;
    },
    currentRoute () {
      return this.$route.name;
    },
    authenticated () {
      return this.$store.state.user && this.$store.state.user.username;
    },
    name () {
      const user = this.$store.state.user;
      if (user) {
        return user.firstname + ' ' + user.lastname;
      }
      return null;
    },
    admin () {
      for (let match of this.$route.matched) {
        if (match.name === 'Admin') {
          return true;
        }
      }
      return false;
    },
    alerts () {
      return this.$store.state.alerts;
    },
    privileges () {
      if (this.authenticated) {
        return this.$store.state.user.privileges;
      }
      return [];
    },
  },
  methods: {
    logout () {
      this.$store.dispatch('logout');
      if (this.admin) {
        router.push('/');
      }
    },
    authorized (requiredPrivileges) {
      if (this.authenticated) {
        for (let privilege of requiredPrivileges) {
          if (this.$store.state.user.privileges.indexOf(privilege) === -1) {
            return false;
          }
        }
        return true;
      }
      return false;
    },
  },
};
</script>

<style lang="scss" scoped>
.navbar {
  z-index: 1020;
}
.above-breadcrumbs {
  z-index:80;
}
.nav, .navbar {
  // display: flex;
  flex-direction: row;
}
.navbar-brand {
  text-align: left;
  display: inline;
  color: white;
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
  display: inline;
}
div.nav-item.center-nav {
  position: absolute;
  text-align: center;
  left: 0px;
  width: 100%;
  margin: 0;
  height: 40px;

  ol.breadcrumb {
    text-align: left;
    display: inline-block;
    padding: 0.5em 0.5em;
    margin-bottom: 0px;
    background-color: transparent;
    li.breadcrumb-item {
      display: inline-block;
      &::before {
        color: white;
      }
      a {
        color: white;
        text-decoration: none;
      }
      &.active {
        color: white;
        font-weight: bold;

      }
    }
  }
}
</style>
