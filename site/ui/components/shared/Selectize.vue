<template>

  <div class="selectize">
    <select :placeholder="placeholder" autofocus="false"></select>

      <span class="error-message" v-if="errorMessage">
        <span v-if="dirty && invalid">{{errorMessage}}</span>
        &nbsp; <!-- just to keep it from expanding and shrinking when the message appears and disappears -->
      </span>
  </div>
</template>

<script>
import $ from 'jquery';
import 'selectize';

export default {
  name: 'selectize',
  props: ['options', 'value', 'placeholder', 'settings', 'errorMessage'],
  data () {
    return {
      selectize: null,
      dirty: false,
      invalid: false,
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
      this.dirty = true;
      $(e.currentTarget).addClass('dirty');
      this.setValidState(this.value);
    });

    // force single input to show selected value on initialization
    if (settings.maxItems === 1) {
      this.selectize.addItem(this.value, true);
    }

    this.update(this.value);
    this.selectize.refreshItems();
  },
  methods: {
    // this function is called whenever the user changes the value of the selectize
    update (values) {
      this.$emit('updated', values);
      const div = $(this.$el).find('.selectize-input');
      div.scrollTop($(div)[0].scrollHeight);
      this.setValidState(values);
      // if (this.settings.clearValue) {
      //   this.selectize.clear();
      // }
    },
    setValidState (values) {
      if (this.settings.required) {
        const div = $(this.$el).find('.selectize-input');
        if (!this.valid(values)) {
          div.parent().addClass('has-error');
          this.invalid = true;
        } else {
          div.parent().removeClass('has-error');
          this.invalid = false;
        }
      }
    },
    valid (value) {
      if (this.settings.maxItems === 1) {
        return !!value;
      } else {
        if (!Array.isArray(value) || value.length === 0) {
          return false;
        }
        return true;
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

<style lang="scss" scoped>
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
.error-message {
  position: relative;
  left: 12px;
  top: -4px;
  color: #d9534f;
  font-size: 14px;
}
</style>
