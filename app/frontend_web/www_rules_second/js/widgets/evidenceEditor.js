
define ([
     'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'models/ruleModel',
    'internalViews/SourceManager',
    'text!/templates/evidenceEditor.html'
    ],


    function($, _, Backbone, curRule, SourceManager, editorTemplate){

        var EvidenceEditor = Backbone.View.extend({
           template: _.template(editorTemplate),
           initialize: function(){

            this.$el.html(this.template());
               this.$el.hide();
              curRule.on('change:evidence', this.render, this);
              curRule.on('change:id', this.handleRuleLoad, this);
              $('.evidence-editor-text').on('blur', function(){
                  var fields = $(".evidence-editor-text", this.$el);
                  for (var c=0;c<fields.length;c++){
                      curRule.get('evidence').set(fields[c].name, fields[c].value)

                  }
                  curRule.save();
              });
           },
           render: function(){
               var fields = $(".evidence-editor-text", this.$el);
               if (!curRule.get('evidence')){
                   curRule.set({'evidence': new Backbone.Model({'short-title': "", 'short-description': "", 'long-title': "", 'long-description': ""})}, {silent:true});

                 }
               if (!curRule.get('sources')){
                   curRule.set('sources', new Backbone.Collection())
               }
               for (var c=0;c<fields.length;c++){
                   fields[c].value = curRule.get('evidence').get(fields[c].name);
               }
               console.log($('#source-manager'))
               this.sourceView = new SourceManager({el: $('#source-manager', this.$el)})
               console.log(this.sourceView)
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