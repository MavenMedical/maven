define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone

], function ($, _, Backbone) {

    var Helpers = {

        detailHeadings: {
            'enc_pl_dx': "Encounter or Problem List Diagnosis",
            'pl_dx': "Problem List Diagnosis",
            'hist_dx': "Historical Diagnosis",
            'lab': "Lab Results",
            'enc_dx': "Encounter Diagnosis",
            'hist_proc': "Historic Procedure",
            'enc_proc':"(unusued) Encounter Procedure",
            'ml_med' : "Medication List",
            'vitals': "Vital Signs",
            'vitals_bp': "Disjunctive Blood Pressure Detail"
        },
        detailDescriptions: {

            'enc_pl_dx' : "Specify a constraint based on a diagnosis that can be found either in the current encounter or on the patient’s problem list. This would represent a fairly comprehensive set of acute and chronic diagnoses that are likely to be currently active for the patient.",
            'pl_dx'     : "Specify a constraint based on a diagnosis in the patient’s problem list. The patient problem list is a patient-level section of the medical record that catalogs the most important diagnoses for the patient",
            'hist_dx'   : "Specify a constraint based on a diagnosis in the patient’s diagnostic history",
            'lab'       : "Specify a constraint based on the patient's lab results",
            'enc_dx'    : "Specify a constraint based on any diagnosis currently associated with the encounter such as chief complaints, differential diagnoses, or symptoms that have been discretely documented and transmitted to Maven. ",
            'hist_proc' : "Specify a constraint based on procedures that the patient has undergone in the past",
            'enc_proc'  : "(unusued) Encounter Procedure",
            'ml_med'    : "Specify a constraint based on medications that the patient is currently taking according to the medical record",
            'vitals'    : "Specify a constraint based on the patient's vitals",
            'vitals_bp' : "Specify a constraint based on the patient's blood pressure which allows for EITHER the systolic OR diastolic to be within a given range"
        },
        notDetail: ['id', 'treeInfo', 'evidence','genders', 'minAge', 'maxAge', 'name', 'triggers', 'triggerType', 'sources', 'detID', 'conflicts']
    };

    return Helpers;


});
