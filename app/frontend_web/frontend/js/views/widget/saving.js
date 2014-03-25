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
        el: '.saving',
        template: _.template(savingTemplate),
        initialize: function(){
            _.bindAll(this, 'render');
            this.render();
        },
        render: function () {
          this.$el.html(this.template);
        }
    });
    return Saving;
});
