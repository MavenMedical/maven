define([
    'jquery',
    'underscore',
    'backbone',
    'globalmodels/contextModel'
], function($, _, Backbone, contextModel) {
    AlertModel = Backbone.Model;

    var AlertCollection = Backbone.Collection.extend({
	url: function() {return '/alerts/'+this.offset+'-'+(this.offset+this.limit);},
	limit: 3,
	tried: 0,
	offset: 0,
	model: AlertModel,
	initialize: function(){
            // nothing here yet
        },
	more: function() {
	    if(this.tried <= this.models.length) {
		this.offset = this.models.length;
		this.tried = this.models.length+this.limit;
		alertCollection.fetch({
		    data:$.param(contextModel.toParams()),
		    remove:false});
	    }
	}
    });

    alertCollection = new AlertCollection;
    if(contextModel.get('userAuth')) {
	this.tried = 0;
	this.offset=0;
	alertCollection.fetch({
	    data:$.param(contextModel.toParams()),
	    remove:true});
    }
    contextModel.on('change:patients', 
		    // this will be needed once the context filters things
		    function(cm) {
			if(true && cm.get('userAuth')) {
			    this.tried = 0;
			    this.offset=0;
			    alertCollection.fetch({
				data:$.param(contextModel.toParams()),
				remove:true});
			}
		    }, alertCollection);
    //alertCollection.on('all', function(en) { console.log('alertCollection: '+en);});

    return alertCollection;
});
