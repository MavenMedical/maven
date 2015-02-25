define([
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone

    //views
    'globalmodels/userCollection',
    'singleRow/userRow',

    'globalmodels/contextModel',
    'text!templates/userScroll.html'

], function ($, _, Backbone, UserCollection, UserRow, contextModel, UserListTemplate) {

    var userCollection;

    var UserList = Backbone.View.extend({
    extraData: {},
	initialize: function(arg) {
        if (typeof arg.template !== "undefined") {
            this.template = _.template(arg.template); // this must already be loaded
        }
        else {
            this.template = _.template(UserListTemplate);
        }
        if (typeof arg.extraData !== "undefined") {
            this.extraData = arg.extraData;
        }
        //initialize user collection with all required data
        userCollection = new (UserCollection.extend({extraData: this.extraData}));

        this.$el.html(this.template({height:$(window).height()-50+'px'}));
	    userCollection.bind('add', this.addUser, this);
	    userCollection.bind('reset', this.reset, this);
	    userCollection.bind('sync', this.addAll, this);

	    this.render();
        var userlist = $('.useraccordion', this.$el);
	    userlist.scrollTop(0);
	    userlist.scroll(function() {
		if(userlist.scrollTop() + userlist.innerHeight() + 100 >= userlist[0].scrollHeight) {
		    userCollection.more();
		}
	    });

        $(".refreshButton", this.$el).click(function(event){
            $( '.usertable > tbody', this.$el).empty();
            userCollection.refresh();
        });
        $(".refreshButton", this.$el).hover(function(event) {
            $(event.target).attr('title', "Last Refresh: " + userCollection.getLastRefresh());
        });

	},
    events: {
	    'click #save-user-changes': 'saveChanges'
    },
    saveChanges: function() {
    /*    that = this;
        $(".user-row").each(function () {
            var user_id  = $(this).find(".user-val-id").html();
            var state="disabled";
            if($(this).find('.user-state').is(':checked'))
            {
                    state = "active";
            }
            $.ajax({
                url: "/update_user",
                data: $.param(contextModel.toParams()) + "&target_user=" + user_id +
                                                         "&state=" + state,
                success: function () {
                    $("#save-user-message").html("Changes Saved!");
                },
                error : function () {
                     $("#save-user-message").html("Sorry, an error occurred. Please try again later");
                }
            });
        });*/
    },
	render: function() {
	    this.$el.html(this.template(this));
	    this.addAll();
        $(window).resize(function() {
            $(".usertable-header").width($('.usertable', this.$el).width());
        });
	},
	addAll: function() {
	    this.reset();
	    var nonempty = false;
	    if (userCollection.length) {
            for(user in userCollection.models) {
                this.addUser(userCollection.models[user]);
                nonempty = true;
            }
	    }
        userCollection.lastRefresh = new Date();

        var userlist = $('.useraccordion', this.$el);
        var usertable = $('.usertable', this.$el);
        $(document).ready(function(){
            setTimeout(function() {
                $(".usertable-header").width(usertable.width());
            },200);
        });

        setTimeout(function() {
            var newWidth = userlist.innerWidth();
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
	},	
	reset: function() {
	    $('.usertable > tbody', this.$el).empty();
	},
    refresh: function() {
        this.reset();
    }
    });

    return UserList;
});
