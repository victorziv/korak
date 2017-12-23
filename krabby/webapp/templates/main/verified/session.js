"use strict";

var session_grid = jQuery("#machines_verified_grid");
var session_task_grid = jQuery("#session_task_grid");
var selectedSessionID = "{{ sessionid }}";
// ______________________________

function  applyStateClass(grid_rows) {
    for (i=0;i<grid_rows.length;i++) {
        var rowid = grid_rows[i];
        var state = session_grid.getRowData(rowid).state;

        if (state === 'running') {
            session_grid.jqGrid('setRowData', rowid, false, "verification_running");
        }

        if (state === 'onhold') {
            session_grid.jqGrid('setRowData', rowid, false, "verification_onhold");
        }
    }
}
// ______________________________

function initVerifiedMachinesControls(grid) {
    jQuery("#add_machine_session").on('click', showAddMachineDialog);
    jQuery("#delete_machine_session").on('click', showDeleteConfirmation);
    jQuery("#update_from_jira").on('click', showUpdateJiraConfirmation);
        
}
// ______________________________

function clearSelection() {
    session_task_grid.jqGrid("clearGridData", true).trigger("reloadGrid");
}
// ______________________________

function loadSessionTaskGrid(sessionid, selected) {

    var gridParams = { 
        url: "{{ config.API_URL_PREFIX }}/verification/" + sessionid + "/tasks/",
        page:1,
        postData: {sessionid:sessionid},
        datatype: 'json'

    };

    session_task_grid.setGridParam(gridParams);

    var machineName = session_grid.getRowData(sessionid).system_name;
    var verType = session_grid.getRowData(sessionid).verification_type;

    session_task_grid.setCaption('Verification Session ' + verType +' for ' + machineName);
    session_task_grid.trigger("reloadGrid");
    session_task_grid_container.show();
    session_task_grid.show();
}
// ==== ADD FUNCTIONS =====

function initMachineAddModal(grid) {
    modal_add_machine = jQuery('#modal_add_machine');
    modal_add_machine.modal({
        show: false,
        keyboard: true,
    });

    modal_add_machine.draggable({
        handle: ".modal-header",
        cursor: "move"
    });

    modal_add_machine.draggable({
        handle: ".modal-header",
        cursor: "move"
    });

    jQuery("#btn_machine_add_submit").on('click', function() { submitMachineAdd(grid)});
    modal_add_machine.on('keydown', function(evt) {
        if (evt.which === 13) {
            console.log('Enter pressed: ' + evt.which);
            submitMachineAdd(grid);
            return false;
        }
    });

    modal_add_machine.on('show.bs.modal', function () {
        jQuery('#modal_body_add_machine').css('width', '100%');
        jQuery('#modal_body_add_machine').css('height', 'auto');
    })

    modal_add_machine.on('shown.bs.modal', function () {
        jQuery('#machine_serial').focus();
    })

    modal_add_machine.on('hidden.bs.modal', function () {
        resetAddMachineDialog();
    })
}
// ______________________________

function submitMachineAdd(grid) {
    var machine_serial_input = jQuery("#machine_serial");
    var sn = machine_serial_input.val();
    console.log("SN: " + sn);
    if (! sn) {
        jQuery("#machine_serial_group").addClass("has-error");
        machine_serial_input.focus();
        machine_serial_input.attr("placeholder", "Machine S/N is required");
        return false;
    }

    var weekends_duedate = jQuery("#weekends_duedate");
    var duedate_include_weekends = false;
    if (weekends_duedate.is(':checked')) {
        duedate_include_weekends = true;
    }

    console.log("Weekends: " + duedate_include_weekends);
    jQuery('#modal_add_machine').modal('hide'); 

    var aj = jQuery.ajax({
        type: "POST",
        url: "{{ config.API_URL_PREFIX }}/verification/session/",
        data: JSON.stringify({ 'sn' : sn, 'duedate_include_weekends': duedate_include_weekends }),
        contentType: "application/json",
        dataType: "json",
        async: true,

        beforeSend: function() {
            startWait("Adding a new system...");
        },
    });

    aj.done(function( data, textStatus, obj ) {
        notifySuccess("System has been added successfully!");
        grid.trigger("reloadGrid");

    });

    aj.always(function() {
        stopWait();
        resetAddMachineDialog();
    });

    aj.fail(function( xtr, textStatus, errorThrown ) {
        var msg = JSON.parse(xtr.responseText).message;
        if (xtr.status === 409 && msg.toLowerCase().includes('in verification')) {
            notifyWarning(msg);
        } else {
            notifyError(msg);
        }
    });

}
// _____________________________________

