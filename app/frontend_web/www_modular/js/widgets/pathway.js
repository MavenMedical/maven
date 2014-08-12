/**
 * Created by Asmaa Aljuhani on 8/8/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'jsplumb',
    'globalmodels/contextModel'
], function ($, _, Backbone, jsPlumb, contextModel) {
    var Pathway = Backbone.View.extend({
        initialize: function (arg) {
            this.template = _.template(arg.template);
            console.log('pathway ini');
            this.$el.html(this.template());


            this.render();
        },
        events: {

        },
        render: function () {
            /*
             var j = jsPlumb.getInstance({
             container:"foo"
             });

             jsPlumb.connect({ source:someDiv, target:someOtherDiv });

             jsPlumb.addEndpoint(someDiv, { endpoint options });

             //dragging
             myInstanceOfJsPlumb.draggable($(".someClass"));
             jsPlumb.draggable($("someSelector"), {
             containment:"parent"
             });

             */
            //jsPlumb.default.container('#pathway-container');
            jsPlumb.setContainer('#pathway-container');

        }
    });
    return Pathway;
});