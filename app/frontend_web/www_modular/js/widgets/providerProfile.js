/**
 * Created by Asmaa Aljuhani on 7/23/14.
 */

define([
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'globalmodels/contextModel',
    'widgets/pageOption',
], function ($, _, Backbone, contextModel, pageOption) {

    var Profile = Backbone.View.extend({
            initialize: function(arg){
                this.template = _.template(arg.template);
                this.render();
                 new pageOption({'Profile':['fa-user', 'profile']})
                this.showhide();
                contextModel.on('change:page', this.showhide , this)

            },
            events: {
                'keyup #official-name-input':'doentersave',
                'keyup #display-name-input':'doentersave',
                'keyup #new-password':'doenterchange',
                'click #change-password': 'dochangepassword',
                'click #save-settings': 'dosavesettings',
            },
        showhide: function(){
            if(contextModel.get('page') == 'profile'){
                this.$el.show();
            }else{
                this.$el.hide();
            }
        },
            render: function (){
                this.$el.html(this.template(contextModel.attributes));
            },
            doentersave: function(event){
                $("#settings-save-status").empty();
                if(event.keyCode == 13){
                    this.dosavesettings(event);
                }
            },
            dosavesettings: function(event) {
                var official_name = $("#official-name-input").val();
                var display_name = $("#display-name-input").val();

                $.ajax({
                    url: "/save_user_settings",
                    data:$.param(contextModel.toParams())+"&official_name="+official_name+"&display_name="+display_name,
                    success: function(data) {
                        console.log("Settings saved");
                        $("#settings-save-status").html("Settings Saved!");
                    },
                    error: function(xhr, textStatus, errorThrown){
                        console.log("Settings failed to save");
                        $("#settings-save-status").html("Sorry, an error occurred");
                    }
            });
        },
        dochangepassword: function() {
            if (this.newPasswordChange()){
                console.log("saving new password")
            }
        },
        doenterchange: function(event){
            if(event.keyCode == 13){
                this.dochangepassword();
            } else {
                this.newPasswordChange();
            }
	    },
        newPasswordChange: function() {
            var newpw = $("#new-password").val();
            var check = "<big><big><font color='#00b000'>&#x2714</font></big></big>";
            var X = "<big><font color='#ff0000'>&#x2718</font></big>";
            var len = newpw.length<8;
            var low = newpw.search(".*[a-z]")<0;
            var up = newpw.search(".*[A-Z]")<0;
            var num = newpw.search(".*[0-9]")<0;
            var diff = newpw==$("#current-password").val();
            var diff2 = newpw!=$("#new-password2").val();
            $("#pw-len-cb").html(len?X:check);
            $("#pw-low-cb").html(low?X:check);
            $("#pw-up-cb").html(up?X:check);
            $("#pw-num-cb").html(num?X:check);
            $("#pw-diff-cb").html(diff?X:check);
            if(len || low || up || num || diff || diff2) {
            return false;
            } else {
            return true;
            }
	    }
    });
    return Profile;

});
