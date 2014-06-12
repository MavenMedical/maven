
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'models/ruleModel',


    'text!templates/individualDetails/pl_dx_editor.html'
], function ($, _, Backbone,  curRule, dxDetail) {

    var dxPrbListEditor = Backbone.View.extend({
        template: _.template(dxDetail),

        initialize: function(param){

            this.model = param.model;
            this.newDetail = param.newDetail
            this.$el = param.el;
            this.$el.html(this.template(this.model.toJSON()));
            this.$el.show();

            console.log($('.confirm-detail-button', this.$el))
            var panel = this;
            $('.confirm-detail-button', this.$el)[0].onclick = function(){
                console.log($('.neg-select option', this.$el)[1].selected)
                var negVal;
                if ($('.neg-select option', this.$el)[1].selected){
                    negVal = "true";
                } else {
                    negVal = "false"
                }
                panel.model.set({
                    code: $('.snomed', this.$el).val(),
                    negative: negVal
                })
                if (panel.newDetail){
                    if (curRule.get('pl_dx')){
                        curRule.get('pl_dx').add(panel.model);
                        curRule.save();
                    } else {
                        var c = new Backbone.Collection();
                        c.add(panel.model);
                        curRule.set('pl_dx', c);
                    }

                }
                panel.$el.hide();
            }
        }
    });

    return dxPrbListEditor;

});
