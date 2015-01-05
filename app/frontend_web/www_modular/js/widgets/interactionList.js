define([
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone

    //views
    'globalmodels/interactionCollection',
    'singleRow/interactionRow',

    'globalmodels/contextModel',
    'pathway/models/treeContext'
], function ($, _, Backbone, InteractionCollection, InteractionRow, contextModel, treeContext) {
    var interactionCollection;

    var flip = function() {
        var historyposition = contextModel.get('historyposition')
        if (typeof historyposition !== 'undefined') {
            contextModel.set('historyposition', historyposition+1)
        }
    }

    var keyflip =  function(evt) {
        if (evt.keyCode == 13 || evt.keyCode == 39) {
	    evt.preventDefault()
            flip()
        }
    }
    
    $(document).keydown(function(evt) {keyflip(evt)})


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
            this.$el.html(this.template());
	    interactionCollection.bind('add', this.addInteraction, this);
	    interactionCollection.bind('reset', this.reset, this);
	    //interactionCollection.bind('sync', this.render, this);
	    this.render('Loading ...');
	    contextModel.on('change:page change:history', function() {this.showhide()}, this)
            contextModel.on('change:history change:historyposition change:historydetails', function() {this.updatehistory()}, this)
	},
        updatehistory: function() {
            var history = contextModel.get('history')
            var historyposition = contextModel.get('historyposition')
            var historydetails = contextModel.get('historydetails')
            if (history == null || historyposition == null || historydetails == null) {
                treeContext.suppressClick=false
                Backbone.history.navigate('', true)
                return
            }
            treeContext.suppressClick=true
            var progress = (historyposition+1)
            if (progress > history.length) {
                contextModel.set({history: null, historyposition: null, historydetails: null})
            } else {
                var navstring = 'pathway/' + historydetails.get('protocol')
                    + '/node/-' + history[historyposition]['node_id'] 
                    //+ '/patient/' + historydetails.get('patient') + '/' + historydetails.get('date').slice(0,10)

                Backbone.history.navigate(navstring, true)
                $('#historyheader').text(historydetails.get('protocolname') + " pathway interaction replay: " + historydetails.get('providername') +
                                         " with " + historydetails.get('patientname') + ' on ' + history[historyposition].datetime)
                $('.progress-bar', this.$el).width((progress*100/history.length)+'%')
                
                var action = history[historyposition]['action']

                if (action == 'click') {
                    $('#historydetails').text('traversing the tree')
                } else if (action == 'send') {
                    $('#historydetails').text('forwarding the chart')
                } else if (action == 'copy') {
                    $('#historydetails').text('copying protocol text to the clipboard')
                } else if (action == 'followup') {
                    $('#historydetails').text('scheduling a follow-up message')
                } else if (action == 'checked') {
                    $('#historydetails').text('checking an optional item ' + history[historyposition]['details'])
                } else if (action == 'unchecked') {
                    $('#historydetails').text('unchecking an optional item ' + history[historyposition]['details'])
                } else {
                    $('#historydetails').text('')
                }
                if (progress == history.length) {
                    $('#nextinteraction').html('Finish')
                } else {
                    $('#nextinteraction').html('Next')
                }                        
            }
        },
        showhide: function() {
            
            var page = contextModel.get('page')
	    if (page=='home') {
                this.$el.show()
                $(this.interactioncontrols).hide()
                $(this.interactionlist).show()
            } else if (page=='pathway' && contextModel.get('history')) {
                this.$el.show()
                $(this.interactionlist).hide()
                $(this.interactioncontrols).show()
	    } else {
		this.$el.hide()
	    }
        },
	render: function(empty_text) {
            this.$el.html(this.template());
            if (interactionCollection.length) {
                
            }
	    this.addAll();
            this.interactionlist = $('#listinteractions', this.$el);
            var interactionscroll = $('.interaction-scroll', this.$el)
            interactionscroll.scroll(function(e) {
                if(interactionscroll.scrollTop() + interactionscroll.innerHeight() + 100 >= interactionscroll[0].scrollHeight) {
                    interactionCollection.more();
                }
                return false;
            });
            
            this.interactioncontrols = $('#interactioncontrols', this.$el)
            $('#nextinteraction', this.$el).click(function() {flip()})
            $(this.interactionlist).on('show', function(){
                //make sure that interaction list is correct when loaded (target user's interactions vs. current user interactions)
                interactionCollection.reset();
                interactionCollection.initialize();
            });
            $(".refreshButton", this.$el).click(function(event){
                $('.interactiontable > tbody', this.$el).empty();
                interactionCollection.refresh();
            });
            $(".refreshButton", this.$el).hover(function(event) {
                $(event.target).attr('title', "Last Refresh: " + interactionCollection.getLastRefresh());
            });
            this.showhide()
	},
	addAll: function(empty_text) {
	    this.reset();
	    var nonempty = false;
	    if (interactionCollection.length) {
		for(interaction in interactionCollection.models) {
		    this.addInteraction(interactionCollection.models[interaction]);
		    nonempty = true;
		}
	    }
            else {
                $('.interactiontable > thead', this.$el).show();
                $('.interaction-control-row', this.$el).show();
                this.showhide();
                var interactionlist = $('.interaction-scroll', this.$el);
                setTimeout(function () {
                    var interactionHeight = interactionlist.innerHeight();
                    if (this.lastHeight != interactionHeight && interactionHeight < parseInt(interactionlist.css('max-height'))) {
                        this.lastHeight = interactionHeight;
                        interactionCollection.more();
                    }
                }, 500);
            }
	},
	addInteraction: function(interaction) {
	    var interactionrow = new InteractionRow({model: interaction});
	    $('.interactiontable', this.$el).append(interactionrow.render().el);
	    this.showhide();
        //interactionrow.events();
	},	
	reset: function() {
	    $('.interactiontable > tbody', this.$el).empty();
	    this.$el.hide();
	},
    });

    return InteractionList;

});
