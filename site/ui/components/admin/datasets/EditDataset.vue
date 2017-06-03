<template>

  <div class="add-datasets">

    <div class="col-12">
      <h3>Edit Dataset</h3>
    </div>

    <div class="form-group col-sm-8" :class="{'has-danger': errors.has('Title')}">
      <label for="title" class="form-control-label">Title</label>
      <input type="text" name="Title" id="title" v-model="title" class="form-control"
            v-validate="'required'" :class="{'form-control-danger': errors.has('Title')}">
      <span v-if="errors.has('Title')" class="form-control-feedback">{{ errors.first('Title') }}</span>
    </div>

    <div class="form-group col-sm-12">
      <label for="desc">Description: <small>No HTML please!</small></label>
      <textarea id="mde"></textarea>
    </div>

    <div class="col-12" style="margin-bottom:25px;">
      <button type="button" class="btn btn-primary" @click="saveDataset">Submit</button>
    </div>

    <progress-bar :progress="progressData"></progress-bar>
  </div>
</template>


<script>
import SimpleMDE from 'simplemde'
import ProgressBar from '../../shared/ProgressBar'
import { mapState } from 'vuex'
import router from '../../../router'

export default {
  name: 'edit_datasets',
  components: {
    ProgressBar
  },
  data () {
    return {
      mde: null,
      title: '',
      progressData: {
        active: false,
        percent: 0
      }
    }
  },
  mounted () {
    // console.log()
    if (this.$store.state.dataset.name) {
      this.$set(this, 'title', this.$store.state.dataset.name)
    }
    this.mde = new SimpleMDE({
      element: document.getElementById('mde'),
      autoDownloadFontAwesome: false,
      spellChecker: false,
      hideIcons: ['fullscreen', 'side-by-side'],
      shortcuts: {
        toggleFullScreen: null,
        toggleSideBySide: null
      },
      initialValue: this.$store.state.dataset.description || ''
    })
  },
  computed: mapState({
    // arrow functions can make the code very succinct!
    dataset: (state) => state.dataset
  }),
  methods: {
    stripTags (str) {
      return str.replace(/<[^>]*>/g, '')
    },
    saveDataset () {
      let description = this.stripTags(this.mde.value())
      this.mde.value(description)
      this.$validator.validateAll().then(() => {
        this.$http.post('/api/' + this.dataset.id + '/update', {
          title: this.title,
          description: description
        }).then(
        (response) => {
          if (response.body === true) {
            this.$store.commit('addAlert', {
              variant: 'success',
              message: 'Dataset ' + this.dataset.id + ' updated successfully.',
              show: 3
            })
            router.push('/admin/datasets')
          } else {
            this.$store.commit('addAlert', {
              variant: 'warning',
              message: 'Could not save dataset. Please refresh and try again.',
              show: 3
            })
          }
          this.$store.dispatch('getDatasets')
        },
        (errResponse) => {
          this.$store.commit('addAlert', {
            variant: 'danger',
            message: 'Server error. Could not save dataset.',
            show: 3
          })
          console.error(errResponse)
        })
      }).catch(() => {})// do nothing if validation fails
    }
  },
  watch: {
    // we set the watcher here because the datsset isn't always ready when the page loads
    // this makes sure the mde gets the value it needs
    '$store.state.dataset' () {
      this.$set(this, 'title', this.$store.state.dataset.name)
      this.mde.value(this.$store.state.dataset.description)
    }
  }
}
</script>

<style lang="scss">
.CodeMirror {
	min-height: 150px !important;
  .CodeMirror-scroll {
    min-height: 150px !important;
	  max-height: 150px !important;
  }
}
</style>
