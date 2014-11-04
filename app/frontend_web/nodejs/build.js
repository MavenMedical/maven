({
    mainConfigFile : "../www_modular/js/main.js",
    baseUrl : "../www_modular/js",
    name: "main",
    out: "../www_modular/js/min.js",
    removeCombined: true,
    findNestedDependencies: true,
    generateSourceMaps: true,
    preserveLicenseComments: false,
    optimize: 'uglify2',
    paths: 
    {
        'jsplumb':'empty:',
        'bootstrap':'empty:',
        'jquery':'empty:',
        'jquery_ui':'empty:',
	'underscore':'empty:',
	'backbone':'empty:',
	'ckeditor':'empty:',
	'amcharts':'empty:',
	'bootstrapswitch':'empty:',
	'/services/recaptcha': 'empty:'
    },
    shim: {
        bootstrap :{
            deps: ['jquery']
        },
        jsplumb :{
          deps: ['jquery','jquery_ui']
        },
        fullCalendar :{
            deps: ['jquery','moment', 'jquery_ui']
        },
	jquery_ui: {
	    deps: ['jquery'],
	},
	amchartspie: { deps: ['amcharts'], exports: 'AmCharts', init: function() {AmCharts.isReady = true;}},
	amchartsserial: { deps: ['amcharts'], exports: 'AmCharts', init: function() {AmCharts.isReady = true;}},
	amchartslight: { deps: ['amcharts'], exports: 'AmCharts', init: function() {AmCharts.isReady = true;}},
    },
    inlineText: true,
    exclude: [
	'libs/amcharts/serial',
	'libs/fullCalendar/fullcalendar.min',
	'libs/fullCalendar/moment.min'
    ],
    include: [
	'pathway/modalViews/ruleWizard',
	'pathway/modalViews/sendProtocol',
	'pathway/modalViews/editNode',
	'pathway/modalViews/sendFollowups',
	'pathway/modalViews/detailEditor_archaic',
	'pathway/modalViews/nodeEditor',
	'pathway/modalViews/newPathway',
	'pathway/modalViews/detailEditor',
	'pathway/modalViews/sidePanelEditor',
	'pathway/modalViews/DeleteDialog',
	'pathway/modalViews/protocolEditor',
	'pathway/internalViews/detailSelector',
	'pathway/internalViews/detailSearchBox',
	'pathway/internalViews/triggerNode',
	'pathway/internalViews/treeNodeActionSet',
	'pathway/internalViews/treeNode',
	'pathway/internalViews/protocolNode',
	'pathway/internalViews/detailGroup',
	'pathway/internalViews/detailListBox',
	'pathway/internalViews/multiSelectSearch',
	'pathway/Helpers',
	'pathway/singleRows/pathRow',
	'pathway/models/treeModel',
	'pathway/models/nodeModel',
	'pathway/models/pathwayCollection',
	'globalmodels/summaryModel',
	'globalmodels/patientModel',
	'globalmodels/spendingModel',
	'globalmodels/orderCollection',
	'globalmodels/customerCollection',
	'globalmodels/scrollCollection',
	'globalmodels/auditCollection',
	'globalmodels/patientCollection',
	'globalmodels/userCollection',
	'globalmodels/histogramModel',
	'globalmodels/contextModel',
	'globalmodels/alertCollection',
	'widgets/welcome',
	'widgets/patientSearch',
	'widgets/datepicker-calendar',
	'widgets/patientList',
	'widgets/customerCreation',
	'widgets/providerProfile',
	'widgets/userList',
	'widgets/login',
	'widgets/evidence',
	'widgets/encounterSummary',
	'widgets/auditList',
	'widgets/costtable',
	'widgets/customerList',
	'widgets/costdonut',
	'widgets/patientInfo',
	'widgets/alertList',
	'widgets/widgetModal',
	'widgets/spend_histogram',
	'widgets/maveninfo',
	'widgets/adminSettings',
	'widgets/pathway',
	'widgets/datepicker-chart',
	'widgets/settings',
	'widgets/topBanner',
	'widgets/orderList',
	'widgets/pathway/toolbar.js',
	'widgets/pathway/TreeView.js',
	'Helpers',
	'singleRow/customerRow',
	'singleRow/userRow',
	'singleRow/orderRow',
	'singleRow/auditRow',
	'singleRow/alertRow',
	'singleRow/reminderRow',
	'singleRow/patientRow',
	'text'

    ]
})