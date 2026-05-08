import * as echarts from 'echarts'
import logger from '@/utils/logger'

// ============================================
// AI小商 管理端 ECharts 图表配置
// 设计风格: 深色科技风 + 渐变效果
// ============================================

// 配色方案 - 科技感深色主题
const COLORS = {
  primary: '#0891B2',      // 青色 - 主色
  primaryLight: '#22D3EE', // 亮青 - 渐变
  success: '#059669',      // 薄荷绿 - 成功
  warning: '#F59E0B',      // 琥珀色 - 警告
  danger: '#EF4444',       // 红色 - 危险/强调
  purple: '#8B5CF6',       // 紫色 - 特色
  cyan: '#06B6D4',         // 青色 - 辅助
  bg: {
    dark: '#0F172A',       // 深色背景
    card: '#1E293B',       // 卡片背景
    border: '#334155'      // 边框色
  },
  text: {
    primary: '#F1F5F9',    // 主文字
    secondary: '#94A3B8',  // 次要文字
    muted: '#64748B'       // 弱化文字
  }
}

// 渐变色配置
const GRADIENTS = {
  primary: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
    { offset: 0, color: COLORS.primaryLight },
    { offset: 1, color: COLORS.primary }
  ]),
  success: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
    { offset: 0, color: '#34D399' },
    { offset: 1, color: COLORS.success }
  ]),
  warning: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
    { offset: 0, color: '#FBBF24' },
    { offset: 1, color: COLORS.warning }
  ]),
  danger: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
    { offset: 0, color: '#F87171' },
    { offset: 1, color: COLORS.danger }
  ])
}

// 通用主题配置
const BASE_THEME = {
  backgroundColor: 'transparent',
  textStyle: {
    fontFamily: "'Inter', 'Noto Sans SC', sans-serif",
    color: COLORS.text.secondary
  },
  tooltip: {
    backgroundColor: COLORS.bg.card,
    borderColor: COLORS.bg.border,
    textStyle: { color: COLORS.text.primary },
    extraCssText: 'border-radius: 8px; padding: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.3);'
  },
  axisLine: {
    lineStyle: { color: COLORS.bg.border }
  },
  splitLine: {
    lineStyle: { color: COLORS.bg.border, opacity: 0.5 }
  }
}

// ============================================
// 图表配置函数
// ============================================

/**
 * 水平柱状图 - 功能使用排行
 * @param {Array} data - [{name: string, value: number}]
 */
export function getBarChartOption(data) {
  logger.debug('[ECharts] Generating bar chart with', data?.length, 'items')

  return {
    ...BASE_THEME,
    grid: {
      left: '3%',
      right: '8%',
      bottom: '3%',
      top: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      axisLabel: {
        color: COLORS.text.secondary,
        formatter: (val) => val >= 1000 ? `${(val/1000).toFixed(0)}k` : val
      },
      splitLine: { lineStyle: { color: COLORS.bg.border, opacity: 0.3 } }
    },
    yAxis: {
      type: 'category',
      data: data.map(d => d.name),
      axisLabel: {
        color: COLORS.text.primary,
        fontSize: 13,
        width: 80,
        overflow: 'truncate'
      },
      axisLine: { lineStyle: { color: COLORS.bg.border } }
    },
    series: [{
      type: 'bar',
      data: data.map(d => ({
        value: d.value,
        itemStyle: {
          color: GRADIENTS.primary,
          borderRadius: [0, 6, 6, 0]
        }
      })),
      barWidth: '50%',
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowColor: 'rgba(8, 145, 178, 0.3)'
        }
      },
      label: {
        show: true,
        position: 'right',
        color: COLORS.text.secondary,
        fontSize: 12,
        formatter: (p) => p.value.toLocaleString()
      }
    }],
    animation: true,
    animationDuration: 800,
    animationEasing: 'cubicOut'
  }
}

/**
 * 饼图 - API调用统计
 * @param {Array} data - [{name: string, value: number}]
 */
export function getPieChartOption(data) {
  logger.debug('[ECharts] Generating pie chart with', data?.length, 'items')

  const pieColors = [
    COLORS.primary, COLORS.success, COLORS.warning,
    COLORS.purple, COLORS.cyan, COLORS.danger
  ]

  return {
    ...BASE_THEME,
    legend: {
      orient: 'vertical',
      right: '5%',
      top: 'center',
      textStyle: { color: COLORS.text.secondary },
      itemWidth: 12,
      itemHeight: 12,
      itemGap: 16
    },
    series: [{
      type: 'pie',
      radius: ['45%', '75%'],
      center: ['35%', '50%'],
      avoidLabelOverlap: true,
      itemStyle: {
        borderRadius: 4,
        borderColor: COLORS.bg.dark,
        borderWidth: 2
      },
      label: {
        show: false
      },
      emphasis: {
        label: {
          show: true,
          fontSize: 14,
          fontWeight: 'bold',
          color: COLORS.text.primary
        },
        scaleSize: 8
      },
      data: data.map((d, i) => ({
        value: d.value,
        name: d.name,
        itemStyle: { color: pieColors[i % pieColors.length] }
      }))
    }],
    animation: true,
    animationDuration: 1000,
    animationEasing: 'elasticOut'
  }
}

