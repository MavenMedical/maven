/**
 * Created by devel on 3/27/14.
 */


define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'text!templates/widget/evidence.html'
], function ($, _, Backbone, evidenceTemplate) {

    var Evidence = Backbone.View.extend({
        el: '.page',
        template: _.template(evidenceTemplate),
        initialize: function () {
            _.bindAll(this, 'render');
            this.render();
        },
        render: function () {
            this.$el.append(this.template);
            $('#Modal').modal({
                keyboard: false
            });
        }
    });
    return Evidence;
});
