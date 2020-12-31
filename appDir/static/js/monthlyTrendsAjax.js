import { drawMonthlyTrendsD3 } from "./monthlyTrendsD3Func.js";
import { drawTrianglePointerD3 } from './trianglePointerD3F.js';
var form = document.getElementById("monthly-categories");

form.addEventListener("submit", async (e) => {
    e.preventDefault();

    var csrf_token = document.getElementById("csrf_token").value;
    var selectMonth = document.getElementById("selectMonth").value;
    console.log(selectMonth)

    var formData = JSON.stringify({
        csrf_token: csrf_token,
        selectMonth: selectMonth,
    });

    const response = await fetch("/monthlyTrends", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: formData,
    });

    response.text().then(function (value) {
        var a = JSON.parse(value);

        document.getElementById("txn-data-for").innerHTML = "(for " + a["data_for"] + ")";
        document.getElementById("txn-income").innerHTML = "₹ " + Math.round(a["monthly_num"]["income"]);
        document.getElementById("txn-income").innerHTML = "₹ " + Math.round(a["monthly_num"]["expense"]);

        if(a["monthly_num"]["income-mom-percent"] >= 0){
            var color = "#00C013";
            drawTrianglePointerD3(color, "up", "txn-income-caret");
        }
        else{
            var color = "#C00000";
            drawTrianglePointerD3(color, "down", "txn-income-caret");
        }
        document.getElementById("txn-income-percent").innerHTML = "<span class='change-number' style='color: " + color + ";'>" + Math.round(a["monthly_num"]["income-mom-percent"]) + " %</span> MoM";

        if(a["monthly_num"]["expense-mom-percent"] >= 0){
            var color = "#00C013";
            drawTrianglePointerD3(color, "up", "txn-expense-caret");
        }
        else{
            var color = "#C00000";
            drawTrianglePointerD3(color, "down", "txn-expense-caret");
        }
        document.getElementById("txn-expense-percent").innerHTML = "<span class='change-number' style='color: " + color + ";'>" + Math.round(a["monthly_num"]["expense-mom-percent"]) + " %</span> MoM";

        drawMonthlyTrendsD3(JSON.parse(a["txn_E"]["graph_data"]));
    });
});
