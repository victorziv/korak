var zebra;
var zebraCloseDefault = 3000;
var zebraCloseDefaultError = 5000;
var GRID_POLL_INTERVAL = 5000;
// __________________________________

function initGridResize(grid_container, grid, pager) {
    jQuery(window).resize(function() {
        var width = grid_container.width();
        grid.setGridWidth(width, true);
        pager.setGridWidth(width, true);
    });
}
//________________________________________


function resetAddMachineDialog() {
    var machine_serial_input = jQuery('#machine_serial');
    machine_serial_input.val('');
    machine_serial_input.attr("placeholder", "Machine S/N");
    jQuery("#machine_serial_group").removeClass("has-error");
    jQuery("#weekends_duedate").iCheck('uncheck');
}
// ______________________________

function localDateFormatter(cellvalue, options, rowObject) {
    if (  cellvalue ) {
        return moment(cellvalue).format('YYYY-MM-DD')
    }

    return ''
}
// ______________________________

function localDateTimeFormatter(cellvalue, options, rowObject) {
    if (  cellvalue ) {
        return moment(cellvalue).format('YYYY-MM-DD HH:mm:ss')
    }

    return ''
}
// ______________________________

function infinibookUrlFormatter(cellvalue, options, ro) {
    if ( ! cellvalue ) {
        return '';
    }
    var user_icon = '';

    if ( ro.owner_socialid ) {
        user_icon = '<i class="fa fa-user fa-3x">';
    } else {
        user_icon = '<i class="fa fa-user-secret fa-3x">';
    }
    var href = '<a href="http://infinibook/view/' + ro.owner_email + '/" target="_blank">'+ user_icon + ' ' + ro.owner_name + '</i></a>'; 
    return '<html>'+href+'</html>';
}
//________________________________________


function jiraBrowseUrlFormatter(cellvalue, options, rowObject) {
    if ( ! cellvalue ) {
        return '';
    }

    var href = '<a href="http://jira/browse/' + cellvalue + '/" target="_blank"><i class="fa fa-ticket fa-3x"> ' + cellvalue + '</i></a>'; 

    return '<html>'+href+'</html>'
}
//________________________________________

function logUrlFormatter(cellvalue, options, rowObject) {
    if ( ! cellvalue ) {
        return '';
    }

    var href = '<a href="/task/log/?path='+cellvalue+'" target="_blank"><i class="fa fa-file-text-o fa-3x"></i></a>'; 
    return '<html>'+href+'</html>'
}
//________________________________________

function notifyError(msg,onCloseCallback, auto_close) {
    auto_close = (typeof auto_close === "undefined") ? zebraCloseDefaultError : auto_close;
    new jQuery.Zebra_Dialog( msg,
        {
            buttons:  false,
            modal: false,
            type : 'error',
            title : '<strong>Error!</strong>',
            position: ['right - 20', 'top + 70'],
            onClose: onCloseCallback,
            auto_close : auto_close,
        }
    );
}
// __________________________________

function notifyWarning(msg,onCloseCallback, auto_close) {
    auto_close = (typeof auto_close === "undefined") ? zebraCloseDefault : auto_close;
    new jQuery.Zebra_Dialog( msg,
        {
            buttons:  false,
            modal: false,
            type : 'warning',
            title : '<strong>Warning!</strong>',
            position: ['right - 20', 'top + 70'],
            onClose: onCloseCallback,
            auto_close : auto_close,
        }
    );
}

// __________________________________

function notifySuccess(msg,onCloseCallback, auto_close) {
    auto_close = (typeof auto_close === "undefined") ? zebraCloseDefault : auto_close;
    new jQuery.Zebra_Dialog( msg,
        {
            buttons:  false,
            modal: false,
            type : 'confirmation',
            title : '<strong>Success!</strong>',
            position: ['right - 20', 'top + 70'],
            onClose: onCloseCallback,
            auto_close : auto_close,
        }
    );
}
// __________________________________

function confirmAction(msg, action_callback, callback_param ) {
    var dlg = new BootstrapDialog(
        {
            type: BootstrapDialog.TYPE_WARNING,
            size: BootstrapDialog.SIZE_MEDIUM,
            title: '<H3>Are you sure?</H3>',
            draggable: true,
            message: '<H4>'+msg+'</H4>',
            closable: true,
            buttons : [
                {
                   label: 'Go',
                   action: function(dialogRef){
                       action_callback(callback_param);
                       dialogRef.close();
                   }
                },
                {
                   label: 'Cancel',
                   action: function(dialogRef){
                       dialogRef.close();
                   }
                },
            ]
        }
    );

    dlg.open();
}
// __________________________________

function startWait(msg) {

    if (! msg) {
        msg = "Please wait...";
    }

    zebra = new jQuery.Zebra_Dialog( msg,
        {
            buttons:  false,
            modal: true,
            type : 'information',
            title : false,
            position: ['right - 20', 'top + 70'],
            show_close_button: false,
            custom_class : 'custom_zebra_class' 
        }
    );
}
// __________________________________

function stopWait() {
    zebra.close();
}

// __________________________________

function initCheckbox() {

    jQuery('input.flat').iCheck({
        checkboxClass: 'icheckbox_flat-green',
        radioClass: 'iradio_flat-green'
    });
}
// ______________________________

initCheckbox();

