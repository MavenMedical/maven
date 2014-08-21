define([
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone

    //views
    'globalmodels/userCollection',
    'singleRow/userRow',
], function ($, _, Backbone, userCollection, UserRow) {

    var UserList = Backbone.View.extend({
	initialize: function(arg) {
	    this.typeFilter = arg.typeFilter;
	    this.template = _.template(arg.template); // this must already be loaded
        this.$el.html(this.template({height:$(window).height()-50+'px'}));
	    userCollection.bind('add', this.addUser, this);
	    userCollection.bind('reset', this.reset, this);
	    userCollection.bind('sync', this.addAll, this);
	    //spendingModel.on('change:typeFilter', function() {
		//this.render();
	    //}, this);
	    this.render();
        var userlist = $('.useraccordion', this.$el);
	    userlist.scrollTop(0);
	    userlist.scroll(function() {
		if(userlist.scrollTop() + userlist.innerHeight() + 100 >= userlist[0].scrollHeight) {
		    userCollection.more();
		}
	    });
	},
	render: function() {
	    this.$el.html(this.template(this));
	    this.addAll();
	},
	addAll: function() {
	    this.reset();
	    var typefilter = this.typeFilter; 
	    var nonempty = false;
	    if (userCollection.length) {
		for(user in userCollection.models) {
			this.addUser(userCollection.models[user]);
			nonempty = true;
		}
	    }
	    if(nonempty) {
		this.$el.show();
	    } else {
		this.$el.hide();
	    }

        var userlist = $('.useraccordion', this.$el);
        setTimeout(function() {
            var userHeight = userlist.innerHeight();
            if (userHeight > 0 && userHeight < parseInt(userlist.css('max-height'))) {
                userCollection.more();
            }
        },500);
	},
	addUser: function(user) {
	    var userrow = new UserRow({model: user});
	    $('.usertable').append(userrow.render().el);
	    this.$el.show();
        userrow.events();
	},	
	reset: function() {
	    $('.usertable > tbody', this.$el).empty();
	    this.$el.hide();
	},
    });

    return UserList;

});