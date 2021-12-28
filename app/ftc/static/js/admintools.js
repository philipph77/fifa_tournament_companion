async function adjustNumberofGoalSelections(goalForHomeTeam){
    if(goalForHomeTeam){
        targetNumber = document.getElementById("homeGoalsInput").value
        actualNumber = document.getElementById("homeGoalsInputWrapper").childElementCount;
    }else{
        targetNumber = document.getElementById("awayGoalsInput").value
        actualNumber = document.getElementById("awayGoalsInputWrapper").childElementCount;
    }
    matchId = document.getElementById("matchIDSelector").value

    scoredTeamPlayers = await getPlayersFromMatchId(matchId, goalForHomeTeam)
    receivedTeamPlayers = await getPlayersFromMatchId(matchId, goalForHomeTeam==1 ? 0 : 1)


    for(var i=actualNumber; i<targetNumber; i++){
        addOneGoalsSelect(scoredTeamPlayers, receivedTeamPlayers, goalForHomeTeam, i+1)
    }

    for (var i=actualNumber; i>targetNumber; i--){
        deleteOneGoalsSelect(goalForHomeTeam)
    }
    
}

async function getPlayersFromMatchId(matchId, isHomeTeam) {
    response =  await $.getJSON($SCRIPT_ROOT + 'ajax/_get_players_from_matchid', {
        matchId: matchId,
        isHomeTeam: isHomeTeam
    }, function(data, textStatus, jqXHR) {
        });
    return response.players;
};

function addOneGoalsSelect(scoredTeamPlayers, receivedTeamPlayers, isHomeTeam, i) {
    if (isHomeTeam){
        var parent = document.getElementById("homeGoalsInputWrapper");
    }else{
        var parent = document.getElementById("awayGoalsInputWrapper");
    }

    var wrapper = document.createElement("div");
    wrapper.setAttribute("class", "goalSelectionInput")

    var selectList = document.createElement("select");
    var minuteInput = document.createElement("input");
    minuteInput.setAttribute("type", "number");
    minuteInput.setAttribute("min", "1");

    var wasPenalty = document.createElement("input");
    wasPenalty.setAttribute("type", "checkbox");
    wasPenalty.setAttribute("value", "1");
    if (isHomeTeam){
        wasPenalty.setAttribute("name", "wasPenalty-hg-"+i)
    }else{
        wasPenalty.setAttribute("name", "wasPenalty-ag-"+i)
    }
    
    selectList.required = true;
    minuteInput.required = true;

    if(isHomeTeam){
        selectList.setAttribute("name", "homeGoalSelect-"+i)
        minuteInput.setAttribute("name", "homeGoalMinute-"+i)
    }else{
        selectList.setAttribute("name", "awayGoalSelect-"+i)
        minuteInput.setAttribute("name", "awayGoalMinute-"+i)
    }

    wrapper.appendChild(selectList);
    wrapper.appendChild(minuteInput);
    wrapper.appendChild(wasPenalty);

    var optgroup = document.createElement("optgroup");
    optgroup.label = "Scoring Team"
    selectList.appendChild(optgroup)

    for (var i = 0; i < scoredTeamPlayers.length; i++) {
        var option = document.createElement("option");
        option.setAttribute("value", scoredTeamPlayers[i][0]);
        option.text = scoredTeamPlayers[i][1];
        selectList.appendChild(option);
    }

    var optgroup = document.createElement("optgroup");
    optgroup.label = "Receiving Team"
    selectList.appendChild(optgroup)

    for (var i = 0; i < receivedTeamPlayers.length; i++) {
        var option = document.createElement("option");
        option.setAttribute("value", receivedTeamPlayers[i][0]);
        option.text = receivedTeamPlayers[i][1] + " (OG)";
        selectList.appendChild(option);
    }

    parent.appendChild(wrapper)
}

function deleteOneGoalsSelect(isHomeTeam){
    if (isHomeTeam){
        var parent = document.getElementById("homeGoalsInputWrapper");
    }else{
        var parent = document.getElementById("awayGoalsInputWrapper");
    }
    parent.removeChild(parent.lastChild);
}

