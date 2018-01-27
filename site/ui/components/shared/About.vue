<template>
  <div class="about">
      <h1>About Geney</h1>
      <div class="mt-5">
        <p>
            &emsp; Geney is a Web-based tool for querying large genomic datasets. You can filter data based on sample-level 
            annotations, and you can select your specific genes of interest. Currently, Geney focuses mostly on genomic 
            and transcriptomic data, but it is flexible enough to be able to handle other types of data, too.
        </p>
        <p>
            &emsp; This is a working prototype of the project. We are working to add more datasets and new functionality. 
            If there is a publicly available dataset that you would like to be able to query with this tool, 
            please <a href="../contact">let us know</a>. Please also let us know if you have feedback!
        </p>
      </div>
      <router-link to="/" class="btn btn-primary btn-lg mt-5">
      Go Home
      <i class="fa fa-home" aria-hidden="true"></i>
    </router-link>
  </div>
</template>

<script>
export default {
  name: 'About',
  data () {
    return {};
  },
};
</script>

<style lang="scss" scoped>
.about {
    margin: 20px 40px 20px 40px;
    h1 {
        font-size: 7em;
        // font-weight: bold;
    }
    p {
        text-align: left;
        font-size: 2em;
    }
}
</style>


