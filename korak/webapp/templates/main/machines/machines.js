"use strict";
{% include "common.js" %}
// ______________________________

var machines_grid = jQuery("#machines_grid");
// ______________________________

function showAddMachineDialog() {
    jQuery('#modal_add_machine').modal('show'); 
}
// ______________________________


//function init_machine_add_modal() {
//    alert("Init modal");
//    modal_add_machine = jQuery('#modal_add_machine');
//    modal_add_machine.modal({
//        show: false,
//        keyboard: true,
//    });

//    modal_add_machine.draggable({
//        handle: ".modal-header",
//        cursor: "move"
//    });

//    modal_add_machine.draggable({
//        handle: ".modal-header",
//        cursor: "move"
//    });

//    jQuery("#btn_machine_add_submit").on('click', submitMachineAdd);
//    modal_add_machine.on('keydown', function(evt) {
//        if (evt.which === 13) {
//            submitMachineAdd();
//        }
//    });

//    modal_add_machine.on('show.bs.modal', function () {
//        jQuery('#modal_body_add_machine').css('width', '100%');
//        jQuery('#modal_body_add_machine').css('height', 'auto');
//    })
//}

// ______________________________

//function submitMachineAdd() {
//    alert('bla');
//    console.log("Fetching SN");
//    var sn = JQuery("#machine_serial").val();
//    console.log("SN: " + sn);
//    jQuery('#modal_add_machine').modal('hide'); 
//    var aj = jQuery.ajax({
//        type: "POST",
//        url: "{{ config.API_URL_PREFIX }}/machines/",
//        data: JSON.stringify({ 'sn' : sn }),
//        contentType: "application/json",
//        dataType: "json",
//        async: true,

//        beforeSend: function() {
//            startWait("Adding a new system...");
//        },
//    });

//    aj.done(function( data, textStatus, obj ) {
//        notifySuccess("Infinibox system has been added successfully!");
//        machines_grid.trigger("reloadGrid");

//    });

//    aj.always(function() {
//        stopWait();
//    });

//    aj.fail(function( xtr, textStatus, errorThrown ) {
//        notifyError(xtr.responseText);
//    });

//}
// ______________________________

machines_grid.jqGrid({

    mtype: "GET",
    cache : false,
    async: true,
    datatype: "json",

    url: "{{ config.API_URL_PREFIX }}/machines/",

    jsonReader : { 
        root: "machines",
        page: "currpage",
        total: "totalpages",
        records: "totalrecords",
        repeatitems: false,
        id: "machineid"
    },

    {% include "main/machines/machines_colmodel.js" %}

    rowNum:10,
    rowList:[10,20,30,40,50,100],
    pager: '#machines_grid_pager',
    viewrecords: true,
    height: '100%',
    autowidth: true,
    shrinkToFit: true,

    guiStyle: "bootstrap",
    iconSet: "fontAwesome",
    caption: "Infinidat Machines",
    rownumbers: false,
    sortname: "machine_name",
    sortorder: "asc"
});
//________________________________________

machines_grid.jqGrid('navGrid','#machines_grid_pager',

    {edit:false,add:false,del:false,search:false, view:false, refresh:true },

        {}, {}, {}, {}, {}

).navSeparatorAdd("#machines_grid_pager");
//________________________________________


var options = {
        caption: "",
        buttonicon: "glyphicon glyphicon-plus",
        title: "Add Machine",
        position: 'first',
        onClickButton: showAddMachineDialog
} 

machines_grid.jqGrid('navGrid', '#machines_grid_pager').jqGrid('navButtonAdd',"#machines_grid_pager", options);
init_machine_add_modal();
//________________________________________
