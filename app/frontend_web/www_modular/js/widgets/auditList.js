define([
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone

    //views
    'globalmodels/auditCollection',
    'singleRow/auditRow',

    'globalmodels/contextModel',
    'libs/jquery/jquery-mousestop-event'
], function ($, _, Backbone, AuditCollection, AuditRow, contextModel) {
    var downloadaudit = ['date', 'patient', 'action', 'target', 'device', 'details'];
    var auditCollection;
    var that;
    var AuditList = Backbone.View.extend({
    extraData: {},
    lastHeight: 0,
    first: true,
    initialize: function(arg) {
        that = this;
        if (typeof arg.extraData !== "undefined") {
            this.extraData = arg.extraData;
        }

	    this.template = _.template(arg.template); // this must already be loaded
        var auditlist = $('.audit-scroll', this.$el);

        auditCollection = new (AuditCollection.extend({extraData: this.extraData}));
	    auditCollection.bind('add', this.addAudit, this);
	    auditCollection.bind('reset', this.reset, this);
	    auditCollection.bind('sync', this.addAll, this);
	    this.render('Loading ...');

        $(auditlist).on('show', function(){
            //make sure that audit list is correct when loaded (target user's audits vs. current user audits)
            auditCollection.reset();
            auditCollection.initialize();
        });

        $(".refreshButton", this.$el).click(function(event){
            $( '.audittable > tbody', this.$el).empty();
            auditCollection.refresh();
        });
        $(".refreshButton", this.$el).hover(function(event) {
            $(event.target).attr('title', "Last Refresh: " + auditCollection.getLastRefresh());
        });

	},
    events: {
        'scroll .audit-scroll': 'handleScroll',
	    'click .download-user-audits': 'downloadAudits'
    },
    showhide: function(){
        if(contextModel.get('page') == 'auditlist'){
            this.$el.show();
        }else{
            this.$el.hide();
        }
    },
    downloadAudits: function() {
        that = this;
        var argData = {};
        $.extend(argData, contextModel.toParams(), this.extraData);
        $.ajax({
            url: "/audits",
            data: $.param(argData),
            success: function (data) {
		require(['libs/jquery/Blob', 'libs/jquery/FileSaver.min'], function(blob, saveAs) {
		    
                    var csvContent = [downloadaudit.join(',')];
                    _.each(data, function (row) {
			csvContent.push('"' + _.map(downloadaudit, function (v) {
                            return row[v].replace(/"/g, '');
			}).join('","') + '"');
                    });
		    var b = new Blob([csvContent.join('\n')], {type: 'data:text/csv;charset=utf-8'});
		    saveAs(b, 'audits.csv');
		});
            },
            error : function () {
            }
        });
    },

	render: function(empty_text) {
	    this.$el.html(this.template(this));
            var auditlist = $('.audit-scroll', this.$el);
            auditlist.scroll(function(e) {
                if(auditlist.scrollTop() + auditlist.innerHeight() + 100 >= auditlist[0].scrollHeight) {
                    auditCollection.more();
                }
                return false;
            });

	    this.addAll(empty_text);
	},
	addAll: function(empty_text) {
	    if (!empty_text || typeof(empty_text) != 'string') {
		empty_text = 'None available';
	    }
	    this.reset();
	    var nonempty = false;
	    if (auditCollection.length) {
            for(audit in auditCollection.models) {
                this.addAudit(auditCollection.models[audit]);
                nonempty = true;
            }
	    }
	    if(!nonempty) {
            $('.audittable > tbody', this.$el).html("<tr class='empty-row'><td colspan=\"5\">"+empty_text+"</td></tr>");
            $('.audittable > thead', this.$el).hide();
            $('.audit-control-row', this.$el).hide();
            this.$el.show();
	    }
        else {
            this.showWidget();
            var auditlist = $('.audit-scroll', this.$el);
            setTimeout(function () {
                var auditHeight = auditlist.innerHeight();
                if (this.lastHeight != auditHeight && auditHeight < parseInt(auditlist.css('max-height'))) {
                    this.lastHeight = auditHeight;
                    auditCollection.more();
                }
            }, 500);
        }
	},
    showWidget: function(){
        $('.audittable > thead', this.$el).show();
        $('.empty-row', this.$el).remove();
        $('.audit-control-row', this.$el).show();
        this.$el.show();
    },
	addAudit: function(audit) {
	    var auditrow = new AuditRow({model: audit});
	    $('.audittable', this.$el).append(auditrow.render().el);
	    this.$el.show();
        //auditrow.events();
        this.showWidget();
	},	
	reset: function() {
	    $('.audittable > tbody', this.$el).empty();
        //this.addAll("Refreshing...");
            //this.render()
	    //this.$el.hide();
	},
    });

    return AuditList;

});
