
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'pathway/models/nodeModel',
    'text!templates/pathway/NewProtocolModal.html',


], function ($, _, Backbone, NodeModel, nodeTemplate) {

    var savingModal = Backbone.View.extend({
        template: _.template(nodeTemplate),
        el: $("#modal-target"),
        initialize: function(parent){
            this.$el.html(this.template())
            var that = this
            this.parent = parent
                $("#detail-modal").modal({'show':'true'});
                $("#addNodeButton", this.$el).on("click", function(){
                    var summary = $('#newProtocolSummary', this.$el).val()
                    var recommendation = $('#newProtocolRecommendation', this.$el).val()
                    var note = $('#newProtocolNote', this.$el).val()

                    that.parent.set('protocol', new Backbone.Model({summary: summary, recommendation: recommendation, note: note}))
                    $('#detail-modal').modal('hide')

            })

        }

    });
    return savingModal
});