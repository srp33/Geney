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
    this.update = this.update.bind(this);
    let settings = this.settings || {};
    const selectizeOps = {
      maxItems: settings.maxItems || null,
      valueField: settings.valueField || 'name',
      labelField: settings.labelField || 'name',
      searchField: settings.searchField || 'name',
      options: this.options,
      create: false,
      items: this.value,
      maxOptions: settings.maxOptions || 500,
      onChange: this.update,
      render: settings.render || undefined,
      load: settings.load || undefined,
    };

    this.selectize = $(this.$el).find('select').selectize(selectizeOps)[0].selectize;

    // mark the selectize as dirty
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
    'options' (to, from) {
      this.selectize.clear();
      this.selectize.clearOptions();
      this.selectize.addOption(this.options);
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
