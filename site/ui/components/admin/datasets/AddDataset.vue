<template>

  <div class="add-datasets">

    <div class="col-12">
      <h3>Add Dataset</h3>
    </div>

    <div class="form-group col-sm-8" :class="{'has-danger': errors.has('Title')}">
      <label for="title" class="form-control-label">Title</label>
      <input type="text" name="Title" id="title" v-model="title" class="form-control"
            v-validate="'required'" @blur="setId" :class="{'form-control-danger': errors.has('Title')}">
      <span v-if="errors.has('Title')" class="form-control-feedback">{{ errors.first('Title') }}</span>
    </div>

    <div class="form-group col-sm-4" :class="{'has-danger': errors.has('Unique ID')}">
      <label for="id" class="form-control-label">Unique ID</label>
      <input type="text" name="Unique ID" id="id" v-model="id" class="form-control"
            v-validate="'required|idUsed'" tabindex="-1" :class="{'form-control-danger': errors.has('Unique ID')}">
      <span v-if="errors.has('Unique ID')" class="form-control-feedback">{{ errors.first('Unique ID') }}</span>
    </div>

    <div class="form-group col-sm-12">
      <label for="desc">Description: <small>No HTML please!</small></label>
      <textarea id="mde"></textarea>
    </div>

    <div class="form-group col-sm-12" :class="{'has-danger': errors.has('file')}">
      <label for="file" class="form-control-label">
        File Upload
        <!--<b-tooltip content="Comma Separated Values files only.">
          <i class="fa fa-question-circle-o" aria-hidden="true"></i>
        </b-tooltip>-->
      </label>
      <br>
      <!--<b-form-file id="file" name="file" v-model="file" accept="text/csv" v-validate="'required|ext:csv'"></b-form-file>-->
      <input type="file" name="file" id="file" @change="updateFile" accept="text/csv" v-validate="'required|ext:csv'">
      <br>
      <span v-if="errors.has('file')" class="form-control-feedback">{{ errors.first('file') }}</span>
    </div>

    <div class="form-group col-sm-4" :class="{'has-danger': errors.has('columns')}">
      <label for="cols" class="form-control-label"># of MetaData Columns</label>
      <input type="number" name="columns" id="cols" v-model="metaCols" class="form-control" min="1" v-validate="'required|numeric|min_value:1'">
      <span v-if="errors.has('columns')" class="form-control-feedback">{{ errors.first('columns') }}</span>
    </div>

    <div class="col-12" style="margin-bottom:25px;">
      <button type="button" class="btn btn-primary" @click="addDataset">Submit</button>
    </div>

    <progress-bar :progress="progressData"></progress-bar>
  </div>
</template>


<script>
import SimpleMDE from 'simplemde'
import ProgressBar from '../../shared/ProgressBar'
import router from '../../../router'

export default {
  name: 'add_datasets',
  components: {
    ProgressBar
  },
  data () {
    return {
      mde: null,
      title: '',
      id: '',
      file: null,
      metaCols: null,
      progressData: {
        active: false,
        percent: 0
      }
    }
  },
  mounted () {
    this.mde = new SimpleMDE({
      element: document.getElementById('mde'),
      autoDownloadFontAwesome: false,
      spellChecker: false,
      hideIcons: ['fullscreen', 'side-by-side'],
      shortcuts: {
        toggleFullScreen: null,
        toggleSideBySide: null
      }
    })
  },
  computed: {
  },
  methods: {
    setId () {
      if (this.title.length) {
        this.id = this.title.toLowerCase().replace(/\s/g, '')
      }
    },
    updateFile (event) {
      let files = event.target.files
      if (files.length === 1) {
        this.file = files[0]
      } else {
        this.file = null
      }
    },
    stripTags (str) {
      return str.replace(/<[^>]*>/g, '')
    },
    addDataset () {
      let that = this
      let description = this.stripTags(this.mde.value())
      this.mde.value(description)
      this.$validator.validateAll().then(valid => {
        if (valid) {
          let formData = new FormData()
          formData.append('id', that.id)
          formData.append('title', that.title)
          formData.append('description', description)
          formData.append('metaCols', that.metaCols)
          formData.append('file', that.file)
          that.progressData.active = true
          that.$http.put('/api/datasets', formData, {
            progress (e) {
              that.progressData.percent = (e.loaded / e.total) * 100
            }
          }).then(response => {
            that.progressData.active = false
            that.progressData.percent = 0
            this.$store.commit('addAlert', {
              variant: 'success',
              message: 'Added dataset! You will recieve an email when processing is complete.',
              show: 3
            })
            setTimeout(() => {
              router.push('/admin/datasets')
            }, 250)
          }).catch(response => {
            that.progressData.active = false
            that.progressData.percent = 0
            console.log(response)
          })
        }
      })
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
