import * as echarts from 'echarts'

// 主色调
const PRIMARY_COLOR = '#0891B2'
const PRIMARY_LIGHT = '#22D3EE'
const GRADIENT_COLORS = [
  { offset: 0, color: '#0891B2' },
  { offset: 1, color: '#22D3EE' }
]

/**
 * 成绩分布直方图配置
 * @param {Array} distribution - [{range, count, percentage}]
 */
export function getDistributionChart(distribution) {
  return {
    title: {
      text: '成绩分布',
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 600,
        color: '#1E293B'
      }
    },
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        const data = params[0]
        const item = distribution[data.dataIndex]
        return `${data.name}<br/>人数: ${data.value}人 (${item.percentage}%)`
      }
    },
    grid: {
      left: '10%',
      right: '10%',
      top: '15%',
      bottom: '15%'
    },
    xAxis: {
      type: 'category',
      data: distribution.map(d => d.range),
      axisLabel: {
        color: '#64748B',
        fontSize: 12
      },
      axisLine: {
        lineStyle: { color: '#E2E8F0' }
      }
    },
    yAxis: {
      type: 'value',
      name: '人数',
      nameTextStyle: {
        color: '#64748B',
        fontSize: 12
      },
      axisLabel: {
        color: '#64748B',
        fontSize: 12
      },
      axisLine: {
        lineStyle: { color: '#E2E8F0' }
      },
      splitLine: {
        lineStyle: { color: '#F1F5F9' }
      },
      min: 0
    },
    series: [{
      type: 'bar',
      data: distribution.map(d => d.count),
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, GRADIENT_COLORS),
        borderRadius: [4, 4, 0, 0]
      },
      barWidth: '40%',
      label: {
        show: true,
        position: 'top',
        formatter: '{c}人',
        color: '#64748B',
        fontSize: 11
      }
    }]
  }
}

/**
 * 学生能力雷达图配置
 * @param {Array} students - 学生成绩数据（取前5名）
 * @param {number} maxDisplay - 最大显示学生数，默认5
 */
export function getRadarChart(students, maxDisplay = 5) {
  const topStudents = students.slice(0, maxDisplay)

  // 配色方案
  const colorPalette = [
    '#0891B2', '#22D3EE', '#34D399', '#8B5CF6', '#F59E0B'
  ]

  // 动态计算高度，确保足够的垂直空间
  const chartHeight = Math.max(350, 200 + topStudents.length * 25)

  return {
    backgroundColor: '#FFFFFF',
    title: {
      text: '学生能力雷达图',
      left: 'center',
      top: 10,
      textStyle: {
        fontSize: 16,
        fontWeight: 600,
        color: '#1E293B'
      },
      padding: [0, 0, 10, 0]
    },
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(255,255,255,0.95)',
      borderColor: '#E2E8F0',
      textStyle: { color: '#475569' }
    },
    legend: {
      orient: 'horizontal',
      data: topStudents.map(s => s.student_name),
      bottom: 5,
      left: 'center',
      itemWidth: 12,
      itemHeight: 8,
      itemGap: 10,
      textStyle: {
        color: '#64748B',
        fontSize: 11
      },
      pageTextStyle: {
        color: '#64748B'
      }
    },
    radar: {
      center: ['50%', '52%'],
      radius: '60%',
      triggerEvent: true,
      name: {
        textStyle: {
          color: '#475569',
          fontSize: 12,
          fontWeight: 500,
          padding: [3, 10]
        }
      },
      indicator: [
        { name: '平时表现', max: 100 },
        { name: '期中考试', max: 100 },
        { name: '期末考试', max: 100 },
        { name: '实验实践', max: 100 }
      ],
      splitNumber: 4,
      splitLine: {
        show: true,
        lineStyle: {
          color: '#E2E8F0',
          width: 1
        }
      },
      splitArea: {
        show: true,
        areaStyle: {
          color: ['#FFFFFF', '#F8FAFC']
        }
      },
      axisLine: {
        show: true,
        lineStyle: {
          color: '#CBD5E1',
          width: 1
        }
      },
      axisTick: { show: false },
      axisLabel: { show: false }
    },
    series: [{
      type: 'radar',
      symbol: 'circle',
      symbolSize: 5,
      lineStyle: {
        width: 2
      },
      emphasis: {
        lineStyle: { width: 3 },
        areaStyle: { opacity: 0.3 }
      },
      data: topStudents.map((s, idx) => ({
        name: s.student_name,
        value: [
          s.usual_score || 0,
          s.midterm_score || 0,
          s.final_score || 0,
          s.practice_score || 0
        ],
        lineStyle: {
          color: colorPalette[idx % colorPalette.length]
        },
        areaStyle: {
          color: colorPalette[idx % colorPalette.length],
          opacity: 0.12
        },
        itemStyle: {
          color: colorPalette[idx % colorPalette.length]
        }
      }))
    }]
  }
}

/**
 * 排名变化折线图配置
 * @param {Array} items - 排序后的成绩数据
 */
