changeTxnBoxColor()

function changeTxnBoxColor(){
    var divArray = document.getElementsByClassName("txn-box");

    for(ii=0; ii<divArray.length; ii++){
        if(divArray[ii].getElementsByClassName("txn-type")[0].innerHTML.match(/\/([a-zA-Z]*).png/)[1] == "MoneyOut"){
            divArray[ii].style["background-color"] = "#ffdfdf";
        }
        else{
            divArray[ii].style["background-color"] = "#dfffe0";
        }
    }
}