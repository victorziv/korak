var session_task_grid_container = jQuery("#session_task_grid_container"); 
var DONE_STATES = ['finished', 'aborted', 'terminated', 'paused', 'skipped'];
//___________________________________

function initSessionTask() {
    setActionButtonsState();
}
//___________________________________

function pollTaskStateChange(taskid, state) {

    var aj = jQuery.ajax({
        type: "GET",
        url: "{{ config.API_URL_PREFIX }}/verification/session/tasks/"+taskid+"/current_state/"+state,
        contentType: "application/json",
        dataType: "json",
        async: true,
        beforeSend: function() { },
    });

    aj.done(function( data, textStatus, obj ) {

        if ( data.state_changed ) {

            if (data.state == 'running') {
                session_task_grid.jqGrid('setRowData', data.taskid, false, "verification_running");
            }

            if (data.state == 'onhold') {
                session_task_grid.jqGrid('setRowData', data.taskid, false, "verification_onhold");
            }

            session_task_grid.trigger('reloadGrid');

            var sessionid = session_task_grid.getRowData(data.taskid).sessionid;
            console.log("Task state changed on session " + sessionid);
            updateSessionState(sessionid);
        }
        
        if ( jQuery.inArray(data.state, DONE_STATES) > -1 ) {
            session_task_grid.trigger('reloadGrid');
            return false;
        }

        setTimeout(function() { pollTaskStateChange(data.taskid, data.state) }, GRID_POLL_INTERVAL);
    });

    aj.always(function() {});

    aj.fail(function( xtr, textStatus, errorThrown ) {
        notifyError(JSON.parse(xtr.responseText).message);
    });
}
//___________________________________

function queueTask(task) {
    var aj = jQuery.ajax({
        type: "POST",
        url: "{{ config.API_URL_PREFIX }}/verification/session/task/queue",
        contentType: "application/json",
        dataType: "json",
        data: JSON.stringify({task: task}),
        async: true,

        beforeSend: function() { },
    });

    aj.done(function( data, textStatus, obj ) {
//        updateTaskState(data.taskid, data.state);
        pollTaskStateChange(data.taskid, data.state);
        notifySuccess("Task <i>" + data.taskname + "</i> has been queued for execution!");
    });

    aj.always(function() {
        session_task_grid.trigger("reloadGrid");
    });

    aj.fail(function( xtr, textStatus, errorThrown ) {
        notifyError(JSON.parse(xtr.responseText).message);
    });

}
//___________________________________

function setActionButtonsState() {

//    var task_states = getTaskStates();
    jQuery("#btn_run_task").show();
    jQuery("#btn_stop_task").hide();
}
//___________________________________

function onStopTask(task) {
    var aj = jQuery.ajax({
        type: "POST",
        url: "{{ config.API_URL_PREFIX }}/verification/session/task/action/stop",
        contentType: "application/json",
        dataType: "json",
        data: JSON.stringify({task: task}),
        async: true,

        beforeSend: function() { },
    });

    aj.done(function( data, textStatus, obj ) {
        console.log("STOP task return task id : " + data.taskid);
        console.log("STOP task return task state : " + data.state);
        pollTaskStateChange(data.taskid, data.state);
        notifySuccess("Finishing " + data.taskname + "!");
    });

    aj.always(function() {
        session_task_grid.trigger("reloadGrid");
    });

    aj.fail(function( xtr, textStatus, errorThrown ) {
        notifyError(JSON.parse(xtr.responseText).message);
    });
}

//___________________________________

var task_action = {
    run: queueTask,
    stop: onStopTask
};
//___________________________________


function takeAction(taskid, action) {
    var sessionid = session_task_grid.getRowData(taskid).sessionid;
    var task = {
        system_name: session_grid.getRowData(sessionid).system_name,
        system_sn: session_grid.getRowData(sessionid).sn,
        session_task_name: session_task_grid.getRowData(taskid).taskname,
        session_taskid: taskid,
        sessionuid: session_grid.getRowData(sessionid).uid,
    }

    task_action[action](task);
}
//___________________________________

