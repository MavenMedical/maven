
define ([
     'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'models/ruleModel',
    'text!/templates/evidenceEditor.html'],


    function($, _, Backbone, curRule, editorTemplate){

        var EvidenceEditor = Backbone.View.extend({
           template: _.template(editorTemplate),
           initialize: function(){

            this.$el.html(this.template());
               this.$el.hide();
              curRule.on('change:evidence', this.render, this);
              curRule.on('change:id', this.handleRuleLoad, this);
              $('#evidence-area')[0].onblur = function(){
                  console.log($('#evidence-area')[0]);

                  curRule.set('evidence', $('#evidence-area').val());
                  console.log(curRule);
                  curRule.save();
              };

           },
           render: function(){

               console.log(curRule)
               if (!curRule.get('evidence'))
                   curRule.set('evidence', "Enter Evidence Here", {silent:true});
               $('.evidence-editor-text').val(curRule.get('evidence'));


           },
           handleRuleLoad: function(){

               if (curRule.get('id')){
                   this.$el.show();
                   this.render();
               } else {
                   this.$el.hide();
               }


           },


           events: {
               'onblur #evidence-area': 'saveEvidence'


           }


        });
         return EvidenceEditor;



    }
);