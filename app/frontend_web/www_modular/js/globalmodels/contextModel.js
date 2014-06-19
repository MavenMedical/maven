/***************************************************************************
 * Copyright (c) 2014 - Maven Medical
 * AUTHOR: 'Asmaa Aljuhani'
 * DESCRIPTION: This Javascript file is for context that will be used within
 *              the application.
 *              This file needed to be called in all other modules.
 * PREREQUISITE: libraries should be predefine in main.js
 * LAST MODIFIED FOR JIRA ISSUE: MAV-98
 **************************************************************************/

define([
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
], function ($, _, Backbone) {
    
    function setActiveStyleSheet(title) {
	var i, a, main;
	for(i=0; (a = document.getElementsByTagName("link")[i]); i++) {
	    if(a.getAttribute("rel").indexOf("style") != -1 && a.getAttribute("title")) {
		a.disabled = true;
		if(a.getAttribute("title") == title) a.disabled = false;
	    }
	}
    }

    var Context = Backbone.Model.extend({
	urlRoot: '/login',
        defaults: {
            page: null,
            userAuth: '',
            patients: '',
            patientAuth: '',
            patientName:'',
            provider: null,
            encounter: null,
            department: null,
	    searchPatient: null,
	    searchDiagnosis: null,
	    loginTemplate: 'login.html',
        },
	toParams: function() {
	    var ret = _.pick(this.attributes,['user','provider','date','daterange',
		 			      'patients','department','userAuth', 'customer_id']);
	    for(var x in ret) {
		if(!ret[x]) {delete ret[x];}
	    }
	    return ret;
	},
	loginCallback: function (res) {
		if(res.get('stylesheet')) {
		    setActiveStyleSheet(res.get('stylesheet'));
		}
		// each row is [html_id, viewfile, templatefile]
		var widgetlist = res.get('widgets');
		var viewlist = []; 
		var templatelist = [];
		for (var ind in widgetlist) {
		    var row = widgetlist[ind];
		    viewlist.push('widgets/'+row[1]);
		    if (row.length==3) {
			templatelist.push('text!/templates/'+row[2]);
		    } else {
			templatelist.push('text!templates/'+row[1]+'.html');
		    }
		    console.log('adding view '+row[1]+' to element '+row[0]+
				' with template '+templatelist[templatelist.length-1]);
		}
		require(viewlist.concat(templatelist),function () {
			for(var i=0;i<viewlist.length;i++) {
			    var view = new arguments[i]({el:$(widgetlist[i][0]),
							 template:arguments[i+viewlist.length]});
			}
			$("#content").show();
			Backbone.history.loadUrl(Backbone.history.fragment);
		    })
	    }, 
        setUser: function (user, pw) {
	    if (this.user != user || !this.userAuth) {
		this.set('user', user);
		//alert('setting user');
		this.fetch({success: this.loginCallback, 
			    data: JSON.stringify({user:user, password:pw}),
			    type: 'POST'});
	    }
	    },
        setProvider: function (provider, customer, userAuth) {
		//alert('setting user');
		this.fetch({success: this.loginCallback, 
			    data: JSON.stringify({provider:provider, 
					customer: customer,
					userAuth: userAuth}),
			    type: 'POST'});
	    },
	});
    
    return new Context;
});
