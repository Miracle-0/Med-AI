import React, { useEffect, useRef, useState } from 'react';
import * as echarts from 'echarts';
import { Spin, Empty } from 'antd';
import { graphAPI } from '../services/api';

const GraphVisualization = ({ textbookId }) => {
  const chartRef = useRef(null);
  const chartInstance = useRef(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (chartRef.current) {
      chartInstance.current = echarts.init(chartRef.current);
    }
    return () => {
      chartInstance.current?.dispose();
    };
  }, []);

  useEffect(() => {
    if (textbookId) {
      loadGraphData();
    }
  }, [textbookId]);

  const loadGraphData = async () => {
    setLoading(true);
    try {
      const [nodesRes, edgesRes] = await Promise.all([
        graphAPI.getNodes(textbookId),
        graphAPI.getEdges(textbookId)
      ]);
      renderGraph(nodesRes.data, edgesRes.data);
    } catch (error) {
      console.error('加载图谱数据失败', error);
    }
    setLoading(false);
  };

  const renderGraph = (nodes, edges) => {
    if (!chartInstance.current) return;

    const graphNodes = nodes.map((node) => ({
      id: node.node_id,
      name: node.name,
      symbolSize: 30,
      category: node.category === '核心概念' ? 0 : node.category === '定理' ? 1 : 2,
      itemStyle: {
        color: node.textbook_id?.includes('01') ? '#5470c6' :
               node.textbook_id?.includes('02') ? '#91cc75' : '#fac858'
      },
      tooltip: {
        formatter: `<b>${node.name}</b><br/>定义：${node.definition}<br/>章节：${node.chapter_id}<br/>页码：${node.page}`
      }
    }));

    const graphEdges = edges.map(edge => ({
      source: edge.source_node_id,
      target: edge.target_node_id,
      lineStyle: {
        type: edge.relation_type === 'prerequisite' ? 'solid' : 'dashed'
      }
    }));

    const option = {
      tooltip: {},
      legend: {
        data: ['核心概念', '定理', '方法']
      },
      series: [{
        type: 'graph',
        layout: 'force',
        animation: true,
        label: {
          show: true,
          position: 'right',
          formatter: '{b}'
        },
        roam: true,
        draggable: true,
        data: graphNodes,
        links: graphEdges,
        categories: [
          { name: '核心概念' },
          { name: '定理' },
          { name: '方法' }
        ],
        force: {
          repulsion: 100,
          gravity: 0.1,
          edgeLength: 50,
          layoutAnimation: true
        },
        emphasis: {
          focus: 'adjacency',
          lineStyle: {
            width: 10
          }
        }
      }]
    };

    chartInstance.current.setOption(option);
  };

  return (
    <div style={{ height: '100%' }}>
      <h3 style={{ marginBottom: 16 }}>知识图谱可视化</h3>
      {loading ? (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px' }}>
          <Spin size="large" />
        </div>
      ) : textbookId ? (
        <div ref={chartRef} style={{ height: '600px', width: '100%' }} />
      ) : (
        <Empty description="请选择教材" />
      )}
    </div>
  );
};

export default GraphVisualization;
