/**
 * Created by Asmaa Aljuhani on 3/11/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'globalmodels/contextModel', // current patient (if any)
], function ($, _, Backbone, contextModel) {
    //A model representing the state of groups, connected to the database
    var GroupsModel = Backbone.Model.extend({
        //this is the url for syncing this model with the server
        URL: '/EMAIL_GROUP',
        //When the server gives us info in JSON form this is how we put in Backbone Model form,
        parse: function(JSON){

        },
        //when we send data to the server turn the data in the Backbone Model into the JSON to sync
        toJSON: function(){
               var convertedAttribs = this.attributes
               //if nessecary, the code to turn the attributes into valid json goes here


                return convertedAttribs
        }


    })

    var GroupManager = Backbone.View.extend({

       initialize: function(){

           //create a model which will match the server
           this.model = new GroupsModel()
           //fetch the data from the server
           this.model.fetch()

           //If the model changes, which this view will do, sync with the server
           this.model.on('change', this.model.save)
           //Whenever we sync with the server, rerender the view
           this.model.on('sync', this.render)


       },
       render: function(){
            //Everything nessecary to display the current state of the model goes here as well as event handlers to
            //change it
           

       }
    });
    return GroupManager;

});