function deleteAllGoalsSelections(){
    var parentHome = document.getElementById("homeGoalsInputWrapper");
    var parentAway = document.getElementById("awayGoalsInputWrapper");
    while (parentHome.firstChild) {
        parentHome.removeChild(parentHome.firstChild);
    }
    while (parentAway.firstChild) {
        parentAway.removeChild(parentAway.firstChild);
    }
    return false
}

function resetGoalInputs(){
    homeGoalsInputSelector = document.getElementById("homeGoalsInput");
    awayGoalsInputSelector = document.getElementById("awayGoalsInput");

    homeGoalsInputSelector.value = 0
    awayGoalsInputSelector.value= 0

    return false
}

async function adjustNumberofCards(){
    targetNumber = document.getElementById("cardsInput").value
    actualNumber = document.getElementById("cardsInputWrapper").childElementCount;

    matchId = document.getElementById("matchIDSelector").value

    homePlayers = await getPlayersFromMatchId(matchId, 1)
    awayPlayers = await getPlayersFromMatchId(matchId, 0)

    for(var i=actualNumber; i<targetNumber; i++){
        addOneCardsSelect(homePlayers, awayPlayers, i+1)
    }

    for (var i=actualNumber; i>targetNumber; i--){
        deleteOneCardsSelect()
    }
}

function addOneCardsSelect(homePlayers, awayPlayers, i){
    var parent = document.getElementById("cardsInputWrapper");

    var wrapper = document.createElement("div");
    wrapper.setAttribute("class", "cardSelectionInput")

    var selectList = document.createElement("select");
    var minuteInput = document.createElement("input");
    var wasYellowCardSelect = document.createElement("select");

    minuteInput.setAttribute("type", "number")
    minuteInput.setAttribute("min", "1")
    minuteInput.setAttribute("name", "cardMinute-"+i)

    selectList.setAttribute("name", "cardPlayer-"+i)

    wasYellowCardSelect.setAttribute("name", "cardCategory-"+i)

    minuteInput.required = true;
    selectList.required = true;
    wasYellowCardSelect.required = true
    
    wrapper.appendChild(selectList);
    wrapper.appendChild(minuteInput);
    wrapper.appendChild(wasYellowCardSelect)

    var option = document.createElement("option");
    option.setAttribute("value", 1);
    option.text = "Yellow";
    wasYellowCardSelect.appendChild(option);
    var option = document.createElement("option");
    option.setAttribute("value", 3);
    option.text = "Yellow-Red";
    wasYellowCardSelect.appendChild(option);
    var option = document.createElement("option");
    option.setAttribute("value", 5);
    option.text = "Red";
    wasYellowCardSelect.appendChild(option);

    var optgroup = document.createElement("optgroup");
    optgroup.label = "Home Team"
    selectList.appendChild(optgroup)

    for (var i = 0; i < homePlayers.length; i++) {
        var option = document.createElement("option");
        option.setAttribute("value", homePlayers[i][0]);
        option.text = homePlayers[i][1];
        selectList.appendChild(option);
    }

    var optgroup = document.createElement("optgroup");
    optgroup.label = "Away Team"
    selectList.appendChild(optgroup)

    for (var i = 0; i < awayPlayers.length; i++) {
        var option = document.createElement("option");
        option.setAttribute("value", awayPlayers[i][0]);
        option.text = awayPlayers[i][1];
        selectList.appendChild(option);
    }

    parent.appendChild(wrapper)
}

function deleteOneCardsSelect(){
    var parent = document.getElementById("cardsInputWrapper");
    parent.removeChild(parent.lastChild);
}

function deleteAllCardsSelections(){
    var parent = document.getElementById("cardsInputWrapper");
    while (parent.firstChild) {
        parent.removeChild(parent.firstChild);
    }
    return false
}

function resetCardInputs(){
    cardsInputSelector = document.getElementById("cardsInput");
    cardsInputSelector.value = 0

    return false
}