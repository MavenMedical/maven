
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone

    'models/ruleModel',

    'modalViews/'+'detailEditor',
    'text!templates/detailPanel/detailSection.html'
], function ($, _, Backbone, curRule, DetailEditor, detailSectionTemplate) {

    var DetailGroup = Backbone.View.extend({

        template: _.template(detailSectionTemplate),

        initialize: function(params){
          this.lineTemplate = params.lineTemplate;

          this.list= params.list;
          this.type = params.type;
          this.el = params.el;
          this.list.on('add', this.render, this)
          this.list.on('remove', this.render, this)
          curRule.on('sync', this.render, this)

        },
        render: function(){
            console.log("rendering")
            this.$el.html("");
            var type = this.type;
            var panel = this
            var detailLine = Backbone.View.extend({

                initialize: function(params){
                    console.log(params)
                    this.el = params.el
                    this.$el.html(params.text)

                    this.detail = params.detail
                    console.log(curRule)
                    if (curRule.get('conflicts')){
                        _.each(curRule.get('conflicts').models, function(cur){
                                console.log(cur.get('0'), this.detail.get('did'))
                                if (cur.get('0') == this.detail.get('did') || cur.get('1') == this.detail.get('did')){
                                    this.$el.addClass("conflict")
                                }
                        }, this)

                    }
                    var that = this
                    $('.detail-item', this.$el)[0].onclick = function(){
                         require(['text!/templates/individualDetails/' + type + '_editor.html'],
                                 function(curTemplate) {

                                    var curView = new DetailEditor({model: that.detail, el:$('#modal-target'), template:_.template(curTemplate), type: type});
                                     $("#detail-modal").modal('show')
                                 }
                              );
                    }
                    $('.remove-detail', this.$el)[0].onclick = function(){
                        curRule.get(type).remove(that.detail);
                        curRule.needsSave = true;
                        curRule.trigger("needsSave")

                    }

                }
            })
            this.list.each(function(cur) {


                cur.off('change')
                cur.on('change', this.render, this)
                this.$el.append("<div class = 'item-holder'></div>")
                new detailLine({el: $('.item-holder', this.$el).last(), text: this.lineTemplate(cur.attributes), detail: cur})




            } , this);

            return this;

        }

    });

    return DetailGroup;

});
