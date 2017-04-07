<template>

  <div class="manage-datasets">

    <h1>Manage Datasets</h1>

    <textarea id="mde"></textarea>


  </div>
</template>


<script>
import SimpleMDE from 'simplemde'

export default {
  name: 'manage_datasets',
  data () {
    return {
      mde: null
    }
  },
  mounted () {
    this.mde = new SimpleMDE({
      element: document.getElementById('mde'),
      spellChecker: false,
      hideIcons: ['fullscreen', 'side-by-side'],
      shortcuts: {
        toggleFullScreen: null,
        toggleSideBySide: null
      }
    })
  },
  computed: {
    datasets () {
      return this.$store.state.datasets
    }
  },
  methods: {
  }
}
</script>

<style lang="scss" scoped>
.CodeMirror {
	max-height: 300px;
}
</style>
