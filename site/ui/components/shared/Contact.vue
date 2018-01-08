<template>
  <div class="contact">
      <h1>Contact Us</h1>
      <p class="mt-5">&emsp;Geney is an open source project managed by the Stephen Piccolo Lab at Brigham Young University
          in Provo, UT. If you have any questions or issues with Geney, please let us know by logging an
          issue on the project's
          <a href="https://github.com/srp33/Geney/issues">Github repository</a>.
          If you would like to contact us directly, Dr. Piccolo's contact information is found
          <a href="http://piccolo.byu.edu/Contact">here</a>.
      </p>

      <router-link to="/" class="btn btn-primary btn-lg mt-5">
      Go Home
      <i class="fa fa-home" aria-hidden="true"></i>
    </router-link>
          
  </div>
</template>

<script>
export default {
  name: 'Contact',
  data () {
    return {};
  },
  created () {
  },
  computed: {
  },
  methods: {
  },
};
</script>

<style lang="scss" scoped>
.contact {
    margin: 20px 40px 20px 40px;
    h1 {
        font-size: 7em;
        // font-weight: bold;
    }
    p {
        font-size: 2em;
        text-align: left;
    }
}
</style>
