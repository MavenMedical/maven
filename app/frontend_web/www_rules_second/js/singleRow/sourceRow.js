/* a backbone view which displays a row of info about a evidence source
    params:
        model: the Backbone model representing the source to be displayed
        parent: the Backbone Collection containing the source


 */
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'models/contextModel',
    'models/ruleModel',
    'text!templates/sourceRow.html'

], function ($, _, Backbone, contextModel, ruleModel, sourceRowTemplate) {

    var sourceRow = Backbone.View.extend({
        template: _.template(sourceRowTemplate),
        events:{
	       'click .remove-button': 'handleRemove'
        },
        initialize: function(params){
            //set the params
            this.model = params.model;
            this.parent = params.parent;
            this.template = _.template(params.template)

        },
        render: function(){
            //render
            $(this.el).html(this.template(this.model.toJSON()));
            return this;
        },
        //if the button is clicked remove the model from its parent
    	handleRemove: function() {

            this.parent.remove(this.model);
    	}
    });

    return sourceRow

});
