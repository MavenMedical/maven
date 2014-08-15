/*
    a very simple view which is rendered in the modal while the rule is saving, informs the user that saving is occuring
    and locks them from acting before it completes

 */
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
        //always render in the modal target
        el: $("#modal-target"),
        initialize: function(){
            this.$el.html(this.template())
            //the modal cant be exited through normal means
            $("#detail-modal").modal({'show':'true', 'backdrop':'static',keyboard:false});

        }

    });
    return savingModal
});