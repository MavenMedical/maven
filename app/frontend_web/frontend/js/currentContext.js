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

], function () {

    var currentContext = (function () {
        var context = {};
        context.page = null;
        context.user = 'tom';
        context.patients = '';
	context.patient_name = '';
        context.key = '1U6BAcMeDWIN5_MyUd971tUU8jUk3F_R';
        context.provider = null;
        context.encounter = null;
        context.department = null;
        context.alert = null;

        return context;
    }());

    return currentContext;

});