function showAddMachineDialog() {
    jQuery('#modal_add_machine').modal('show'); 
}
// _____________________________________

// ==== ADD FUNCTIONS =====

// ==== EDIT FUNCTIONS =====

function showEditSessionDialog(evt) {
    var sessionid = session_grid.jqGrid ('getGridParam', 'selrow');
    if (! sessionid) {
        notifyWarning("No IBox system was selected for editing");
        return false;
    }
    var dlg = new BootstrapDialog(
        {
            type: BootstrapDialog.TYPE_PREMIUM,
            size: BootstrapDialog.SIZE_MEDIUM,
            title: '<H3>Edit Verification Session</H3>',
            draggable: true,
            message: jQuery('<div></div>').load('session/'+sessionid+'/edit'),
            closable: true,
            buttons : [
                {
                    label: 'Submit',
                    cssClass: 'btn-primary btn-round',
                    
                    action: function(dialogRef){
                        onSubmitEditSession();
                        dialogRef.close();
                   }
                },
                {
                    label: 'Cancel',
                    cssClass: 'btn-dark btn-round',
                    action: function(dialogRef){
                       dialogRef.close();
                    }
                },
            ]
        }
    );

    dlg.open();
}
// ______________________________

function onSubmitEditSession(sessionid) {

    var name = session_grid.getRowData(sessionid).system_name;

    var aj = jQuery.ajax({
        type: "PUT",
        url: "{{ config.API_URL_PREFIX }}/verification/session/" + sessionid + "/update/from/jira",
        contentType: "application/json",
        dataType: "json",
        async: true,

        beforeSend: function() {},
    });

    aj.done(function( data, textStatus, obj ) {
        var msg = "System  " + name + " has been updated!";
        session_grid.trigger("reloadGrid");
        notifySuccess(msg);
    });

    aj.always(function() {});

    aj.fail(function( xtr, textStatus, errorThrown ) {
        var msg = JSON.parse(xtr.responseText).message;
        notifyError(msg);
    });
}
// _________________________________________

// ====/EDIT FUNCTIONS =====

// === UPDATE FUNCTIONS ====


function onSubmitUpdate(sessionid) {

    var name = session_grid.getRowData(sessionid).system_name;

    var aj = jQuery.ajax({
        type: "PUT",
        url: "{{ config.API_URL_PREFIX }}/verification/session/" + sessionid + "/update/from/jira",
        contentType: "application/json",
        dataType: "json",
        async: true,

        beforeSend: function() {},
    });

    aj.done(function( data, textStatus, obj ) {
        var msg = "System  " + name + " has been updated!";
        session_grid.trigger("reloadGrid");
        notifySuccess(msg);
    });

    aj.always(function() {});

    aj.fail(function( xtr, textStatus, errorThrown ) {
        var msg = JSON.parse(xtr.responseText).message;
        notifyError(msg);
    });
}
// _________________________________________

function showUpdateJiraConfirmation() {
    var rowid = session_grid.jqGrid ('getGridParam', 'selrow');
    if (! rowid) {
        notifyWarning("No IBox system was selected for update from Jira");
        return false;
    }

    var name = session_grid.getRowData(rowid).system_name;
    var sessionuid = session_grid.getRowData(rowid).uid;

    confirmAction("Updating system " + name, onSubmitUpdate, rowid);
}
    
// === / UPDATE FUNCTIONS ====

// ======= DELETE Functions =============

function onSubmitDelete(machineid) {

    var name = session_grid.getRowData(machineid).system_name;

    var aj = jQuery.ajax({
        type: "DELETE",
        url: "{{ config.API_URL_PREFIX }}/machine/verified/" + machineid,
        contentType: "application/json",
        dataType: "json",
        async: true,

        beforeSend: function() {},
    });

    aj.done(function( data, textStatus, obj ) {
        var msg = "System  " + name + " has been removed from verification!";
        notifySuccess(msg);
    });

    aj.always(function() {
        session_grid.trigger("reloadGrid");
    });

    aj.fail(function( xtr, textStatus, errorThrown ) {
        var msg = JSON.parse(xtr.responseText).message;
        notifyError(msg);
    });
}
// _________________________________________

function showDeleteConfirmation() {
    var rowid = session_grid.jqGrid ('getGridParam', 'selrow');
    var name = session_grid.getRowData(rowid).system_name;
    if (! rowid) {
        notifyWarning("No IBox system was selected for deletion");
        return false;
    }

    confirmAction("Removing system " + name + " from verification", onSubmitDelete, rowid);
}
// ======= DELETE Functions =============

// ======= Session Run Functions =============

function onSubmitSessionRun(machineid) {
    notifyWarning("Sorry, not implemented yet!");
    return false;
}
// _________________________________________

