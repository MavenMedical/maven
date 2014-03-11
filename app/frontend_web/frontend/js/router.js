/**
 * Created by Asmaa Aljuhani on 3/11/14.
 */

define([
  'jquery',     // lib/jquery/jquery
  'underscore', // lib/underscore/underscore
  'backbone',    // lib/backbone/backbone,

    //views
    'views/sidemenu',
    'views/topnav',
    
    'views/home',
    'views/patient',
    'views/episode',
    'views/alerts'
], function($, _, Backbone, SideMenu, TopNav, HomeView, PatientView, EpisodeView, AlertsView){
    var AppRouter = Backbone.Router.extend({
        routes: {
            "": 'showHome',
            "patient" : 'showPatient',
            "alerts" : 'showAlerts',
            "episode": 'showEpisode',

            //default
            '*action':'defaultAction'
        }
    });

    var initialize = function(){
        var app_router = new AppRouter;

        // render side menu and topnav for all pages
            var sidemenu = new SideMenu;
            sidemenu.render();
            var topnav = new TopNav;
            topnav.render();

        app_router.on('route:showHome', function(){
            // Call render on the module we loaded in via the dependency array
            var homeView = new HomeView;
            homeView.render();
        });
        app_router.on('route:showPatient', function(){
              var patientView = new PatientView;
            patientView.render();

        });
        app_router.on('route:showAlerts', function(){
            var alertsView = new AlertsView;
            alertsView.render();
        });
        app_router.on('route:showEpisode', function(){
            var episodeView = new EpisodeView;
            episodeView.render();
        });
        app_router.on('defaultAction', function(actions){
           console.log('No route:', actions);
        });

        Backbone.history.start();
    };

  return {
      initialize: initialize
  };
});