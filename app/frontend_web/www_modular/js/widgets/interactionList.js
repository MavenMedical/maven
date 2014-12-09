define([
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone

    //views
    'globalmodels/interactionCollection',
    'singleRow/interactionRow',

    'globalmodels/contextModel',
    'libs/jquery/jquery-mousestop-event'
], function ($, _, Backbone, InteractionCollection, InteractionRow, contextModel) {
    var downloadinteraction = ['date', 'patient', 'action', 'target', 'device', 'details'];
    var interactionCollection;

    var InteractionList = Backbone.View.extend({
    extraData: {},
    lastHeight: 0,
    first: true,
    initialize: function(arg) {
        if (typeof arg.extraData !== "undefined") {
            this.extraData = arg.extraData;
        }
        interactionCollection = new (InteractionCollection.extend({extraData: this.extraData}));

	    this.template = _.template(arg.template); // this must already be loaded
        this.$el.html(this.template({height:$(window).height()-50+'px'}));
	    interactionCollection.bind('add', this.addInteraction, this);
	    interactionCollection.bind('reset', this.reset, this);
	    interactionCollection.bind('sync', this.render, this);
	    this.render('Loading ...');
        var interactionlist = $('.interaction-scroll', this.$el);

        $(interactionlist).on('show', function(){
            //make sure that interaction list is correct when loaded (target user's interactions vs. current user interactions)
            interactionCollection.reset();
            interactionCollection.initialize();
        });

	},
        events: {
            'scroll .interaction-scroll': 'handleScroll',
        },
	render: function(empty_text) {
	    this.$el.html(this.template(this));
	    this.addAll(empty_text);
            $(".refreshButton", this.$el).click(function(event){
                $('.interactiontable > tbody', this.$el).empty();
                interactionCollection.refresh();
            });
            $(".refreshButton", this.$el).hover(function(event) {
                $(event.target).attr('title', "Last Refresh: " + interactionCollection.getLastRefresh());
            });
	},
	addAll: function(empty_text) {
	    if (!empty_text || typeof(empty_text) != 'string') {
		empty_text = 'None available';
	    }
	    this.reset();
	    var nonempty = false;
	    if (interactionCollection.length) {
		for(interaction in interactionCollection.models) {
		    this.addInteraction(interactionCollection.models[interaction]);
		    nonempty = true;
		}
	    }
	    if(!nonempty) {
                $('.interactiontable > tbody', this.$el).html("<tr><td colspan=\"5\">"+empty_text+"</td></tr>");
                $('.interactiontable > thead', this.$el).hide();
                $('.interaction-control-row', this.$el).hide();
                this.$el.show();
	    }
            else {
                $('.interactiontable > thead', this.$el).show();
                $('.interaction-control-row', this.$el).show();
                this.$el.show();
                var interactionlist = $('.interaction-scroll', this.$el);
                setTimeout(function () {
                    var interactionHeight = interactionlist.innerHeight();
                    if (this.lastHeight != interactionHeight && interactionHeight < parseInt(interactionlist.css('max-height'))) {
                        this.lastHeight = interactionHeight;
                        interactionCollection.more();
                    }
                    else {
                        
                        interactionlist.scroll(function(e) {
                            if(interactionlist.scrollTop() + interactionlist.innerHeight() + 100 >= interactionlist[0].scrollHeight) {
                                interactionCollection.more();
                            }
                            return false;
                        });
                    }
                }, 500);
            }
	},
	addInteraction: function(interaction) {
	    var interactionrow = new InteractionRow({model: interaction});
	    $('.interactiontable', this.$el).append(interactionrow.render().el);
	    this.$el.show();
        //interactionrow.events();
	},	
	reset: function() {
	    $('.interactiontable > tbody', this.$el).empty();
	    this.$el.hide();
	},
    });

    return InteractionList;

});
