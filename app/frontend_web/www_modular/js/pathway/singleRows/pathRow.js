
/***************************************************************************
 * Copyright (c) 2014 - Maven Medical
 * AUTHOR: 'Tom DuBois'
 * DESCRIPTION: This Javascript file handle a hierarchy of rulelist view
 *              so we can handle events easier.
 *
 **************************************************************************/
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jqueryq
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'router',
    'globalmodels/contextModel',
    'pathway/models/pathwayCollection',
    'text!templates/pathway/pathwayListEntry.html',
    '../../widgets/pathway/historyList',
    'pathway/modalViews/renamePathway',

], function ($, _, Backbone, router, contextModel, pathwayCollection, pathRowTemplate, HistoryList, RenamePathway) {

    var ruleRow = Backbone.View.extend({
        tagName: "li class='dd-item pathrow-item dd2-item dd-collapsed'",
        template: _.template(pathRowTemplate),
        historyList: null,
        events:{
	      'click .select-button': 'handleSelect',
	      'click .show-hist': 'handleHistory',
	      'click .delete-button': 'handleRemove',
	      'click .pathway-checkbox': 'handleCheck',
	      'click .rename-pathway': 'handleRename',
	      'click .pathway-switch-label': 'handleToggle',
        },
        handleToggle: function(event){
            event.stopPropagation();
        },
        render: function(){
            $(this.el).html(this.template(this.model.toJSON()));
            this.model.url = "/list/" + this.model.get("canonical");

            var that = this;
            $(document).ready(function(){
                $('.pathway-enable', that.$el).click(function(event) {
                   // event.stopPropagation();
                    var state = false;
                    if (event.target.checked){
                        state = true;
                        $(event.target).attr('title','Disable Pathway');
                        $(".history-checkbox", this.$el).removeClass("check-disabled",0);
                    }
                    else {
                        $(event.target).attr('title','Enable Pathway');
                        $(".history-checkbox", this.$el).addClass("check-disabled",0);
                    }

                    that.model.save({active: state});
                });
             });
            return this;
        },
        initialize: function(params){
            this.model = params.model
            that = this;
            $(this.el).on("remove", function(){
               console.log("this pathway was removed");
            });
        },
        handleRename: function(event){
            event.stopPropagation();

            new RenamePathway({el: '#modal-target', canonical_id: this.model.get('canonical'), nameEl: $(".select-button",this.$el)});

        },
        handleSelect: function() {
            if (contextModel.get('code') == 'undefined') {
                if (contextModel.get('canonical') != this.model.get('canonical')){
                    contextModel.set('code', 'undefined', {silent: true});
                }
            }
            contextModel.set('canonical', String(this.model.get('canonical')))
            contextModel.set('pathid', String(this.model.get('id')))

            $(".active-pathway").removeClass("active-pathway");
            $(this.el).addClass("active-pathway")

            contextModel.unbind('change:pathid', this.updateCurPath);
            contextModel.on("change:pathid", this.updateCurPath, {that: this});
        },
        updateCurPath: function(event){
            if (contextModel.get('canonical') == this.that.model.get('canonical')) {
                this.that.model.set('id', contextModel.get('pathid'));
            }
            else {
                contextModel.unbind('change:pathid', this.that.updateCurPath);
            }
        },
        handleCheck: function(event){
            var active = false;
            if ($(event.target).hasClass("glyphicon-check")) {
                $(event.target).switchClass("glyphicon-check", "glyphicon-unchecked", 0);
                $(".history-checkbox", this.$el.parent()).addClass("check-disabled",0);
            }
            else {
                active = true;
                $(event.target).switchClass("glyphicon-unchecked", "glyphicon-check", 0);
                $(".history-checkbox", this.$el.parent()).removeClass("check-disabled",0);
            }
            //$(this.el).trigger("change");
            this.model.save({active: active});
        },
        handleHistory: function() {
            var pathwayHistory = $(".pathway-history-section", this.$el)
           // pathwayHistory.toggle();
            //if (pathwayHistory.is(":visible")){
                //hide all other history views
                //$(".pathway-history-section").not(pathwayHistory).hide();
                //if (pathwayHistory.is(":empty")) {
                    //only fetch history if not yet fetched
                    var extraData = {canonical: this.model.get('canonical')};
                    this.historyList = new HistoryList({el: pathwayHistory, currentPath: this.model.get('id'), extraData: extraData});
                    $(this.historyList.el).bind("change", {that: this}, this.updateActivePathway);
                //}
           // }
        },
        updateActivePathway: function(event) {
            event.data.model.set('id', event.data.that.historyList.currentPath);
        },
    	handleRemove: function() {
            var del = confirm("Are you sure you want to delete this pathway?");
            if (!del) return;
            this.model.destroy({success: function(){
                pathwayCollection.fetch()
            }})

            this.undelegateEvents(); // Unbind all local event bindings

            $(this.el).remove(); // Remove view from DOM

            delete this.$el; // Delete the jQuery wrapped object variable
            delete this.el; // Delete the variable reference to this node
    	}
    });

    return ruleRow;

});
