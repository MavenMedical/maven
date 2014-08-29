define([
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone

    //views
    'globalmodels/auditCollection',
    'singleRow/auditRow',
], function ($, _, Backbone, auditCollection, AuditRow) {

    var AuditList = Backbone.View.extend({
    targetProvider:null,
    targetCustomer:null,
	initialize: function(arg) {
        if (arg.targetProvider || arg.targetCustomer)
        {
            this.userFilter = "active";
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
            $('.audittable > tbody', this.$el).html("<tr><td colspan=\"2\">None available</td></tr>");
           this.$el.show();
	    }
        else {
            this.$el.show();
            var auditlist = $('.auditlist', this.$el);
            setTimeout(function () {
                var auditHeight = auditlist.innerHeight();
                if (auditHeight > 0 && auditHeight < parseInt(auditlist.css('max-height'))) {
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
