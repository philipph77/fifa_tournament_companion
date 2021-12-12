$(document).ready(function() {
    $('.select2Dropdown').select2({
        minInputLength: 2
    });
});

$(document).ready(function() {
    $('.asyncPlayerSelect').select2({
        placeholder: "Search for Playername or Clubname",
        ajax: {
            delay: 250,
            url: $SCRIPT_ROOT + 'ajax/_get_players_from_query',
            data: function (params) {
                var query = {
                    searchInput: params.term
                }
                return query;
            },
            processResults: function (data) {
                return {
                    results: $.map(data, function (item) {
                        console.log(item)
                        return {
                            text: item.short_name + " (" + item.club_name + ")",
                            id: item.ID
                        }
                    })
                };
            }
        },
        minimumInputLength: 2
    });
});