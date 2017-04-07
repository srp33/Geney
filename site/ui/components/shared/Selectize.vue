<template>

  <div class="selectize">
    <select :placeholder="placeholder" autofocus="false"></select>
  </div>
</template>

<script>
import $ from 'jquery'
import 'selectize'

export default {
  name: 'selectize',
  props: ['options', 'value', 'placeholder', 'settings'],
  data () {
    return {
      selectize: null
    }
  },
  mounted () {
    var component = this
    this.selectize = $(this.$el).find('select').selectize({
      maxItems: this.settings.maxItems || null,
      valueField: this.settings.valueField || 'name',
      labelField: this.settings.labelField || 'name',
      searchField: this.settings.searchField || 'name',
      options: this.options,
      create: false,
      items: this.value,
      maxOptions: this.settings.maxOptions || 500,
      onChange (values) {
        component.$emit('updated', values)
        var div = $(component.$el).find('.selectize-input')
        div.scrollTop($(div)[0].scrollHeight)
      }
    })[0].selectize
    // force single input to show selected value on initialization
    if (this.settings.maxItems === 1) {
      this.selectize.addItem(this.value, true)
    }
  },
  watch: {
    'options' (to, from) {
      this.selectize.clear()
      this.selectize.clearOptions()
      this.selectize.addOption(this.options)
      if (this.value) {
        for (var val of this.value) {
          this.selectize.addItem(val, true)
        }
      }
      this.selectize.refreshItems()
      this.selectize.refreshOptions()
      this.selectize.blur()
      this.selectize.close()
    }
  }
}
</script>

<style lang="scss">
h1, h2 {
  font-weight: normal;
}
.selectize {
  text-align: left;
}


.selectize-input {
  max-height: 83px !important;
  overflow-y: scroll !important;
}

</style>
