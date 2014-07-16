
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

            this.$el.html("");
            var type = this.type;

            this.list.each(function(cur) {
                console.log("outputting detail", cur)
                this.$el.append(this.lineTemplate(cur.attributes))

                $('.detail-item', this.$el).last()[0].onclick = function(){
                     require(['text!/templates/individualDetails/' + type + '_editor.html'],
		                     function(curTemplate) {
		    	                var curView = new DetailEditor({model: cur, el:$('#modal-target'), template:_.template(curTemplate), type: type});
                                 $("#detail-modal").modal('show')
		                     }
                          );
                }
                $('.remove-detail', this.$el).last()[0].onclick = function(){
                    curRule.get(type).remove(cur);
                    curRule.needsSave = true;
                    curRule.trigger("needsSave")

                }


            } , this);

            return this;

        }

    });

    return DetailGroup;

});
