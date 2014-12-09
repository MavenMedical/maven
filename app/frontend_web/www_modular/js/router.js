/***************************************************************************
 * Copyright (c) 2014 - Maven Medical
 * AUTHOR: 'Asmaa Aljuhani'
 * DESCRIPTION: This Javascript file has the main router functions that calls
 *               all other views.
 * PREREQUISITE: libraries should be predefine in main.js
 * LAST MODIFIED FOR JIRA ISSUE: MAV-98
 **************************************************************************/

define([
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone,

    'globalmodels/contextModel',
    'globalmodels/layoutModel',
    'widgets/evidence',
    'widgets/login',
    'widgets/settings'
], function ($, _, Backbone, currentContext, layoutModel, Evidence, Login, Settings) {

    var CheckLogin = function () {
        if (!currentContext.get('user') || !currentContext.get('userAuth')) {
            new Login({el: '#login-modal'})
            return false;
        }
        return true;
    };
    //This variables holds an array of the content of the container in index.html
    var layout = ["#floating-left",
                  "#dynamic-content",
                  "#floating-right"];
    //This variable holds each page and its layout
    // array length should match the number of layouts
    // the sum of each array should be 12 (Following bootstrap grid)
    var pageLayout = {
        "home": [0, 12, 0],
        "patient": [0, 9, 3],
        "episode": [0, 9, 3],
        "pathway": [0, 12, 0],
        "pathEditor": [3, 9, 0],
        "triggerEditor": [0,12, 0]
    };
    changePageLayout = function (page) {

        if (page in pageLayout) {
            $.each(layout, function (index, value) {
                if (pageLayout[page][index] == 0) {
                    $(value).hide();
                }
                else {
                    $(value).show();
                    $(value).removeClass();
                    //$(value)[0].className = $(value)[0].className.replace(/(\s)*(col-md-.*?)(?=\s)/g, "col-md-"+pageLayout[page][index]);
                    $(value).addClass("content col-md-"+pageLayout[page][index]);
                }
            });
        }
        else
            return;//"#f2c313";
    };

    var showPage = function (user, customer, userAuth) {
        if ((document.cookie && !currentContext.get('userAuth')) || (user && !currentContext.get('user'))) {
            currentContext.autoSetUser(user, customer, userAuth, Login);
        } else {
            if (CheckLogin()) {
                console.log('showing page ' + currentContext.get('page'));
                changePageLayout(currentContext.get('page'));
                /* do more stuff here */
                window.scrollTo(0, 0);
		return true;
            } else {
                console.log('trying to log in');
            }
        }
	return false;
    };

    var AppRouter = Backbone.Router.extend({
        routes: {
            "logout": 'logout',
            "settings": 'settings',
            "(login/:user/:customer/)(:userAuth)": 'showHome',
            "patient/:id(/login/:user/:customer/)(:userAuth)": 'showPatient',
            "episode/:id/patient/:id/:date(/login/:user/:customer/)(:userAuth)": 'showEpisode',
            "evidence/:id/patient/:id/evi/:id(/login/:user/:customer/)(:userAuth)": 'showEvidence',
            "pathway/:id/node/:id(/patient/:id/:date)(/login/:user/:customer/)(:userAuth)": 'showPathway',
            "pathwayeditor/:id/node/:id(/login/:user/:customer/)(:userAuth)": 'EditPathway',
            "triggereditor/:id/node/:id(/login/:user/:customer/)(:userAuth)": 'EditTriggers',
	    "password/:type/:user/:customer/:oauth": 'password',
            //default
            '*action': 'defaultAction',
        },
	password: function (type, user, customer, oauth) {
	    if (currentContext.get('userAuth')) {
		window.location = '#';
	    } else {
		currentContext.set({'loginTemplate': type+'.html', 'user':user, 'customer_id':customer, 'oauth':oauth});
		new Login({el: '#login-modal'});
	    }
	},
        showHome: function (user, customer, userAuth) {
            /* remove the current patient list, encounter, etc to revert the view to the doctor's user page */
            currentContext.set({page: 'home', patients: null, encounter: null, patientName: null});

            //TODO This is only for Demo purpose
            if(currentContext.get('official_name') == 'Heathcliff Huxtable'){
                currentContext.set({page: 'pathway', patients: null, encounter: null, patientName: null});
            }

            showPage(user, customer, userAuth);
        },
        showPatient: function (patid, user, customer, userAuth) {
            currentContext.set({page: 'patient', encounter: null, patients: patid});
            showPage(user, customer, userAuth);
        },
        showEpisode: function (enc, pat, date, user, customer, userAuth) {
            currentContext.set({page: 'episode', encounter: enc, patients: pat, enc_date: date,
                startdate: null, enddate: null});
            showPage(user, customer, userAuth);
        },
        showPathway: function (path, code, pat, date, user, customer, userAuth) {
            layoutModel.set({'fluidContent': false})
            var delimit = code.search('_')
            var nextcode = null
            if (delimit>0) {
                nextcode = code.slice(delimit+1)
                code = code.slice(0,delimit)
            }
            currentContext.set({page: 'pathway', code: code, nextcode: nextcode, pathid: path, patients: pat, enc_date: date,
                                startdate: null, enddate: null});

            showPage(user, customer, userAuth);
        },
        showEvidence: function (enc, pat, evi, user, customer, userAuth) {
            currentContext.set({page: 'episode', encounter: enc, patients: pat});
	    if(showPage(user, customer, userAuth)) {
                var evidence = new Evidence({'evi': evi});
                //$('#evidence-' + evi).modal();
            }
        },
        EditPathway: function (path, code, user, customer, userAuth) {
            layoutModel.set('fluidContent', true)
            currentContext.set({page: 'pathEditor',  pathid: path, code: code, nextcode: null});
            showPage(user, customer, userAuth);
        },
        EditTriggers: function (path, code, user, customer, userAuth) {
            layoutModel.set('fluidContent', false)
            currentContext.set({page: 'triggerEditor',  pathid: path, code: code});
            showPage(user, customer, userAuth);
        },
        showPathwayHistory: function (path, code, user, customer, userAuth) {
            currentContext.set({page: 'pathHistory',  pathid: path, code: code});
            showPage(user, customer, userAuth);
        },
        logout: function () {
	    eraseCookie('valid-through')
	    eraseCookie('roles')
	    eraseCookie('username')
	    var max=10;
	    while(document.cookie && max>0) {
		max = max-1
		eraseCookie(document.cookie.split('=')[0]);
	    }
            currentContext.clear({silent: true});
	    $.ajax({type: 'POST',dataType: 'json',url: "/logout"})
            location.href = "/index.html";
        },
        defaultAction: function (action) {
            console.log('No route:', action);
        },
        initialize: function () {
            //ajaxPrefilter
            $.ajaxPrefilter(function (options, originalOptions, jqXHR) {
                options.url = 'services' + options.url;
            });
            Backbone.history.start();
        }
    });

    return AppRouter;
});
