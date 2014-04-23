/**
 * Created by Asmaa Aljuhani on 3/14/14.
 */

define([
    'underscore',
    'backbone'
], function (_, Backbone) {

    var SpendingModel = Backbone.Model.extend({
	    urlRoot: '/spending',
	    clickType: function(x, that) {
		that.set({title:x.dataItem.title});
	    },
	    clickDate: function(x,that) {
		var d=x.item.dataContext.date;
		//console.log(d);
		d.setHours(0);
		d.setMinutes(0);
		d.setSeconds(0);
		d.setMilliseconds(0);
		that.set({date:d});
	    }
	});
    
    return SpendingModel;
       });