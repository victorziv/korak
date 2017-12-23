colModel: [
    {
        label: 'ID',
        name: 'id',
        index: 'id',
        align: 'left',
        sortable: false,
        hidden: true,
        search: false
    },
    {
        label: 'UID',
        name: 'uid',
        index: 'uid',
        align: 'left',
        sortable: false,
        hidden: true,
        search: false
    },
    {
        label: 'Machine S/N',
        name: 'sn',
        index: 'sn',
        align: 'left',
        sortable: false,
        hidden: true,
        search: true
    },
    {
        label: 'System Name',
        name: 'system_name',
        index: 'system_name',
        align: 'left',
        sortable: true,
        hidden: false,
        search: true
    },
    {
        label: 'Model',
        name: 'model',
        index: 'model',
        align: 'center',
        sortable: true,
        hidden: false,
        search: true
    },
    {
        label: 'Verification Type',
        name: 'verification_type',
        index: 'verification_type',
        align: 'center',
        sortable: true,
        hidden: false,
        search: true
    },
    {
        label: 'IVT Owner',
        name: 'owner_name',
        index: 'owner_name',
        align: 'center',
        sortable: true,
        hidden: false,
        search: true,
        formatter: infinibookUrlFormatter
    },
    {
        label: 'owner_email',
        name: 'owner_email',
        index: 'owner_email',
        align: 'center',
        sortable: true,
        hidden: true,
        search: true,
    },
    {
        label: 'owner_username',
        name: 'owner_username',
        index: 'owner_username',
        align: 'center',
        sortable: true,
        hidden: true,
        search: true,
    },
    {
        label: 'owner_socialid',
        name: 'owner_socialid',
        index: 'owner_socialid',
        align: 'center',
        sortable: true,
        hidden: true,
        search: true,
    },
    {
        label: 'Ticket',
        name: 'ticket',
        index: 'ticket',
        align: 'center',
        sortable: true,
        hidden: false,
        search: true,
        formatter: jiraBrowseUrlFormatter
    },
    {
        label: 'Ticket Opened',
        name: 'created',
        index: 'created',
        align: 'right',
        sortable: true,
        hidden: true,
        search: true,
        formatter: localDateTimeFormatter
    },
    {
        label: 'Customer',
        name: 'customer',
        index: 'customer',
        align: 'center',
        sortable: true,
        hidden: false,
        search: true
    },
    {
        label: 'Slot',
        name: 'slot',
        index: 'slot',
        align: 'center',
        sortable: true,
        hidden: false,
        search: true
    },
    {
        label: 'State',
        name: 'state',
        index: 'state',
        align: 'center',
        sortable: true,
        hidden: false,
        search: true
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
            } else if ( typeof cellvalue === 'undefined' ) {
                return "";
            } else if ( cellvalue ) {
                return '<span class="result-passed">Passed</span>';
            } else  if ( ! cellvalue ) {
                return '<span class="result-failed">Failed</span>';
            }
        }
    },
    {
        label: 'Start',
        name: 'start',
        index: 'start',
        align: 'right',
        sortable: true,
        hidden: false,
        search: true,
        formatter: localDateFormatter
    },
    {
        label: 'Due Date',
        name: 'due',
        index: 'due',
        align: 'right',
        sortable: true,
        hidden: false,
        search: true,
        formatter: localDateFormatter

    },
    {
        label: 'Weekends Included',
        name: 'weekend_included',
        index: 'weekend_included',
        align: 'center',
        sortable: true,
        hidden: false,
        search: false,
        formatter: function(cellvalue, options,rowObject) {
            if ( cellvalue === null || typeof cellvalue === 'undefined' ) {
                return "Unknown";
            } else if ( cellvalue ) {
                return 'Yes';
            } else  if ( ! cellvalue ) {
                return "No";
            }
        }

    }
],