function onSubmitTaskRun(taskid) {
    jQuery("#btn_run_task").hide();
    jQuery("#btn_stop_task").show();
    takeAction(taskid, 'run')
}
// _________________________________________

function onSubmitTaskStop(taskid) {
    jQuery("#btn_stop_task").hide();
    jQuery("#btn_run_task").show();
    takeAction(taskid, 'stop')
}
// _________________________________________

function showTaskRunConfirmation() {
    var rowid = session_task_grid.jqGrid ('getGridParam', 'selrow');
    var task = session_task_grid.getRowData(rowid).taskname;
    console.log("Selected task to run: " + task);
    if (! rowid) {
        notifyWarning("No task was selected to run");
        return false;
    }

    confirmAction("Starting task <b>" + task + "</b>", onSubmitTaskRun, rowid);
}

// _________________________________

function showStopTaskConfirmation() {
    var rowid = session_task_grid.jqGrid ('getGridParam', 'selrow');
    var task = session_task_grid.getRowData(rowid).taskname;
    console.log("Selected task to stop: " + task);
    if (! rowid) {
        notifyWarning("No task was selected to stop");
        return false;
    }

    confirmAction("Terminating task <b>" + task + "</b>", onSubmitTaskStop, rowid);
}

// _________________________________

function showPauseTaskConfirmation() {
    alert("Pause");

}
// _________________________________

function showSkipTaskConfirmation() {
    alert("Pause");

}
// _________________________________

function updateSessionState(sessionid) {

    var aj = jQuery.ajax({
        type: "PUT",
        url: "{{ config.API_URL_PREFIX }}/verification/session/" + sessionid + "/state",
        contentType: "application/json",
        dataType: "json",
        async: true,
        beforeSend: function() {}
    });

    aj.done(function( data, textStatus, obj ) {

        if (data.state === 'running') {
            jQuery("#machines_verified_grid tr#"+sessionid).removeClass("verification_onhold");
            jQuery("#machines_verified_grid tr#"+sessionid).addClass("verification_running");
        } else if (data.state === 'onhold') {
            jQuery("#machines_verified_grid tr#"+sessionid).removeClass("verification_running");
            jQuery("#machines_verified_grid tr#"+sessionid).addClass("verification_onhold");
        } else {
            jQuery("#machines_verified_grid tr#"+sessionid).removeClass("verification_running");
            jQuery("#machines_verified_grid tr#"+sessionid).removeClass("verification_onhold");
        }

        session_grid.jqGrid('setCell', sessionid, 'state', data.state);
    });

    aj.always(function() {});

    aj.fail(function( xtr, textStatus, errorThrown ) {
        notifyError(xtr.responseText);
    });
}
// _____________________________________________

function viewTask(taskid, iRow, iCol, evt) {
    evt.preventDefault();
    var $self = jQuery(this);
    if ( taskid === null ) {
        var msg = "Please select a step to view!";
        notifyWarning(msg);
        return false;
    } 
    
//    window.location.href = "/machines/verification/session/step/"+taskid;
    notifySuccess("I am your step: " + taskid);
    return false;
}
//___________________________________

//function updateTaskState(taskid, state) {
//    console.log(taskid);
//    console.log(state);
//    session_task_grid.jqGrid('setCell', taskid, 'state', state);
//}
// ===============================