function showRunSessionConfirmation() {
    var rowid = session_grid.jqGrid ('getGridParam', 'selrow');
    if (! rowid) {
        notifyWarning("No verification session was selected to run");
        return false;
    }

    confirmAction("Starting verification session", onSubmitSessionRun, rowid);
}
// ======= /Session Run Functions =============

session_grid.jqGrid({
    mtype: "GET",
    cache : false,
    async: true,
    datatype: "json",

    url: "{{ config.API_URL_PREFIX }}/verification/session/",

    jsonReader : { 
        root: "session",
        page: "currpage",
        total: "totalpages",
        records: "totalrecords",
        repeatitems: false,
        id: "id"
    },

    {% include "main/verified/session_colmodel.js" %}

    rowNum:10,
    rowList:[10,20,30,40,50,100],
    pager: '#machines_verified_grid_pager',
    viewrecords: true,
    height: '100%',
    autowidth: true,
    shrinkToFit: true,

    caption: "Systems In Verification",
    rownumbers: false,
    sortname: "due",
    sortorder: "desc",

    onSelectRow: function (rowid, selected) {
        if ( selected ) {
            loadSessionTaskGrid(rowid, selected);
        } else { 
            session_task_grid.jqGrid("clearGridData", true).trigger("reloadGrid");
            session_task_grid_container.hide();
            session_task_grid.hide();
        }
    },

    onSortCol : clearSelection,
    onPaging : clearSelection,

    loadComplete: function() {

       session_task_grid.hide();
       session_task_grid_container.hide();

        var grid_rows = session_grid.getDataIDs();
        if (grid_rows.length === 0) {
           return false;
        }

        applyStateClass(grid_rows);

//        var selectedRowID = null;
//        if (selectedSessionID === parseInt(selectedSessionID, 10) && selectedSessionID > 0) {
//            selectedRowID = selectedSessionID;
//        } else {
//            var last_record = session_grid.getDataIDs()[0];
//            selectedRowID = last_record;
//        }

//        var report_selected = function () { 
//            session_grid.setSelection(selectedRowID);
//        };

//        window.setTimeout(report_selected, 1000);
    }
});
//________________________________________


session_grid.jqGrid('navGrid','#machines_verified_grid_pager',

    {edit:false,add:false,del:false,search:false, view:false, refresh:true },

        {}, {}, {}, {}, {}

).navSeparatorAdd("#machines_verified_grid_pager");

//________________________________________

var options = {
        caption: "",
        buttonicon: "fa fa-download",
        title: "Update From Jira",
        position: 'first',
        onClickButton: showUpdateJiraConfirmation
} 

session_grid.jqGrid('navGrid', '#machines_verified_grid_pager').jqGrid(
    'navButtonAdd',"#machines_verified_grid_pager", options);
//________________________________________

var options = {
        caption: "",
        buttonicon: "fa fa-trash",
        title: "Delete Session",
        position: 'first',
        onClickButton: showDeleteConfirmation
} 

session_grid.jqGrid('navGrid', '#machines_verified_grid_pager').jqGrid(
    'navButtonAdd',"#machines_verified_grid_pager", options);
//________________________________________

var options = {
        caption: "",
        buttonicon: "fa fa-edit",
        title: "Edit Session",
        position: 'first',
        onClickButton: showEditSessionDialog
} 

session_grid.jqGrid('navGrid', '#machines_verified_grid_pager').jqGrid(
    'navButtonAdd',"#machines_verified_grid_pager", options);
//________________________________________

var options = {
        caption: "",
        buttonicon: "fa fa-plus",
        title: "Add Session",
        position: 'first',
        onClickButton: showAddMachineDialog
} 

session_grid.jqGrid('navGrid', '#machines_verified_grid_pager').jqGrid(
    'navButtonAdd',"#machines_verified_grid_pager", options);
//________________________________________


//var options = {
//        caption: "",
//        buttonicon: "fa fa-play",
//        title: "Run session",
//        position: 'first',
//        id: "btn_run_session",
//        onClickButton: showRunSessionConfirmation
//} 

//session_grid.jqGrid(
//    'navGrid', '#machines_verified_grid_pager').jqGrid('navButtonAdd',"#machines_verified_grid_pager", options);

//________________________________________

initMachineAddModal(session_grid);
initVerifiedMachinesControls(session_grid);
//________________________________________

var verified_grid_container = jQuery("#machines_verified_grid_container");
var verified_grid_pager = jQuery("#machines_verified_grid_pager");
session_grid.jqGrid('setGridWidth', verified_grid_container.width(), true);
initGridResize(verified_grid_container, session_grid, verified_grid_pager);
