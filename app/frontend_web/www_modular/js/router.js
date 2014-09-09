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
    'widgets/evidence',
    'widgets/login',
    'widgets/settings'
], function ($, _, Backbone, currentContext, Evidence, Login, Settings) {

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
        "home": [0, 9, 3],
        "patient": [0, 9, 3],
        "episode": [0, 9, 3],
        "pathway": [0, 9, 3],
        "pathEditor": [3, 6, 3],
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

    var showPage = function (provider, customer, userAuth) {
        if (provider && !currentContext.get('user')) {
            console.log('pre-authenticated login');
            currentContext.setProvider(provider, customer, userAuth);
        } else {
            if (CheckLogin()) {
                console.log('showing page ' + currentContext.get('page'));
                changePageLayout(currentContext.get('page'));
                /* do more stuff here */
                window.scrollTo(0, 0);
            } else {
                console.log('trying to log in');
            }
        }
    };

    var AppRouter = Backbone.Router.extend({
        routes: {
            "(login/:provider/:customer/:userAuth)": 'showHome',
            "patient/:id(/login/:provider/:customer/:userAuth)": 'showPatient',
            "episode/:id/patient/:id/:date(/login/:provider/:customer/:userAuth)": 'showEpisode',
            "evidence/:id/patient/:id/evi/:id(/login/:provider/:customer/:userAuth)": 'showEvidence',
            "pathway/:id/patient/:id/:date(/login/:provider/:customer/:userAuth)": 'showPathway',
            "pathway/:id/pathid/:id(/login/:provider/:customer/:userAuth)": 'EditPathway',
            "logout": 'logout',
            "settings": 'settings',
            //default
            '*action': 'defaultAction'
        },
        showHome: function (provider, customer, userAuth) {
            /* remove the current patient list, encounter, etc to revert the view to the doctor's user page */
            console.log(currentContext);
            currentContext.set({page: 'home', patients: null, encounter: null, patientName: null});

            //TODO This is only for Demo purpose
            if(currentContext.get('official_name') == 'Heathcliff Huxtable'){
                currentContext.set({page: 'pathEditor', patients: null, encounter: null, patientName: null});
            }

            showPage(provider, customer, userAuth);
        },
        showPatient: function (patid, provider, customer, userAuth) {
            currentContext.set({page: 'patient', encounter: null, patients: patid});
            showPage(provider, customer, userAuth);
        },
        showEpisode: function (enc, pat, date, provider, customer, userAuth) {
            currentContext.set({page: 'episode', encounter: enc, patients: pat, enc_date: date,
                startdate: null, enddate: null});
            showPage(provider, customer, userAuth);
        },
        showPathway: function (path, pat, date, provider, customer, userAuth) {
            currentContext.set({page: 'pathway', pathid: path, patients: pat, enc_date: date,
                startdate: null, enddate: null});
            showPage(provider, customer, userAuth);
        },
        showEvidence: function (enc, pat, evi, provider, customer, userAuth) {
            currentContext.set({page: 'episode', encounter: enc, patients: pat});
            if (provider && provider != currentContext.get('user')) {
                currentContext.setProvider(provider, customer, userAuth);
            } else {
                if (CheckLogin()) {
                    var evidence = new Evidence({'evi': evi});
                    //$('#evidence-' + evi).modal();
                }
            }
        },
        EditPathway: function (enc, path, provider, customer, userAuth) {
            currentContext.set({page: 'pathEditor', encounter: enc, pathid: path});
            showPage(provider, customer, userAuth);
        },
        logout: function () {
            currentContext.clear({silent: true});
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
