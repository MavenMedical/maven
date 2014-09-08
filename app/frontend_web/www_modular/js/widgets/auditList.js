define([
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone

    //views
    'globalmodels/auditCollection',
    'singleRow/auditRow',

    'globalmodels/contextModel'
], function ($, _, Backbone, auditCollection, AuditRow, contextModel) {

    var AuditList = Backbone.View.extend({
    targetProvider:null,
    targetCustomer:null,
    lastHeight: 0,
	initialize: function(arg) {
        if (arg.targetProvider || arg.targetCustomer)
        {
            this.targetProvider = arg.targetProvider;
            this.targetCustomer = arg.targetCustomer;
            auditCollection.data="target_provider="+arg.targetProvider+"&target_customer="+arg.targetCustomer;
        }
        else
        {
            auditCollection.data = "";
        }
        auditCollection.initialize();
	    this.template = _.template(arg.template); // this must already be loaded
        this.$el.html(this.template({height:$(window).height()-50+'px'}));
	    auditCollection.bind('add', this.addAudit, this);
	    auditCollection.bind('reset', this.reset, this);
	    auditCollection.bind('sync', this.addAll, this);
		//this.render();
	    //}, this);
	    this.render();
        var auditlist = $('.auditlist', this.$el);
	    auditlist.scrollTop(0);
	    auditlist.scroll(function() {
		if(auditlist.scrollTop() + auditlist.innerHeight() + 100 >= auditlist[0].scrollHeight) {
		    auditCollection.more();
		}
	    });
	},
    events: {
	    'click .download-user-audits': 'downloadAudits',
    },
    downloadAudits: function() {
        that = this;
        var extra_data = "";
        if (that.targetProvider && that.targetCustomer) {
            var extra_data = "&target_provider=" + that.targetProvider + "&target_customer=" + that.targetCustomer;
        }

        $.ajax({
            url: "/download_audits",
            data: $.param(contextModel.toParams()) + extra_data,
            success: function (data) {
                    //window.open(data);
            },
            error : function () {
            }
        });
    },

	render: function() {
	    this.$el.html(this.template(this));
	    this.addAll();
	},
	addAll: function() {
	    this.reset();
	    var nonempty = false;
	    if (auditCollection.length) {
		for(audit in auditCollection.models) {
			this.addAudit(auditCollection.models[audit]);
			nonempty = true;
		}
	    }
	    if(!nonempty) {
            $('.audittable > tbody', this.$el).html("<tr><td colspan=\"5\">None available</td></tr>");
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
