/*A Backbone View which actually displays and sets the rule's titles and descriptions
  IT used to handle evidence which is now handled by sources, it should be renamed


 */
define ([
     'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'models/ruleModel',
    'text!/templates/evidenceEditor.html'
    ],


    function($, _, Backbone, curRule, editorTemplate){

        var EvidenceEditor = Backbone.View.extend({
           template: _.template(editorTemplate),
           initialize: function(){

            this.$el.html(this.template());
               //dont show this el by default
               this.$el.hide();

               //if the contents of the evidence is changed, rerender this
               curRule.on('change:evidence', this.render, this);
               //if the current rule is chagned, handle the rule load
               curRule.on('change:id', this.handleRuleLoad, this);
               //if the rule is cleared stop showing this until it is requested to render again
               curRule.on('cleared', function(){
                    this.$el.hide()

               }, this)
               //when text is entered and then the mouse leaves the editor, update the data structure
              $('.evidence-editor-text').on('blur', function(){
                  var fields = $(".evidence-editor-text", this.$el);
                  for (var c=0;c<fields.length;c++){
                      curRule.get('evidence').set(fields[c].name, fields[c].value)

                  }
                  //the data structure of thr
                  curRule.needsSave = true;
                 curRule.trigger("needsSave")
              });
              curRule.needsSave = true;
              curRule.trigger("needsSave")
           },
           render: function(){
               //if it gets rendered, then show it
               this.$el.show()
               //create the jquery selector to find all 'evidence' fields which currently include
               //short title, short description, long title, and long description
               var fields = $(".evidence-editor-text", this.$el);
               //if there is no 'evidence' on the rule set the default evidence
               if (!curRule.get('evidence')){
                   curRule.set({'evidence': new Backbone.Model({'short-title': "", 'short-description': "", 'long-title': "", 'long-description': ""})}, {silent:true});

                 }
               //should be moved to the beginning of the sources view, but if there are no sources
               //set the default sources
               if (!curRule.get('sources')){
                   curRule.set('sources', new Backbone.Collection())
               }
               //for all of the fields add their current value mapped to their name to the evidence attribute in the
               //cur rule data structure
               for (var c=0;c<fields.length;c++){
                   fields[c].value = curRule.get('evidence').get(fields[c].name);
               }

           },
            // if a rule is loaded, if its a legitiame rule (with an id) show this el and render it, otherwise hide it
           handleRuleLoad: function(){

               if (curRule.get('id')){
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