/**
 * 折线图 - 24小时活跃趋势
 * @param {Array} data - [{hour: number, count: number}]
 */
export function getLineChartOption(data) {
  logger.debug('[ECharts] Generating line chart with', data?.length, 'items')

  return {
    ...BASE_THEME,
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: data.map(d => `${d.hour}:00`),
      boundaryGap: false,
      axisLabel: {
        color: COLORS.text.secondary,
        interval: 2,
        rotate: 0
      },
      axisLine: { lineStyle: { color: COLORS.bg.border } },
      splitLine: { show: false }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        color: COLORS.text.secondary,
        formatter: (val) => val >= 1000 ? `${(val/1000).toFixed(0)}k` : val
      },
      splitLine: {
        lineStyle: { color: COLORS.bg.border, opacity: 0.3 }
      }
    },
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        const p = params[0]
        return `<div style="font-size: 13px;">
          <span style="color: ${COLORS.text.secondary}">${p.name}</span><br/>
          <span style="color: ${COLORS.primary}; font-weight: 600;">${p.value.toLocaleString()}</span>
          <span style="color: ${COLORS.text.muted}"> 人</span>
        </div>`
      }
    },
    series: [{
      type: 'line',
      data: data.map(d => d.count),
      smooth: 0.6,
      symbol: 'circle',
      symbolSize: 6,
      lineStyle: {
        color: COLORS.primary,
        width: 3,
        shadowColor: 'rgba(8, 145, 178, 0.4)',
        shadowBlur: 8
      },
      itemStyle: {
        color: COLORS.primaryLight,
        borderColor: COLORS.primary,
        borderWidth: 2
      },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(8, 145, 178, 0.25)' },
          { offset: 1, color: 'rgba(8, 145, 178, 0.02)' }
        ])
      },
      emphasis: {
        scale: true,
        scaleSize: 10
      }
    }],
    animation: true,
    animationDuration: 1200,
    animationEasing: 'cubicOut'
  }
}

/**
 * 环形进度图 - API失败率
 * @param {number} value - 失败率百分比 (0-100)
 */
export function getGaugeOption(value) {
  const getColor = (v) => {
    if (v > 5) return COLORS.danger
    if (v > 1) return COLORS.warning
    return COLORS.success
  }

  return {
    series: [{
      type: 'gauge',
      radius: '90%',
      center: ['50%', '50%'],
      startAngle: 220,
      endAngle: -40,
      min: 0,
      max: 10,
      splitNumber: 5,
      itemStyle: {
        color: getColor(value),
        shadowColor: `rgba(${value > 5 ? '239, 68, 68' : value > 1 ? '245, 158, 11' : '5, 150, 105'}, 0.5)`,
        shadowBlur: 10
      },
      progress: {
        show: true,
        width: 12,
        roundCap: true
      },
      pointer: { show: false },
      axisLine: {
        lineStyle: {
          width: 12,
          color: [[1, COLORS.bg.border]]
        },
        roundCap: true
      },
      axisTick: { show: false },
      splitLine: {
        length: 0,
        lineStyle: { width: 0 }
      },
      axisLabel: {
        distance: -30,
        color: COLORS.text.secondary,
        fontSize: 11,
        formatter: (v) => v.toFixed(1) + '%'
      },
      anchor: { show: false },
      title: { show: false },
      detail: {
        valueAnimation: true,
        fontSize: 28,
        fontWeight: 'bold',
        color: getColor(value),
        offsetCenter: [0, '10%'],
        formatter: (v) => v.toFixed(2) + '%'
      },
      data: [{ value: value }]
    }],
    animation: true,
    animationDuration: 1000
  }
}

// ============================================
// 仪表盘专用图表配置
// ============================================

/**
 * 获取仪表盘完整配置
 */
export function getDashboardTheme() {
  return {
    color: [
      COLORS.primary, COLORS.success, COLORS.warning,
      COLORS.danger, COLORS.purple, COLORS.cyan
    ],
    backgroundColor: 'transparent',
    textStyle: {
      fontFamily: "'Inter', 'Noto Sans SC', sans-serif"
    }
  }
}

// ============================================
// 导出配色常量（供组件使用）
// ============================================
export const dashboardColors = COLORS
export { COLORS as colors }