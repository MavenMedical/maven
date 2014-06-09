
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone



    'text!templates/detailSection.html'
], function ($, _, Backbone, detailSectionTemplate) {

    var DetailGroup = Backbone.View.extend({

        template: _.template(detailSectionTemplate),
        initialize: function(params){
          this.lineTemplate = params.lineTemplate;
          this.heading= params.heading;
          this.list= params.list;;
          console.log(this.list);


        },
        render: function(){
            console.log()
            this.$el.html(this.template(this));
            this.list.each(function(cur) {

                console.log(cur);
                $('.items', this.$el).append(this.lineTemplate(cur.attributes))


            } , this);
            return this;

        }

    });

    return DetailGroup;

});
