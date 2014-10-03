define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'pathway/modalViews/detailEditor',
    'text!templates/pathway/RuleWizard.html'

], function ($, _, Backbone, detailEditor, wizardTemplate) {

    var ruleWizard = Backbone.View.extend({
         el: '#modal-target',

        initialize: function(params){
            this.triggerNode = params.triggerNode
            this.template = _.template(wizardTemplate)
            this.$el.html(this.template())
                            var that = this

            $('#createRuleButton').on('click', function(){
                $("#detail-modal").modal('hide');
                var detailType = $('#detailTypeField').val()
                $('#detail-modal').on('hidden.bs.modal', function () {

                    require(['text!templates/pathway/' + detailType +"_editor.html"], function(template){
                        console.log("tnod", that.triggerNode)

                        var curEditor = new detailEditor({template: _.template(template), model: new Backbone.Model(), newDetail: true, el:$('#modal-target'), triggerNode: that.triggerNode, type: detailType})
                        curEditor.render()
                    })

                })

            })
            $("#detail-modal").modal({'show':'true'});
        }


    });
    return ruleWizard
});