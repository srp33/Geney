<template>

  <div class="admin top">
    <router-view></router-view>
  </div>
</template>


<script>
import router from '../../router';

export default {
  name: 'admin',
  data () {
    return {
    };
  },
  created () {
    this.$store.dispatch('getUser').then(user => {
      if (user === null || user.username === undefined) {
        router.push('/login');
      } else {
        // check if the user has ANY privileges
        if (user.privileges.length) {
          // check if we only matched the /admin route
          if (this.$route.matched.length === 1) {
            let route = user.privileges[0];
            router.replace('/admin/' + route);
          } else {
            let path = this.$route.path.split('/');
            let requiredPrivilege = null;
            if (path.length >= 3) {
              requiredPrivilege = path[2];
            }
            if (requiredPrivilege && user.privileges.indexOf(requiredPrivilege) === -1) {
              this.reject();
            }
          }
        } else {
          this.reject();
        }
      }
    });
  },
  watch: {
    $route (to, from) {
      let path = to.path.split('/');
      let requiredPrivilege = null;
      if (path.length >= 3) {
        requiredPrivilege = path[2];
      }
      if (requiredPrivilege) {
        this.$store.dispatch('getUser').then(user => {
          if (user === null || user.username === undefined) {
            router.push('/login');
          } else {
            if (user.privileges.indexOf(requiredPrivilege) === -1) {
              this.reject();
            }
          }
        });
      }
    }
  },
  methods: {
    reject () {
      this.$store.commit('addAlert', {
        variant: 'danger',
        message: 'You have no permissions!',
        show: 3
      });
      router.replace('/');
    }
  }
};
</script>

<style lang="scss" scoped>

.admin {
  text-align: left;
  padding-left: 25px;
  padding-right: 25px;
}

</style>