session_task_grid.jqGrid({
    jsonReader : { 
        root: "tasks",
        page: "currpage",
        total: "totalpages",
        records: "totalrecords",
        repeatitems: false,
        id: "id"
    },

    {% include "main/verified/session_task_colmodel.js" %}

    rowNum:20,
    rowList:[10,20,30,40,50],
    pager: '#session_task_grid_pager',
    viewrecords: true,
    height: '100%',
//    ondblClickRow: viewSessionStep,
    autowidth: true,
    shrinkToFit: true,
    caption:"Verification Session Steps",
    rownumbers: false,
    sortname: 'execution_order',
    sortorder: "asc",
    
    inlineEditing: {
        keys: true,
        defaultFocusField: "state",
        focusField: "state"
    },
    
    cmTemplate: { autoResizable: true },
    autoResizing: { compact: true },
    autoencode: true,
    loadComplete: function() {
        var $self = jQuery(this);
        var ids = $self.getDataIDs();
        for (i=0;i<ids.length;i++) {
            var row = session_task_grid.jqGrid('getRowData', ids[i]);

            if (row.state === 'running') {
                session_task_grid.jqGrid('setRowData', ids[i], false, "verification_running");
            }

            if (row.state === 'onhold') {
                session_task_grid.jqGrid('setRowData', ids[i], false, "verification_onhold");
            }
        }
    },

     actionsNavOptions: {
            delbutton: false,
            editbutton: false,
            runTaskicon: "fa-play",
            runTasktitle: "Run Task",
            stopTaskicon: "fa-stop",
            stopTasktitle: "Stop Task",

            isDisplayButtons: function (options, rowData) {
                if (options.rowData.state === 'running') {
                    return {
                        runTask: {display: false},
                        stopTask: {display: true},
                    };

                } else if (options.rowData.state === 'pending') {
                    return {
                        runTask: {display: true},
                        stopTask: {display: false},
                    };
                } else if (options.rowData.state === 'onhold') {
                    return {
                        runTask: {display: true},
                        stopTask: {display: false}
                    };
                } else if (options.rowData.state === 'queued') {
                    return {
                        runTask: {display: false},
                        stopTask: {display: true}
                    };
                } else if (jQuery.inArray(options.rowData.state, DONE_STATES) > -1 ) {
                    return {
                        runTask: {display: true},
                        stopTask: {display: false}
                    };
                }
            },
            custom: [
                { 
                    action: "runTask",
                    position: "first",
                    onClick: function (options) {
                        var action = 'run';
                        takeAction(options.rowid, action);
                    }
                },
                {
                    action: "stopTask",
                    position: "first",
                    onClick: function (options) {
                        var action = 'stop';
                        takeAction(options.rowid, action);
                    }
                },
            ]
        }

}).jqGrid("gridResize");

session_task_grid.jqGrid('setGridWidth', session_task_grid_container.width(), true);
session_task_grid.jqGrid(
    'navGrid',
    '#session_task_grid_pager',
    {edit:false,add:false,del:false,search:false, view:false, refresh:true }
).navSeparatorAdd("#session_task_grid_pager");
//________________________________________

//var options = {
//        caption: "",
//        buttonicon: "fa fa-thumbs-down",
//        title: "Skip Task",
//        position: 'first',
//        onClickButton: showSkipConfirmation
//} 

//session_task_grid.jqGrid(
//    'navGrid', '#session_task_grid_pager').jqGrid('navButtonAdd',"#session_task_grid_pager", options);

//var options = {
//        caption: "",
//        buttonicon: "fa fa-stop",
//        title: "Stop task",
//        position: 'first',
//        id: "btn_stop_task",
//        onClickButton: showStopTaskConfirmation
//} 

//session_task_grid.jqGrid(
//    'navGrid', '#session_task_grid_pager').jqGrid('navButtonAdd',"#session_task_grid_pager", options);

//var options = {
//        caption: "",
//        buttonicon: "fa fa-pause",
//        title: "Pause Task",
//        position: 'first',
//        onClickButton: showPauseConfirmation
//} 

//session_task_grid.jqGrid(
//    'navGrid', '#session_task_grid_pager').jqGrid('navButtonAdd',"#session_task_grid_pager", options);


//var options = {
//        caption: "",
//        buttonicon: "fa fa-play",
//        title: "Run task",
//        position: 'first',
//        id: "btn_run_task",
//        onClickButton: showTaskRunConfirmation
//} 

//session_task_grid.jqGrid(
//    'navGrid', '#session_task_grid_pager').jqGrid('navButtonAdd',"#session_task_grid_pager", options);

//________________________________________

initSessionTask();

var session_task_grid_pager = jQuery("#session_task_grid_pager");
session_task_grid.jqGrid('setGridWidth', session_task_grid_container.width(), true);
initGridResize(session_task_grid_container, session_task_grid, session_task_grid_pager);
