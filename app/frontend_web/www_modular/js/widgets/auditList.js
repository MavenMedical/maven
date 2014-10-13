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

    var downloadaudit = ['date', 'patient', 'action', 'device', 'details'];
    var auditCollection;

    var AuditList = Backbone.View.extend({
    targetUser:null,
    targetCustomer:null,
    lastHeight: 0,
    initialize: function(arg) {
        auditCollection = new AuditCollection;

        if (arg.targetUser || arg.targetCustomer)
        {
            this.targetUser = arg.targetUser;
            this.targetCustomer = arg.targetCustomer;
            auditCollection.data="target_user="+arg.targetUser+"&target_customer="+arg.targetCustomer;
        }
        else
        {
            auditCollection.data = "";
        }
	    auditCollection.reset();
        auditCollection.initialize();
	    this.template = _.template(arg.template); // this must already be loaded
        this.$el.html(this.template({height:$(window).height()-50+'px'}));
	    auditCollection.bind('add', this.addAudit, this);
	    auditCollection.bind('reset', this.reset, this);
	    auditCollection.bind('sync', this.render, this);
	    this.render('Loading ...');
        var auditlist = $('.audit-scroll', this.$el);
	    auditlist.scrollTop(0);
        auditlist.scroll(function() {
            if(auditlist.scrollTop() + auditlist.innerHeight() + 100 >= auditlist[0].scrollHeight) {
                auditCollection.more();
            }
	    });
        $(auditlist).on('show', function(){
            //make sure that audit list is correct when loaded (target user's audits vs. current user audits)
            auditCollection.reset();
            auditCollection.initialize();
        });
	},
    events: {
        'scroll .audit-scroll': 'handleScroll',
	    'click .download-user-audits': 'downloadAudits',
    },
    handleScroll: function(){
        console.log("Scrolling!");
    },
    downloadAudits: function() {
        that = this;
        var extra_data = "";
        if (that.targetUser && that.targetCustomer) {
            extra_data = "&target_user=" + that.targetUser + "&target_customer=" + that.targetCustomer;
        }

        $.ajax({
            url: "/audits",
            data: $.param(contextModel.toParams()) + extra_data,
            success: function (data) {
                var csvContent = ["data:text/csv;charset=utf-8," + downloadaudit.join(',')];
                _.each(data, function (row) {
                    csvContent.push('"' + _.map(downloadaudit, function (v) {
                        return row[v].replace(/"/g, '');
                    }).join('","') + '"');
                });
                window.open(encodeURI(csvContent.join('\n')));
            },
            error : function () {
            }
        });
    },

	render: function(empty_text) {
	    this.$el.html(this.template(this));
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
            $('.audittable > tbody', this.$el).html("<tr><td colspan=\"5\">"+empty_text+"</td></tr>");
            $('.audittable > thead', this.$el).hide();
            $('.audit-control-row', this.$el).hide();
            this.$el.show();
	    }
        else {
            $('.audittable > thead', this.$el).show();
            $('.audit-control-row', this.$el).show();
            this.$el.show();
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
	addAudit: function(audit) {
	    var auditrow = new AuditRow({model: audit});
	    $('.audittable', this.$el).append(auditrow.render().el);
	    this.$el.show();
        //auditrow.events();
	},	
	reset: function() {
	    $('.audittable > tbody', this.$el).empty();
	    this.$el.hide();
	},
    });

    return AuditList;

});
