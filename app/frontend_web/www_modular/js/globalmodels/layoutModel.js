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




    var layoutModel;



    var LayoutModel = Backbone.Model.extend({
	    defaults: {
            fluidContent: false,
            contentHeight: '400px'

        },
        applicationFunctions: new Backbone.Model({
          'fluidContent': function(n){
              if (n){
                    $('#contentContainer').addClass('container-fluid')
                    $('#contentContainer').removeClass('container')
                } else {
                    $('#contentContainer').removeClass('container-fluid')
                    $('#contentContainer').addClass('container')
                }
          },
          'contentHeight': function(n){
            $('#contentContainer').css({'height': n})

          }

        }),
        initialize: function(){
            this.on('change', function(){
                this.apply()
            }, this )
        },
        apply: function(setToApply){
            if (setToApply){
                for (var i in setToApply){
                    var cur = setToApply[i]
                    this.applicationFunctions.get(cur)(this.get(cur))
                }
            } else {
                for (var i in _.keys(this.attributes)){
                    var cur = _.keys(this.attributes)[i]
                    this.applicationFunctions.get(cur)(this.get(cur))
                }

            }


        }



    });

    layoutModel = new LayoutModel;
    
    return layoutModel;
});
