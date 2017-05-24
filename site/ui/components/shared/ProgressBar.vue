<template>

  <div class="p-bar" v-if="progress.active">
    <div class="middle-box">
      <h4>Uploading...</h4>
      <div class="progress">
        <div class="progress-bar progress-bar-striped active" role="progressbar" :style="'width:' + progress.percent + '%'"></div>
      </div>
    </div>
  </div>
</template>


<script>
export default {
  name: 'progress-bar',
  props: ['progress'],
  data () {
    return {

    }
  },
  created () {

  },
  methods: {

  }
}
</script>

<style lang="scss" scoped>
.p-bar {
  position: fixed;
  top: 0;
  left: 0;
  height: 100vh;
  width: 100%;
  z-index: 8888;
  background-color: rgba(80, 80, 80, 0.8);
  text-align: center;
  color: #eee;
  
  .middle-box {
    margin-left: 10%;
    margin-top: 50vh;
    width: 80%;
  }
}
</style>
