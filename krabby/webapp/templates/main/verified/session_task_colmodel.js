colModel: [
    {
        label: 'stepid',
        name: 'id',
        index: 'id',
        align: 'left',
        sortable: false,
        hidden: true,
        search: false
    },
    {
        label: 'sessionid',
        name: 'sessionid',
        index: 'sessionid',
        align: 'left',
        sortable: false,
        hidden: true,
        search: true
    },

    { name: "act", template: "actions" },

    {
        label: 'Name',
        name: 'taskname',
        index: 'taskname',
        align: 'left',
        sortable: false,
        hidden: false,
        search: true
    },
    {
        label: 'State',
        name: 'state',
        index: 'state',
        align: 'center',
        sortable: false,
        hidden: false,
        search: false,
        editable: true,
        edittype: "select",
        editoptions: { value: "pending:pending;running:running;onhold:onhold;finished:finished" }
    },
    {
        label: 'Start',
        name: 'start',
        index: 'start',
        align: 'center',
        sortable: false,
        hidden: false,
        search: true,
        formatter: localDateTimeFormatter
    },
    {
        label: 'Finish',
        name: 'finish',
        index: 'finish',
        align: 'center',
        sortable: false,
        hidden: false,
        search: true,
        formatter: localDateTimeFormatter
    },
    {
        label: 'Result',
        name: 'result',
        index: 'result',
        align: 'center',
        sortable: false,
        hidden: false,
        search: false,

        formatter: function(cellvalue, options,rowObject) {
            if ( cellvalue === null ) {
                return "";
            } else if ( cellvalue ) {
                return '<span class="result-passed">Passed</span>';
            } else  if ( ! cellvalue ) {
                return '<span class="result-failed">Failed</span>';
            }
        }
    },
    {
        label: 'Log',
        name: 'log',
        index: 'log',
        align: 'center',
        sortable: false,
        hidden: false,
        search: false,
        formatter: logUrlFormatter
    },
    {
        label: 'Message',
        name: 'message',
        index: 'message',
        align: 'left',
        sortable: false,
        hidden: false,
        search: false,
        cellattr: function (rowId, tv, rawObject, cm, rdata) { 
            return 'style="white-space: normal;"';
        }
    },
    {
        label: 'Execution Order',
        name: 'execution_order',
        index: 'execution_order',
        align: 'right',
        sortable: false,
        hidden: true,
        search: false,
    }
],
