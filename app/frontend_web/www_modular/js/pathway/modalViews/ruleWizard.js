define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'text!templates/pathway/RuleWizard.html'

], function ($, _, Backbone, wizardTemplate) {

    var ruleWizard = Backbone.View.extend({
        initialize: function(params){
            this.$el = params.el
            this.triggerNode = params.triggerNode
            this.template = _.template(wizardTemplate)

        }

    });
    return ruleWizard
});