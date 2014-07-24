/**
 * Created by Asmaa Aljuhani on 3/11/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'globalmodels/contextModel', // current patient (if any)
], function ($, _, Backbone, contextModel) {

    var TopBanner = Backbone.View.extend({
        initialize: function (arg) {
            this.template = _.template(arg.template);
            this.update(contextModel);
            contextModel.on('change:display change:page', this.update, this);
        },
        update: function (pat) {
            this.$el.html(this.template(contextModel.attributes));
        },
        events: {
            'click #settings_button': 'handle_settings',
            'click #profile_button' : 'handle_profile'
        },
        handle_profile: function () {
            console.log('profile is clicked');
            $("#profile-modal").modal({'show': 'true'});
        },
        handle_settings: function () {
            $("#settings-modal").modal({'show': 'true'});
        }
    });
    return TopBanner;
});
