
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone

    'models/ruleModel',

    'text!templates/detailPanel/detailSection.html'
], function ($, _, Backbone, curRule, detailSectionTemplate) {

    var DetailGroup = Backbone.View.extend({

        template: _.template(detailSectionTemplate),

        initialize: function(params){
          this.lineTemplate = params.lineTemplate;

          this.list= params.list;
          this.type = params.type;
          this.el = params.el;
          this.list.on('add', this.render, this)
          this.list.on('remove', this.render, this)


        },
        render: function(){
            console.log(this.list);

            this.$el.html("");
            var type = this.type;


            this.list.each(function(cur) {

                this.$el.append(this.lineTemplate(cur.attributes))
                $('.detail-item', this.$el).last()[0].onclick = function(){

                     require(['modalViews/'+type+'_editor.js'],
		                     function(modalView) {
		    	                var curView = new modalView({model: cur, el:$('#modal-target')});
		                     }
                          );
                }
                $('.remove-detail', this.$el).last()[0].onclick = function(){
                    curRule.get(type).remove(cur);
                    curRule.save();


                }


            } , this);

            return this;

        }

    });

    return DetailGroup;

});
