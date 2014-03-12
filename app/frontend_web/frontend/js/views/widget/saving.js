/**
 * Created by Asmaa Aljuhani on 3/11/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'text!templates/widget/saving.html'
], function ($, _, Backbone, savingTemplate) {

    var Saving = Backbone.View.extend({
        el: $('.saving'),
        render: function () {
            var template = _.template(savingTemplate, {});
            $('.saving').append(template);
        }
    });
    return Saving;
});