export function getRankTrendChart(items) {
  // 按排名排序
  const sorted = [...items].sort((a, b) => (a.rank || 999) - (b.rank || 999))

  return {
    title: {
      text: '成绩排名',
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 600,
        color: '#1E293B'
      }
    },
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        const data = params[0]
        const item = sorted[data.dataIndex]
        return `${item.student_name}<br/>排名: 第${item.rank}名<br/>总分: ${item.total_score}分`
      }
    },
    grid: {
      left: '12%',
      right: '5%',
      top: '15%',
      bottom: '20%'
    },
    xAxis: {
      type: 'category',
      data: sorted.map(s => s.student_name),
      axisLabel: {
        rotate: 45,
        color: '#64748B',
        fontSize: 11,
        interval: Math.floor(sorted.length / 10) // 超过10个学生时每隔几个显示一个
      },
      axisLine: {
        lineStyle: { color: '#E2E8F0' }
      }
    },
    yAxis: {
      type: 'value',
      name: '分数',
      nameTextStyle: {
        color: '#64748B',
        fontSize: 12
      },
      axisLabel: {
        color: '#64748B',
        fontSize: 12
      },
      axisLine: {
        lineStyle: { color: '#E2E8F0' }
      },
      splitLine: {
        lineStyle: { color: '#F1F5F9' }
      },
      min: 0,
      max: 100
    },
    series: [{
      type: 'line',
      data: sorted.map(s => s.total_score),
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(8, 145, 178, 0.25)' },
          { offset: 1, color: 'rgba(8, 145, 178, 0.02)' }
        ])
      },
      lineStyle: {
        color: PRIMARY_COLOR,
        width: 2.5
      },
      itemStyle: {
        color: PRIMARY_COLOR
      },
      label: {
        show: false
      }
    }]
  }
}

/**
 * 各单项成绩对比柱状图
 * @param {Object} byComponent - {usual: {avg, max, min}, ...}
 */
export function getComponentChart(byComponent) {
  const components = []
  const avgData = []
  const maxData = []
  const minData = []

  if (byComponent) {
    const names = {
      usual: '平时分',
      midterm: '期中分',
      final: '期末分',
      practice: '实验分'
    }

    for (const [key, name] of Object.entries(names)) {
      if (byComponent[key]) {
        components.push(name)
        avgData.push(byComponent[key].avg)
        maxData.push(byComponent[key].max)
        minData.push(byComponent[key].min)
      }
    }
  }

  if (components.length === 0) {
    return null
  }

  return {
    title: {
      text: '各单项成绩统计',
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 600,
        color: '#1E293B'
      }
    },
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        const idx = params[0].dataIndex
        return `${components[idx]}<br/>平均: ${avgData[idx]}分<br/>最高: ${maxData[idx]}分<br/>最低: ${minData[idx]}分`
      }
    },
    legend: {
      data: ['平均分', '最高分', '最低分'],
      bottom: 0,
      textStyle: {
        color: '#64748B',
        fontSize: 11
      }
    },
    grid: {
      left: '12%',
      right: '5%',
      top: '15%',
      bottom: '18%'
    },
    xAxis: {
      type: 'category',
      data: components,
      axisLabel: {
        color: '#64748B',
        fontSize: 12
      },
      axisLine: {
        lineStyle: { color: '#E2E8F0' }
      }
    },
    yAxis: {
      type: 'value',
      name: '分数',
      nameTextStyle: {
        color: '#64748B',
        fontSize: 12
      },
      axisLabel: {
        color: '#64748B',
        fontSize: 12
      },
      axisLine: {
        lineStyle: { color: '#E2E8F0' }
      },
      splitLine: {
        lineStyle: { color: '#F1F5F9' }
      },
      min: 0,
      max: 100
    },
    series: [
      {
        name: '平均分',
        type: 'bar',
        data: avgData,
        itemStyle: {
          color: PRIMARY_COLOR,
          borderRadius: [4, 4, 0, 0]
        },
        barWidth: '25%'
      },
      {
        name: '最高分',
        type: 'bar',
        data: maxData,
        itemStyle: {
          color: '#34D399',
          borderRadius: [4, 4, 0, 0]
        },
        barWidth: '25%'
      },
      {
        name: '最低分',
        type: 'bar',
        data: minData,
        itemStyle: {
          color: '#F59E0B',
          borderRadius: [4, 4, 0, 0]
        },
        barWidth: '25%'
      }
    ]
  }
}

/**
 * 创建/更新图表的Helper函数
 * @param {HTMLElement} el - DOM元素
 * @param {Object} option - ECharts配置
 * @returns {echarts.ECharts} chart实例
 */
export function createChart(el, option) {
  let chart = echarts.getInstanceByDom(el)
  if (!chart) {
    chart = echarts.init(el)
  }
  chart.setOption(option)
  return chart
}

/**
 * 销毁图表实例
 * @param {HTMLElement} el - DOM元素
 */
export function disposeChart(el) {
  const chart = echarts.getInstanceByDom(el)
  if (chart) {
    chart.dispose()
  }
}
