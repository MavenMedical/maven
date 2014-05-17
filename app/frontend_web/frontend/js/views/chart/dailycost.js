/**
 * Created by Asmaa Aljuhani on 3/11/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'currentContext',
    'text!templates/templatesA/chart/dailycost.html'
], function ($, _, Backbone, currentContext, dailycostTemplate) {

    var DailyCost = Backbone.View.extend({
        el: '.dailycost',
        template: _.template(dailycostTemplate),
        initialize:function(){
            _.bindAll(this,'render');
            this.render();
        },
        render: function () {
            this.$el.html(this.template({ page: currentContext.get('page')}));
            return this;
        }
    });
    return DailyCost;
});
//Chart codes are in the template file dailycost.html