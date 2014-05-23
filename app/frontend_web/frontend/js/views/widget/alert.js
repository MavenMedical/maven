/**
 * Created by Asmaa Aljuhani on 3/11/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone

    'currentContext',

    //sub view
    '../singleRow/alertRow',

    //Model
    'models/alertModel',

    'collections/alerts',
    'text!templates/templatesA/widget/alert.html'
	], function ($, _, Backbone,currentContext, alertRow, AlertModel, AlertCollection, alertTemplate) {

    var Alert = Backbone.View.extend({
        el: '.alertlist',
        template: _.template(alertTemplate),

        initialize: function(){
		//console.log("alert ini ");
            _.bindAll(this, 'render', 'addAlert');
            this.alerts = new AlertCollection;
            this.alerts.bind('add', this.addAlert, this);
            this.alerts.fetch({data: $.param(currentContext.toJSON())});
            this.render();
        },
        render: function () {
		//console.log('alert render');
            this.$el.html(this.template);

        },
        addAlert: function (alrt){
		//console.log("add alert");
            var alertrow = new alertRow({
                model: alrt
            });
         $('#accordion2').append(alertrow.render().el);
        }
    });
    return Alert;
});
