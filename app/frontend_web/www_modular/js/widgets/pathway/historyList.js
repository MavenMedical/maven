define([
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone

    //views
    'pathway/models/historyCollection',
    'pathway/singleRows/historyRow',

    'text!templates/pathway/historyScroll.html',
    'globalmodels/contextModel',

], function ($, _, Backbone, HistoryCollection, HistoryRow, HistoryListTemplate, contextModel) {
    var historyCollection;

    var HistoryList = Backbone.View.extend({
    extraData: {},
    lastHeight: 0,
    first: true,
    initialize: function(arg) {
        if (typeof arg.template !== "undefined") {
            this.template = _.template(arg.template); // this must already be loaded
        }
        else {
            this.template = _.template(HistoryListTemplate);
        }
        if (typeof arg.extraData !== "undefined") {
            this.extraData = arg.extraData;
        }
        historyCollection = new (HistoryCollection.extend({extraData: this.extraData}));

        this.$el.html(this.template({height:$(window).height()-50+'px'}));1
	    historyCollection.bind('add', this.addHistory, this);
	    historyCollection.bind('reset', this.reset, this);
	    historyCollection.bind('sync', this.render, this);
	    //this.render();
	},
    events: {

    },
	render: function() {
	    this.$el.html(this.template(this));
	    this.addAll();
	},
	addAll: function() {
	    this.reset();
	    var nonempty = false;
	    if (historyCollection.length) {
		for(hist in historyCollection.models) {
			this.addHistory(historyCollection.models[hist]);
			nonempty = true;
		}
	    }
	    if(!nonempty) {
            $('.historyaccordion').html('No History');
            //this.$el.show();
	    }
        else {
            //this.$el.show();
            var historylist = $('.history-scroll', this.$el);
            setTimeout(function () {
                var historyHeight = historylist.innerHeight();
                if (this.lastHeight != historyHeight && historyHeight < parseInt(historylist.css('max-height'))) {
                    this.lastHeight = historyHeight;
                    historyCollection.more();
                }
                else {
                    historylist.scroll(function(e) {
                        if(historylist.scrollTop() + historylist.innerHeight() + 100 >= historylist[0].scrollHeight) {
                            historyCollection.more();
                        }
                        return false;
                    });
                }
            }, 500);
        }
	},
	addHistory: function(history) {
	    var historyrow = new HistoryRow({model: history});
	    $('.historyaccordion', this.$el).append(historyrow.render().el);
	    //this.$el.show();
        //historyrow.events();
	},	
	reset: function() {
	    $('.historytable > tbody', this.$el).empty();
	    this.$el.hide();
	},
    });

    return HistoryList;

});
