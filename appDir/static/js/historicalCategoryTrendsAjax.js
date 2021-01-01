import { drawHistoricalCategoryTrendsD3 } from './historicalCategoryTrendsD3Func.js';
var form = document.getElementById('category-history');

form.addEventListener('submit', async(e) => {
    e.preventDefault();
    var csrf_token = document.getElementById('csrf_token').value;
    var selectCat = document.getElementById('selectCat').value;

    var formData = JSON.stringify({
        csrf_token: csrf_token,
        selectCat: selectCat
    });

    const response = await fetch('/categoryHistory', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: formData
    });

    response.text().then(function(value){
        var a = JSON.parse(value);

        drawHistoricalCategoryTrendsD3(JSON.parse(a["graph_data"]));
    });
})
