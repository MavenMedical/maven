/**
 * Created by Asmaa Aljuhani on 3/11/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'currentContext',

    'text!templates/chart/costbd.html'
], function ($, _, Backbone, currentContext, costbdTemplate) {

    var CostBD = Backbone.View.extend({
        el: '.costbd',
        template: _.template(costbdTemplate),
        initialize: function(){
            _.bindAll(this, 'render', 'click');
            this.render();
        },
        events:{
            'click': 'click'
        },
        click:function(){
          console.log('clicked');
        },
        render: function () {
            this.$el.html(this.template({page: currentContext.get('page')}));
            return this;
        }
    });
    return CostBD;
});

//Chart codes are in the template file costbd.html