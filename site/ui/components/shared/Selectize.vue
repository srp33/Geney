<template>

  <div class="selectize">
    <select :placeholder="placeholder" autofocus="false"></select>
  </div>
</template>

<script>
import $ from 'jquery';
import 'selectize';

export default {
  name: 'selectize',
  props: ['options', 'value', 'placeholder', 'settings'],
  data () {
    return {
      selectize: null,
      dirty: false,
    };
  },
  mounted () {
    // preserve the scope of the update function using bind
    this.update = this.update.bind(this);
    const settings = this.settings || {};
    let options = this.options || [];
    if ((typeof settings.load) === 'function' && Array.isArray(this.value) && this.value.length > 0) {
      options = this.value.map(item => ({name: item}));
    }
    const selectizeOps = {
      maxItems: settings.maxItems || null,
      valueField: settings.valueField || 'name',
      labelField: settings.labelField || 'name',
      searchField: settings.searchField || 'name',
      options: options,
      create: false,
      items: this.value,
      maxOptions: settings.maxOptions || 500,
      onChange: this.update,
      render: settings.render || undefined,
      load: settings.load || undefined,
      preload: !!settings.load,
    };
    // turn the select in our element into a selectize and save a reference to it
    this.selectize = $(this.$el).find('select').selectize(selectizeOps)[0].selectize;

    // mark the selectize as dirty when it loses focus for the first time
    $(this.$el).find('.selectize-input').one('focusout', (e) => {
      $(e.currentTarget).addClass('dirty');
    });

    // force single input to show selected value on initialization
    if (settings.maxItems === 1) {
      this.selectize.addItem(this.value, true);
    }

    this.update(this.value);
  },
  methods: {
    // this function is called whenever the user changes the value of the selectize
    update (values) {
      this.$emit('updated', values);
      const div = $(this.$el).find('.selectize-input');
      div.scrollTop($(div)[0].scrollHeight);
      if (this.settings.required) {
        if (this.settings.maxItems === 1) {
          if (!values) {
            div.parent().addClass('has-error');
          } else {
            div.parent().removeClass('has-error');
          }
        }
      }
    },
  },
  watch: {
    // update the selectize when the options change
    // this happens when you switch between meta types
    'options' (to, from) {
      this.selectize.clear();
      this.selectize.clearOptions();
      if (Array.isArray(this.options)) {
        this.selectize.addOption(this.options);
      }
      if (this.value) {
        for (let val of this.value) {
          this.selectize.addItem(val, true);
        }
      }
      this.selectize.refreshItems();
      this.selectize.refreshOptions();
      this.selectize.blur();
      this.selectize.close();
    },
  },
};
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
