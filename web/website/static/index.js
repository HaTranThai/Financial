window.onload = function () {
  // Menu
  const para = document.getElementById("stockMenu");

  var selectorDiv = document.createElement("div");
  selectorDiv.classList.add("selector");

  var selectFieldDiv = document.createElement("div");
  selectFieldDiv.id = "selectField";

  var dataDiv = document.getElementById("data");
  var idsJsonString = dataDiv.getAttribute("ids");
  idsJsonString = idsJsonString.replace(/'/g, '"');
  var options = JSON.parse(idsJsonString);
  // console.log(options);
  // var options = ["ltceur2018","AAPL", "MSFT", "GOOGL", "AMZN", "DIS", "JPM", "WMT","KO","7203.T","6758.T"];
  var choiceStockP = document.createElement("p");
  choiceStockP.id = "choiceStock";
  choiceStockP.textContent = options[0].ID;
  choiceStockP.style = "margin-bottom: 0px;";
  selectFieldDiv.appendChild(choiceStockP);

  var listUl = document.createElement("ul");
  listUl.id = "list";
  listUl.classList.add("hide");
  options.forEach(function (item) {
    // console.log(item.ID);
    var li = document.createElement("li");
    li.classList.add("options");
    var p = document.createElement("p");
    p.id = "textOption";
    p.style = "margin-bottom: 0px;";
    p.textContent = item.ID;
    li.appendChild(p);
    listUl.appendChild(li);
  });
  selectFieldDiv.appendChild(listUl);
  selectorDiv.appendChild(selectFieldDiv);
  para.appendChild(selectorDiv);
  // --------------------------------------------------------------------------------------------------
  var selectField = document.getElementById("selectField");
  var choiceStock = document.getElementById("choiceStock");
  var options = document.getElementsByClassName("options");
  var list = document.getElementById("list");
  selectField.onclick = function () {
    list.classList.toggle("hide");
  };
  for (option of options) {
    option.onclick = function () {
      choiceStock.innerHTML = this.textContent;
      var Path = "/static/" + choiceStock.textContent.trim() + ".json";
      var title = choiceStock.textContent.trim() + " " + "Stock Chart";
      var name = choiceStock.textContent.trim();
      drawChart(Path, title, name);
    };
    var name = choiceStock.textContent.trim();
    var Path = "/static/" + choiceStock.textContent.trim() + ".json";
    var title = choiceStock.textContent.trim() + " " + "Stock Chart";
    drawChart(Path, title, name);
  }

  // Vũ
  var tbody = document.getElementsByTagName("tbody")[1];
  tbody.innerHTML = "";
  fetch("/static/AAPL.json")
    .then((response) => response.json())
    .then((items) => {
      for (var i = 0; i < 10; i++) {
        var tr = document.createElement("tr");
        if (items[i].changed < 0) {
          tr.innerHTML =
            '<td class="sticky-code sticky-left">' +
            String(items[i].date) +
            "</td>" +
            '<td style="color: #ff453a !important">' +
            String(items[i].changed) +
            "<br />(" +
            String(items[i].changed_rate) +
            ")</td>" +
            "<td>" +
            String(items[i].open) +
            "</td>" +
            "<td>" +
            String(items[i].low) +
            "</td>" +
            "<td>" +
            String(items[i].high) +
            "</td>" +
            "<td>" +
            String(items[i].close) +
            "</td>" +
            "<td>" +
            String(items[i].volume) +
            "</td>";
        } else {
          tr.innerHTML =
            '<td class="sticky-code sticky-left">' +
            String(items[i].date) +
            "</td>" +
            '<td style="color: #34c763 !important"> +' +
            String(items[i].changed) +
            "<br />(" +
            String(items[i].changed_rate) +
            ")</td>" +
            "<td>" +
            String(items[i].open) +
            "</td>" +
            "<td>" +
            String(items[i].low) +
            "</td>" +
            "<td>" +
            String(items[i].high) +
            "</td>" +
            "<td>" +
            String(items[i].close) +
            "</td>" +
            "<td>" +
            String(items[i].volume) +
            "</td>";
        }
        tbody.appendChild(tr);
      }
    });

  const buttons = document.getElementById("search");
  buttons.onclick = function () {
    const ticker = document.getElementById("ticker");
    var date_from = document.getElementsByClassName("data-market__from")[0];
    var date_to = document.getElementsByClassName("data-market__to")[0];

    if (date_from.value == "" || date_to.value == "") {
      date_from = Date.parse("2024-04-01");
      date_to = new Date();
    } else {
      date_from = Date.parse(date_from.value);
      date_to = Date.parse(date_to.value);
    }

    var tbody = document.getElementsByTagName("tbody")[1];
    tbody.innerHTML = "";

    fetch("/static/" + ticker.value + ".json")
      .then((response) => response.json())
      .then((items) => {
        for (var i = 0; i < (items.length > 10 ? 10 : items.length); i++) {
          if (
            date_from <= Date.parse(items[i].date) &&
            Date.parse(items[i].date) <= date_to
          ) {
            var tr = document.createElement("tr");
            if (items[i].changed < 0) {
              tr.innerHTML =
                '<td class="sticky-code sticky-left">' +
                String(items[i].date) +
                "</td>" +
                '<td style="color: #ff453a !important">' +
                String(items[i].changed) +
                "<br />(" +
                String(items[i].changed_rate) +
                ")</td>" +
                "<td>" +
                String(items[i].open) +
                "</td>" +
                "<td>" +
                String(items[i].low) +
                "</td>" +
                "<td>" +
                String(items[i].high) +
                "</td>" +
                "<td>" +
                String(items[i].close) +
                "</td>" +
                "<td>" +
                String(items[i].volume) +
                "</td>";
            } else {
              tr.innerHTML =
                '<td class="sticky-code sticky-left">' +
                String(items[i].date) +
                "</td>" +
                '<td style="color: #34c763 !important"> +' +
                String(items[i].changed) +
                "<br />(" +
                String(items[i].changed_rate) +
                ")</td>" +
                "<td>" +
                String(items[i].open) +
                "</td>" +
                "<td>" +
                String(items[i].low) +
                "</td>" +
                "<td>" +
                String(items[i].high) +
                "</td>" +
                "<td>" +
                String(items[i].close) +
                "</td>" +
                "<td>" +
                String(items[i].volume) +
                "</td>";
            }
            tbody.appendChild(tr);
          }
        }
      });
  };
};

function drawChart(Path, title, name) {
  var dataPoints1 = [],
    dataPoints2 = [],
    dataPoints3 = [];
  var stockChart = new CanvasJS.StockChart("chartContainer", {
    exportEnabled: true,
    theme: "dark1",
    title: {
      text: title,
    },
    charts: [
      {
        toolTip: {
          shared: true,
        },
        axisX: {
          lineThickness: 5,
          tickLength: 0,
          labelFormatter: function (e) {
            return "";
          },
          crosshair: {
            enabled: true,
            snapToDataPoint: true,
            labelFormatter: function (e) {
              return "";
            },
          },
        },
        axisY2: {
          title: name + " Price",
          prefix: "$",
        },
        legend: {
          verticalAlign: "top",
          horizontalAlign: "left",
        },
        data: [
          {
            name: "Price (in Dollar)",
            yValueFormatString: "$#,###.##",
            axisYType: "secondary",
            type: "candlestick",
            risingColor: "green",
            fallingColor: "red",
            dataPoints: dataPoints1,
          },
        ],
      },
      {
        height: 100,
        toolTip: {
          shared: true,
        },
        axisX: {
          crosshair: {
            enabled: true,
            snapToDataPoint: true,
          },
        },
        axisY2: {
          prefix: "$",
          title: name + "/Dollar",
        },
        legend: {
          horizontalAlign: "left",
        },
        data: [
          {
            yValueFormatString: "$#,###.##",
            axisYType: "secondary",
            name: name + "/Dollar",
            dataPoints: dataPoints2,
          },
        ],
      },
    ],
    navigator: {
      data: [
        {
          color: "grey",
          dataPoints: dataPoints3,
        },
      ],
      slider: {
        minimum: new Date().setFullYear(2023),
        maximum: new Date(),
      },
    },
  });
  $.getJSON(Path, function (data) {
    for (var i = 0; i < data.length; i++) {
      dataPoints1.push({
        x: new Date(data[i].date),
        y: [
          Number(data[i].open),
          Number(data[i].high),
          Number(data[i].low),
          Number(data[i].close),
        ],
        color: data[i].open < data[i].close ? "green" : "red",
      });
      dataPoints2.push({
        x: new Date(data[i].date),
        y: Number(data[i].volume_dollar),
        color: data[i].open < data[i].close ? "green" : "red",
      });
      dataPoints3.push({
        x: new Date(data[i].date),
        y: Number(data[i].close),
      });
    }
    stockChart.render();
  });
}
