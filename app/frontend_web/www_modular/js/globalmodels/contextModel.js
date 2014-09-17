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
    'backbone'    // lib/backbone/backbone
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

    var contextModel;

    var loginCallback = function (res) {
	contextModel.set({'loginTemplate':null});
	//if(res.get('stylesheet')) {

	    setActiveStyleSheet('demo');
	//}
	// each row is {element, widget, template}
	var widgetlist = res.get('widgets');
	var viewlist = [];

	var templatelist = [];
	for (var ind in widgetlist) {
	    var row = widgetlist[ind];
	    viewlist.push('widgets/'+row.widget);
		templatelist.push('text!/templates/'+row.template);
	    console.log('adding view '+row.widget +' to element #'+row.element +
			' with template '+ row.template); //templatelist[templatelist.length-1]);
	}
	require(viewlist.concat(templatelist), function () {
	    for(var i=0;i<viewlist.length;i++) {

        var el
        if (widgetlist[i].element =='contentRow'){
            $('#dynamic-content').append("<div class='row content-row'></div>")
	    el = $('.row', $('#dynamic-content')).last()
	} else if (widgetlist[i].element == 'floating-right') {
            $('#floating-right').append("<div class='row content-row'></div>")
	    el = $('.row', $('#floating-right')).last()
	} else if (widgetlist[i].element =='floating-left') {
            $('#floating-left').append("<div class='row content-row'></div>")
	    el = $('.row', $('#floating-left')).last()
        } else {
            el = $("#"+ widgetlist[i].element)
	}
            new arguments[i]({template: arguments[i+viewlist.length], el: el})
	    }
	    $("#content").show();
	    Backbone.history.loadUrl(Backbone.history.fragment);
	})
    }
    
    var ContextModel = Backbone.Model.extend({
	urlRoot: '/login',
        defaults: {
            page: null,
	    user: null,
            userAuth: '',
            patients: '',
            patientAuth: '',
            patientName:'',
            pathid: 0,
            provider: null,
            encounter: null,
            department: null,
	    searchPatient: null,
	    searchDiagnosis: null,
	    loginTemplate: 'login.html',
        settingsTemplate: 'settings.html'
        },
	toParams: function() {
	    //console.log(this);
	    var ret = _.pick(this.attributes,['user','provider','startdate','enddate','encounter',
		 			      'patients','department','userAuth', 'customer_id',
					      'roles', 'pathid', 'userid']);
        ret.id = ret.pathid
	    //console.log(ret);
	    for(var x in ret) {
		if(ret[x] === null || (x != 'provider' && ret[x] === '')) {delete ret[x];}
	    }
	    return ret;
	},
        setUser: function (user, pw, oauth, customer, newpw) {
	    if (this.user != user || !this.userAuth) {
		this.set('user', user);
		var that=this;
		
		var data;
		if (pw) {
		    data = {user:user, password:pw, customer_id:customer};
		    } else {
			data = {user:user, oauth:oauth, customer_id:customer};
		    }
		if(newpw)
		    data.newpassword=newpw;
		this.fetch({success: loginCallback,
			    error: function(request, response) { that.set(response.responseJSON);},
			    data: JSON.stringify(data),
			    type: 'POST'});
	    }
	},
        autoSetUser: function (user, customer, userAuth) {
	    var that=this;
	    this.fetch({success: loginCallback, 
			error: function(request, response) { that.set(response.responseJSON);},
			data: JSON.stringify({user:user,
					      customer_id: customer,
					      userAuth: userAuth}),
			type: 'POST'});
	}
    });

    contextModel = new ContextModel;
    
    return contextModel;
});
