function hideUnhide(checkbox){
    var divArray = document.getElementsByClassName("hide-unhide");

    if(checkbox.checked == true){
        for(i=0; i<divArray.length; i++){
            divArray[i].style.display = 'none';
        }
    }
    else{
        for(i=0; i<divArray.length; i++){
            divArray[i].style.display = '';
        }
    }
}