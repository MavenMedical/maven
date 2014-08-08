/**
 * Created by Asmaa Aljuhani on 8/7/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'modalViews/newPathway',
    'text!templates/actionList.html'
], function ($, _, Backbone, NewPathway, actionListTemplate) {

    var ActionList = Backbone.View.extend({
        template: _.template(actionListTemplate),
        events: {
            'click #newpath-button': 'handle_newPath'
        },
        initialize: function () {
            this.render();
        },
        render: function () {
            this.$el.html(this.template());
        },
        handle_newPath: function () {
            new NewPathway({el: '#createNewPath-modal'});

            $("#createNewPath-modal").modal({'show': 'true'});

        }
    });
    return ActionList;
});
