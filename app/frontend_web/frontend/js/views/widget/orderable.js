/**
 * Created by Asmaa Aljuhani on 3/11/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'text!templates/widget/orderable.html'
], function ($, _, Backbone, orderableTemplate) {

    var Orderable = Backbone.View.extend({
        el: $('.orderable'),
        initialize: function(){
            _.bindAll(this, 'render', 'eventHandeler');
            this.render();
        },
        events: {
          'click .a[data-toggle="collapse"]' : 'eventHandeler'
        },
        eventHandeler: function(){
          console.log("event fired");
        },
        render: function () {
            console.log("render orderables");
           // console.log(this.el);
            this.el.append(_.template(orderableTemplate, {}));
        }
    });
    return Orderable;
});
