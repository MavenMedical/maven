
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone



    'text!templates/detailPanel/detailSection.html'
], function ($, _, Backbone, detailSectionTemplate) {

    var DetailGroup = Backbone.View.extend({

        template: _.template(detailSectionTemplate),
        initialize: function(params){
          this.lineTemplate = params.lineTemplate;
          this.heading= params.heading;
          this.list= params.list;;



        },
        render: function(){
            this.$el.html(this.template(this));
            this.list.each(function(cur) {

                $('.items', this.$el).append(this.lineTemplate(cur.attributes))


            } , this);
            return this;

        }

    });

    return DetailGroup;

});
