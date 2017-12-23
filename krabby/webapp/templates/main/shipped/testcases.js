"use strict";
{% include "common.js" %}
// ______________________________

var testcases_grid = jQuery("#testcases_grid");
// ______________________________


testcases_grid.jqGrid({

    mtype: "GET",
    cache : false,
    async: true,
    datatype: "json",

    url: "{{ config.API_URL_PREFIX }}/testcases/",

    jsonReader : { 
        root: "testcases",
        page: "currpage",
        total: "totalpages",
        records: "totalrecords",
        repeatitems: false,
        id: "caseid"
    },

    {% include "main/testcases/testcases_colmodel.js" %}

    rowNum:10,
    rowList:[10,20,30,40,50,100],
    pager: '#testcases_grid_pager',
    viewrecords: true,
    height: '100%',
    autowidth: true,
    shrinkToFit: true,
    gridview: true,
    autoResize: true,

    guiStyle: "bootstrap",
    iconSet: "fontAwesome",
    caption: "IVT Testcases",
    rownumbers: false,
    sortname: "name",
    sortorder: "asc"
});
//________________________________________

testcases_grid.jqGrid('navGrid','#testcases_grid_pager',

    {edit:false,add:false,del:false,search:false, view:false, refresh:true },

        {}, {}, {}, {}, {}

).navSeparatorAdd("#testcases_grid_pager");
//________________________________________

