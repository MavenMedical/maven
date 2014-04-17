/**
 * Created by devel on 3/27/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'currentContext',
    'text!templates/widget/evidence.html'
], function ($, _, Backbone, currentContext, evidenceTemplate) {

    var Evidence = Backbone.View.extend({
        el: '.page',
        template: _.template(evidenceTemplate),
        initialize: function () {
            console.log("evidence ini test2");
            _.bindAll(this, 'render');
            this.render();
        },
        render: function () {
            this.$el.append(this.template({alert: currentContext.get('alert')}));
             return this;
        }
    });
    return Evidence;
});
