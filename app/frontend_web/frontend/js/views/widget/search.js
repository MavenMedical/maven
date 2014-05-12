/**
 * Created by Asmaa Aljuhani on 4/10/14.
 */
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'currentContext',
    'text!templates/templatesA/widget/search.html'
], function ($, _, Backbone, currentContext, searchTemplate) {

    var Search = Backbone.View.extend({
        el: '.search',
        template: _.template(searchTemplate),
        initialize: function () {
            this.render();
        },
        render: function () {
            this.$el.html(this.template);
            return this;
        }
    });
    return Search;
});
