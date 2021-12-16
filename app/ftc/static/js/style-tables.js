$(document).ready(function() {
    tables = document.getElementsByClassName('dataframe');
    for(tableIndex=0; tableIndex<tables.length; tableIndex++){
        table = tables[tableIndex]
        adjustHeaderClass(table.tHead.rows[0])
        adjustThClass($('.dataframe th'))
        adjustBodyClass(table.tBodies[0])
        adjustRowClass(table.tBodies[0].rows)
        adjustTableDataClass(document.getElementsByTagName("td"))
    }
});

function adjustHeaderClass(tableHead){
    //tableHead = table.tHead.rows[0]
    tableHead.setAttribute("class", "text-xs font-semibold tracking-wide text-left text-gray-500 uppercase border-b dark:border-gray-700 bg-gray-50 dark:text-gray-400 dark:bg-gray-800");
    tableHead.setAttribute("style", "")
}
function adjustThClass(thElems){
    for(i=0;i<thElems.length;i++){
        thElems[i].classList.add("px-4")
        thElems[i].classList.add("py-3")
    }
}
function adjustBodyClass(tableBody){
    tableBody.setAttribute("class", "bg-white divide-y dark:divide-gray-700 dark:bg-gray-800")
}
function adjustRowClass(trElems){
    for(i=0; i<trElems.length;i++){
        trElems[i].classList.add("text-gray-700")
        trElems[i].classList.add("dark:text-gray-400")
    }
}
function adjustTableDataClass(tdElems){
    for(i=0; i<tdElems.length;i++){
        tdElems[i].classList.add("px-4")
        tdElems[i].classList.add("py-3")
        tdElems[i].classList.add("text-sm")
    }
    console.log(tdElems)
}

// px-4 py-3 text-sm