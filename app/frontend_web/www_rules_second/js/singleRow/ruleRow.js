/* a Backbone view displaying a row of the rule list
   dynamically resizes when its rule is selected and shrinks when another rule is selected
 */
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'models/contextModel',
    'models/ruleModel',
    'models/ruleCollection',
    'text!templates/ruleRow.html'

], function ($, _, Backbone, contextModel, ruleModel, ruleCollection, ruleRowTemplate) {

    var ruleRow = Backbone.View.extend({
        tagName: 'tr',
        template: _.template(ruleRowTemplate),
        //define events
        events:{
	    'click .select-button': 'handleSelect',
	    'click .remove-button': 'handleRemove'
        },
        render: function(){
            $(this.el).html(this.template(this.model.toJSON()));
            return this;
        },
        initialize: function(){
            //event: listen for a rule being selected, if it isnt this one, shrink it to normal size
            ruleModel.on('selected', function(){
                if (ruleModel.get('id')!=this.model.get('id'))
                    this.$el.css({'font-size': '100%'})
            }, this)

        },
        handleSelect: function() {
            //if someone clicks this rule, set the context model's id to this id, which will trigger its load
            contextModel.set({id:this.model.get("id"),
			                name:this.model.get("name")});
                     var that = this;
            //also enlarge the text of this view
            this.$el.css({'font-size': '200%'});


            // don't remember what this does
            ruleModel.on('propagate:name',
			 function(model) {
			     if(contextModel.get('id') == this.model.get('id')) {
				 this.model.set({name: ruleModel.get('name')});
				 this.render()
			     } else {
		    		 ruleModel.off('propagate:name', null, this);
			     }
			 },
			 this);

        },
        //when the remove button is clicked
    	handleRemove: function() {

            var temp;
            //get the params
            //dont set the context model, as this would change the selected rule, instead just set the params
            temp = contextModel.toParams();
            temp.id = this.model.get('id');
            //if the id is the selected rule, empty the rule model and set the context model to hide the triggers and
            //details
            if (this.model.get('id')==ruleModel.get('id')) {
                                                            ruleModel.clearData();
                                                            contextModel.set({showTriggers: false, showDetails:false})
            }
           //set the url and destroy the rule in the persistance
           this.model.url = "/rule?" + decodeURIComponent($.param(temp));
           this.model.destroy();

	       //this.model.url('/rule?' + decodeURIComponent($.param(contextModel.toParams())););
    	}
    });

    return ruleRow;

});
