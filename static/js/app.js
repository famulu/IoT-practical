document.addEventListener("DOMContentLoaded", () => {
  const ctx = document.getElementById("myChart").getContext("2d");

  const myChart = new Chart(ctx, {
    type: "line",
    data: {
      datasets: [{ label: "Smoke",  }],
    },
    options: {
      borderWidth: 3,
      borderColor: ['rgba(255, 99, 132, 1)',],
      animation: false
    },
  });

  function addData(label, data) {
    myChart.data.labels.push(label);
    myChart.data.datasets.forEach((dataset) => {
      dataset.data.push(data);
    });
    myChart.update();
  }

  function removeFirstData() {
    myChart.data.labels.splice(0, 1);
    myChart.data.datasets.forEach((dataset) => {
      dataset.data.shift();
    });
  }

  const MAX_DATA_COUNT = 100;
  //connect to the socket server.
  //   var socket = io.connect("http://" + document.domain + ":" + location.port);
  const socket = io.connect();

  //receive details from server
  socket.on("updateSensorData", function (msg) {
    console.log("Received sensorData :: " + msg.date + " :: " + msg.value);

    // Show only MAX_DATA_COUNT data
    if (myChart.data.labels.length > MAX_DATA_COUNT) {
      removeFirstData();
    }
    addData(msg.date, msg.value);

    document.querySelector('#pushButton').textContent = msg.push_button
  });

  socket.on('updateActuatorData', (msg) => {
    document.querySelector('#buzzer').href = '/buzzer/' + msg.buzzer === 1 ? 'off' : 'on';
    document.querySelector('#buzzerState').textContent = msg.buzzer === 1 ? 'on' : 'off';
    document.querySelector('#fan').href = '/fan/' + msg.fan === 1 ? 'off' : 'on';
    document.querySelector('#fanState').textContent = msg.fan === 1 ? 'on' : 'off';
  })

  document.querySelector("#threshold").addEventListener("input", (event) => {
    socket.emit('thresholdChange', event.target.value)
    document.querySelector("#thresholdValue").textContent = event.target.value;
  })
});
