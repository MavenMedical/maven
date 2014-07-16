
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone

    'models/ruleModel',

    'text!/templates/savingModal.html',


], function ($, _, Backbone,  curRule, saveTemplate) {

    var savingModal = Backbone.View.extend({
        template: _.template(saveTemplate),
        el: $("#modal-target"),
        initialize: function(){
            this.$el.html(this.template())
            $("#detail-modal").modal({'show':'true', 'backdrop':'static',keyboard:false});

        }

    });
    return savingModal
});