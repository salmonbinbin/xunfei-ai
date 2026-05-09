import * as echarts from 'echarts'

/**
 * 获取折线图配置（用于AI分析趋势展示）
 * @param {Array} data - 数据点数组
 * @param {Array} xAxisData - X轴标签数组
 * @param {string} seriesName - 系列名称
 * @returns {Object} ECharts配置对象
 */
export function getLineChartOption(data, xAxisData, seriesName = '操作次数') {
  return {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(15, 23, 42, 0.9)',
      borderColor: '#334155',
      textStyle: {
        color: '#F1F5F9'
      },
      formatter: (params) => {
        const item = params[0]
        return `${item.name}<br/>${seriesName}: <strong>${item.value}</strong> 次`
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: xAxisData,
      axisLine: {
        lineStyle: {
          color: '#334155'
        }
      },
      axisLabel: {
        color: '#94A3B8',
        fontSize: 11
      }
    },
    yAxis: {
      type: 'value',
      axisLine: {
        show: false
      },
      axisTick: {
        show: false
      },
      axisLabel: {
        color: '#94A3B8',
        fontSize: 11
      },
      splitLine: {
        lineStyle: {
          color: '#334155',
          type: 'dashed'
        }
      }
    },
    series: [
      {
        name: seriesName,
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 8,
        lineStyle: {
          color: '#22D3EE',
          width: 3
        },
        itemStyle: {
          color: '#0891B2',
          borderColor: '#22D3EE',
          borderWidth: 2
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(34, 211, 238, 0.3)' },
              { offset: 1, color: 'rgba(34, 211, 238, 0.05)' }
            ]
          }
        },
        data: data
      }
    ]
  }
}