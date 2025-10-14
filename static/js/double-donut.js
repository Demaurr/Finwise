(function () {
  const innerLabels = ['Alpha', 'Beta', 'Gamma'];
  const innerData = [35, 25, 40];

  const outerLabels = ['Red', 'Blue', 'Green', 'Yellow'];
  const outerData = [12, 28, 30, 30];

  const innerColors = [
    'rgba(54, 162, 235, 0.85)',   
    'rgba(75, 192, 192, 0.85)',   
    'rgba(255, 205, 86, 0.85)'    
  ];

  const outerColors = [
    'rgba(255, 99, 132, 0.85)',   
    'rgba(153, 102, 255, 0.85)',  
    'rgba(255, 159, 64, 0.85)',   
    'rgba(201, 203, 207, 0.85)'   
  ];

  const ctx = document.getElementById('doubleDonut').getContext('2d');

  const combinedLabels = {
    0: innerLabels,
    1: outerLabels
  };

  const doubleDonut = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: [...innerLabels, ...outerLabels],
      datasets: [
        {
          label: 'Inner categories',
          data: innerData,
          backgroundColor: innerColors,
          weight: 1,
          borderColor: '#fff',
          borderWidth: 2
        },
        {
          label: 'Outer categories',
          data: outerData,
          backgroundColor: outerColors,
          weight: 1,
          borderColor: '#fff',
          borderWidth: 2
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '40%',
      plugins: {
        legend: {
          position: 'right',
          align: 'center',
          labels: {
            generateLabels: function (chart) {
              const datasets = chart.data.datasets;
              const legendItems = [];

              datasets.forEach((ds, datasetIndex) => {
                const labels = combinedLabels[datasetIndex];
                for (let i = 0; i < ds.data.length; i++) {
                  const meta = chart.getDatasetMeta(datasetIndex);
                  legendItems.push({
                    text: `${ds.label} — ${labels[i]} (${ds.data[i]})`,
                    fillStyle: ds.backgroundColor[i],
                    hidden: false,
                    datasetIndex: datasetIndex,
                    index: i
                  });
                }
              });

              return legendItems;
            }
          },
          onClick: function (e, legendItem, legend) {
            const chart = legend.chart;
            const datasetIndex = legendItem.datasetIndex;
            const sliceIndex = legendItem.index;
            const ds = chart.data.datasets[datasetIndex];
            if (ds._hiddenValues === undefined) ds._hiddenValues = new Array(ds.data.length).fill(null);

            if (ds._hiddenValues[sliceIndex] === null) {
              ds._hiddenValues[sliceIndex] = ds.data[sliceIndex];
              ds.data[sliceIndex] = 0;
            } else {
              ds.data[sliceIndex] = ds._hiddenValues[sliceIndex];
              ds._hiddenValues[sliceIndex] = null;
            }
            chart.update();
          }
        },
        tooltip: {
          callbacks: {
            title: function (items) {
              const item = items[0];
              const datasetIndex = item.datasetIndex;
              const index = item.dataIndex;
              const labels = combinedLabels[datasetIndex];
              return `${item.dataset.label} — ${labels[index]}`;
            },
            label: function (context) {
              const val = context.parsed;
              const dataset = context.chart.data.datasets[context.datasetIndex];
              const sum = dataset.data.reduce((a, b) => a + b, 0) || 1;
              const pct = ((val / sum) * 100).toFixed(1);
              return ` ${val} (${pct}%)`;
            }
          }
        },
      },
      spacing: 4,
      animation: {
        animateRotate: true,
        animateScale: true
      }
    }
  });

  window.updateChart = function (payload) {
    if (payload.inner) {
      doubleDonut.data.datasets[0].data = payload.inner.data || doubleDonut.data.datasets[0].data;
      doubleDonut.data.datasets[0].backgroundColor = payload.inner.colors || doubleDonut.data.datasets[0].backgroundColor;
      combinedLabels[0] = payload.inner.labels || combinedLabels[0];
      doubleDonut.data.datasets[0].label = payload.inner.label || doubleDonut.data.datasets[0].label;
    }
    if (payload.outer) {
      doubleDonut.data.datasets[1].data = payload.outer.data || doubleDonut.data.datasets[1].data;
      doubleDonut.data.datasets[1].backgroundColor = payload.outer.colors || doubleDonut.data.datasets[1].backgroundColor;
      combinedLabels[1] = payload.outer.labels || combinedLabels[1];
      doubleDonut.data.datasets[1].label = payload.outer.label || doubleDonut.data.datasets[1].label;
    }
    doubleDonut.update();
  };
})();
