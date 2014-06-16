
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'models/ruleModel'


], function ($, _, Backbone,  curRule) {

    var DetailEditor = Backbone.View.extend({


        initialize: function(param){
            console.log(param);
            this.model = param.model;
            this.newDetail = param.newDetail
            this.$el = param.el;
            this.template = param.template
            this.type = param.type;
            this.$el.html(this.template());
            if (!this.newDetail){
                this.fillTemplate();
            }
            this.$el.show();


            var panel = this;
            $('.confirm-detail-button', this.$el)[0].onclick = function(){
                var inputs = $('.detail-input');
                console.log(inputs);
                for (var i=0;i<inputs.length;i++){
                    var cur = inputs[i];
                    panel.model.set(cur.name, cur.value);

                }

                if (panel.newDetail){
                    if (curRule.get(panel.type)){
                        curRule.get(panel.type).add(panel.model);
                    } else {
                        var model = new Backbone.Collection();
                        model.add(panel.model);
                        curRule.set(panel.type, model);

                    }
                    console.log(curRule)
                    curRule.save()
                }
               $('#detail-modal').modal('hide');


            }

            $('.cancel-edit-button', this.$el)[0].onclick = function(){

                $('#detail-modal').modal('hide');

            }
        },
        fillTemplate: function(){
            var inputs = $('.detail-input');
             for (var i=0;i<inputs.length;i++){
                    var cur = inputs[i];
                    console.log(cur);
                    cur.value =this.model.get(cur.name);

                }
        }






    });


    return DetailEditor;

});
