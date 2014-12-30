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

    function scheduleLogout(offset) {
	var expiration = readCookie('valid-through');
	if(expiration) {
	    var remaining = expiration - (new Date()) + offset;
	    if (remaining > 0) {
		setTimeout(function() {scheduleLogout(offset)}, remaining);
	    } else {
		eraseCookie('valid-through');
		location.href = '#logout';
	    }
	}
    }

    var loginCallback = function (res) {
        console.log('login call back', contextModel);
        var offset = (new Date()) - readCookie('now')
        scheduleLogout(offset);
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
        } else if (widgetlist[i].element =='fixed-topB') {
            $('#fixed-topB').append("<div class='col-xs-12'></div>")
	    el = $('.col-xs-12', $('#fixed-topB')).last()
        } else {
            el = $("#"+ widgetlist[i].element)
	}
	try {
            new arguments[i]({template: arguments[i+viewlist.length], el: el})
	    } catch(err) {
		console.log('failed to start widget ', widgetlist[i], err)
	    }
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
	    customer: null,
            userAuth: '',
            patients: '',
            patientAuth: '',
            patientName:'',
            pathid: 0,
            canonical: null,
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
	    var ret = _.pick(this.attributes,['startdate','enddate','encounter',
		 			      'patients','department', 'pathid']);
        ret.id = ret.pathid
	    //console.log(ret);
	    for(var x in ret) {
		if(ret[x] === null || (x != 'provider' && ret[x] === '')) {delete ret[x];}
	    }
	    return ret;
	},
        setUser: function (user, pw, oauth, customer, newpw) {
	    if (this.user != user || !this.userAuth) {
		this.set({'user': user, 'customer': customer, 'login-message': null});
		var that=this;
		
		var data;
		if (pw) {
		    data = {user:user, password:pw, customer_id:customer};
		    } else {
			data = {user:user, oauth:oauth, customer_id:customer};
		    }
		if(newpw)
		    data.newpassword=newpw;
		this.fetch({success:  loginCallback,
			    error: function(request, response) { that.set(response.responseJSON);},
			    data: JSON.stringify(data),
			    type: 'POST'});
	    }
	},
        autoSetUser: function (user, customer, userAuth, Login) {
	    var that=this;
	    
	    this.set({user:user, customer:customer, userAuth: null});
	    if (userAuth) {
		this.fetch({success: loginCallback, 
			error: function(request, response) { 
			    that.set(response.responseJSON);
			    new Login({el: '#login-modal'})
			},
			data: JSON.stringify({user:user,
					      customer_id: customer,
					      userAuth: userAuth}),
			type: 'POST'});
	    } else if(document.cookie && (!user || readCookie('user')==user)) {
		    this.fetch({
                url: '/refresh_login',
                success: loginCallback,
                error: function(){
                    new Login({el: '#login-modal'})
                }
		    });
	    } else {
		new Login({el: '#login-modal'})
	    }
	}
    });

    contextModel = new ContextModel;
    contextModel.on('change:page', function() {window.scrollTo(0,0)})
    
    return contextModel;
});
