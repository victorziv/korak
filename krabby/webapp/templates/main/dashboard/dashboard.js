"use strict";
{% include "common.js" %}
var ivts_grid = jQuery("#dashboard_grid")
// ______________________________

ivts_grid.jqGrid({

    mtype: "GET",
    cache : false,
    async: true,
    datatype: "json",

    url: "{{ config.API_URL_PREFIX }}/dashboard/",

    jsonReader : { 
        root: "ivts",
        page: "currpage",
        total: "totalpages",
        records: "totalrecords",
        repeatitems: false,
        id: "id"
    },

    {% include "main/dashboard/dashboard_colmodel.js" %}

    rowNum:10,
    rowList:[10,20,30,40,50,100],
    pager: '#dashboard_grid_pager',
    viewrecords: true,
    height: '100%',
    autowidth: true,
    shrinkToFit: true,

    guiStyle: "bootstrap",
    iconSet: "fontAwesome",
    caption: "IVT Systems",
    rownumbers: false,
    sortname: "started",
    sortorder: "desc"
});
//________________________________________

ivts_grid.jqGrid('navGrid','#ivts_grid_pager',

    {edit:false,add:false,del:false,search:false, view:false, refresh:true },

        {}, {}, {}, {}, {}

).navSeparatorAdd("#ivts_grid_pager");
//________________________________________


//ivts_grid.jqGrid('navGrid', '#ivts_grid_pager').jqGrid('navButtonAdd',"#ivts_grid_pager", options);
//________________________________________
