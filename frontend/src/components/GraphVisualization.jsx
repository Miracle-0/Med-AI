import React, { useEffect, useRef, useState } from 'react';
import * as echarts from 'echarts';
import { Spin } from 'antd';
import { ApartmentOutlined } from '@ant-design/icons';
import { graphAPI } from '../services/api';

const GraphVisualization = ({ textbookId, refreshKey }) => {
  const chartRef = useRef(null);
  const chartInstance = useRef(null);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState({ nodes: 0, edges: 0 });

  useEffect(() => {
    if (chartRef.current) {
      chartInstance.current = echarts.init(chartRef.current, null, { renderer: 'canvas' });
      const handleResize = () => chartInstance.current?.resize();
      window.addEventListener('resize', handleResize);
      return () => {
        window.removeEventListener('resize', handleResize);
        chartInstance.current?.dispose();
      };
    }
  }, []);

  useEffect(() => {
    if (textbookId) loadGraphData();
    else {
      chartInstance.current?.clear();
      setStats({ nodes: 0, edges: 0 });
    }
  }, [textbookId, refreshKey]);

  const loadGraphData = async () => {
    setLoading(true);
    try {
      const [nodesRes, edgesRes] = await Promise.all([
        graphAPI.getNodes(textbookId),
        graphAPI.getEdges(textbookId)
      ]);
      setStats({ nodes: nodesRes.data.length, edges: edgesRes.data.length });
      renderGraph(nodesRes.data, edgesRes.data);
    } catch (e) {
      console.error('加载图谱数据失败', e);
    }
    setLoading(false);
  };

  const categoryColors = {
    '核心概念': '#f0a030',
    '定理': '#60a5fa',
    '方法': '#a78bfa',
    '现象': '#4ade80',
    '免疫细胞功能': '#f472b6',
  };

  const renderGraph = (nodes, edges) => {
    if (!chartInstance.current) return;

    const categories = [...new Set(nodes.map(n => n.category))].map(name => ({
      name,
      itemStyle: { color: categoryColors[name] || '#f0a030' }
    }));
    const catIndex = Object.fromEntries(categories.map((c, i) => [c.name, i]));

    const graphNodes = nodes.map((node) => ({
      id: node.node_id,
      name: node.name,
      symbolSize: Math.max(20, Math.min(45, 15 + node.name.length * 2.5)),
      category: catIndex[node.category] ?? 0,
      itemStyle: {
        color: categoryColors[node.category] || '#f0a030',
        shadowColor: categoryColors[node.category] || '#f0a030',
        shadowBlur: 12,
      },
      label: {
        show: true, position: 'right',
        formatter: '{b}',
        fontSize: 11,
        color: '#e8dcc8',
        fontFamily: 'Noto Serif SC, serif',
      },
      tooltip: {
        formatter: `
          <div style="font-family:Noto Serif SC;max-width:280px">
            <div style="font-size:14px;font-weight:600;color:#f0a030;margin-bottom:6px">${node.name}</div>
            <div style="font-size:12px;color:#ccc;margin-bottom:4px">${node.definition}</div>
            <div style="font-size:11px;color:#888">
              <span style="color:${categoryColors[node.category] || '#f0a030'}">● ${node.category}</span>
              &nbsp;·&nbsp;${node.chapter_id?.split('_ch_')[1] || ''}
            </div>
          </div>
        `
      }
    }));

    const graphEdges = edges.map(edge => ({
      source: edge.source_node_id,
      target: edge.target_node_id,
      lineStyle: {
        type: edge.relation_type === 'prerequisite' ? 'solid' : 'dashed',
        width: edge.relation_type === 'prerequisite' ? 2 : 1,
        color: 'rgba(240, 160, 48, 0.2)',
        curveness: 0.2,
      },
      tooltip: {
        formatter: `<div style="font-size:12px;color:#ccc">${edge.description || edge.relation_type}</div>`
      }
    }));

    chartInstance.current.setOption({
      backgroundColor: 'transparent',
      tooltip: {
        backgroundColor: 'rgba(10, 14, 26, 0.95)',
        borderColor: 'rgba(240, 160, 48, 0.3)',
        borderWidth: 1,
        textStyle: { color: '#e8dcc8' },
        extraCssText: 'border-radius: 8px; backdrop-filter: blur(10px);',
      },
      legend: {
        data: categories.map(c => c.name),
        bottom: 16,
        textStyle: { color: 'rgba(232,220,200,0.6)', fontSize: 11, fontFamily: 'Noto Serif SC' },
        itemWidth: 10, itemHeight: 10,
        icon: 'circle',
      },
      animationDuration: 1500,
      animationEasingUpdate: 'quinticInOut',
      series: [{
        type: 'graph',
        layout: 'force',
        animation: true,
        roam: true,
        draggable: true,
        data: graphNodes,
        links: graphEdges,
        categories,
        force: {
          repulsion: 200,
          gravity: 0.08,
          edgeLength: [80, 160],
          layoutAnimation: true,
        },
        emphasis: {
          focus: 'adjacency',
          blurScope: 'coordinateSystem',
          lineStyle: { width: 4, color: 'rgba(240, 160, 48, 0.6)' },
          itemStyle: { shadowBlur: 25 },
        },
        lineStyle: { opacity: 0.6 },
      }]
    }, true);
  };

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Top bar */}
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '16px 24px 12px',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <ApartmentOutlined style={{ color: 'var(--accent)', fontSize: 16 }} />
          <span style={{
            fontFamily: 'var(--font-display)', fontSize: 15, fontWeight: 600,
            color: 'var(--text-primary)', letterSpacing: 2,
          }}>
            知识图谱
          </span>
        </div>
        {stats.nodes > 0 && (
          <div style={{
            display: 'flex', gap: 16, fontSize: 11,
            fontFamily: 'var(--font-mono)', color: 'var(--text-muted)',
          }}>
            <span><span style={{ color: 'var(--accent)' }}>{stats.nodes}</span> 知识点</span>
            <span><span style={{ color: 'var(--accent)' }}>{stats.edges}</span> 关系</span>
          </div>
        )}
      </div>

      {/* Chart area */}
      <div style={{ flex: 1, position: 'relative' }}>
        {loading ? (
          <div style={{
            display: 'flex', flexDirection: 'column',
            justifyContent: 'center', alignItems: 'center', height: '100%', gap: 16,
          }}>
            <Spin size="large" />
            <span style={{ color: 'var(--text-muted)', fontFamily: 'var(--font-display)', fontSize: 13 }}>
              加载图谱数据...
            </span>
          </div>
        ) : textbookId ? (
          <div ref={chartRef} style={{ height: '100%', width: '100%' }} />
        ) : (
          <div style={{
            display: 'flex', flexDirection: 'column',
            justifyContent: 'center', alignItems: 'center', height: '100%',
          }}>
            <div style={{
              width: 80, height: 80, borderRadius: 20,
              background: 'var(--bg-glass)',
              border: '1px solid var(--border-subtle)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              marginBottom: 20, fontSize: 32, opacity: 0.3,
            }}>
              🧠
            </div>
            <div style={{
              fontFamily: 'var(--font-display)', fontSize: 15,
              color: 'var(--text-muted)', letterSpacing: 2,
            }}>
              选择教材以查看知识图谱
            </div>
            <div style={{
              fontSize: 12, color: 'var(--text-muted)', marginTop: 8, opacity: 0.5,
            }}>
              或点击右上角加载演示数据
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default GraphVisualization;
