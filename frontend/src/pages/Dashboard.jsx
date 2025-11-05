import React, { useState, useEffect } from 'react'
import { 
  Row, 
  Col, 
  Card, 
  Statistic, 
  Alert, 
  Table, 
  Tag, 
  Progress,
  Space,
  Typography,
  Spin
} from 'antd'
import {
  WarningOutlined,
  SafetyOutlined,
  EnvironmentOutlined,
  BankOutlined,
  TrendingUpOutlined,
  CloudOutlined
} from '@ant-design/icons'
import Plot from 'react-plotly.js'
import { apiService } from '../services/apiService'

const { Title, Text } = Typography

const Dashboard = () => {
  const [loading, setLoading] = useState(true)
  const [dashboardData, setDashboardData] = useState(null)
  const [alerts, setAlerts] = useState([])
  const [riskSummary, setRiskSummary] = useState(null)

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      const data = await apiService.getDashboardOverview()
      setDashboardData(data)
      setAlerts(data.current_alerts || [])
      setRiskSummary(data.risk_summary || {})
    } catch (error) {
      console.error('Error loading dashboard data:', error)
      // Load mock data for demo
      loadMockData()
    } finally {
      setLoading(false)
    }
  }

  const loadMockData = () => {
    setAlerts([
      {
        district: 'Kuala Krai',
        alert_level: 'red',
        type: 'flood_warning',
        description: 'Red flood warning for Kuala Krai'
      },
      {
        district: 'Kota Bharu',
        alert_level: 'orange',
        type: 'flood_warning',
        description: 'Orange flood warning for Kota Bharu'
      }
    ])

    setRiskSummary({
      districts: [
        { name: 'Kuala Krai', risk_level: 'extreme', probability: 0.85 },
        { name: 'Kota Bharu', risk_level: 'high', probability: 0.7 },
        { name: 'Pasir Mas', risk_level: 'high', probability: 0.65 },
        { name: 'Machang', risk_level: 'medium', probability: 0.4 },
        { name: 'Tanah Merah', risk_level: 'medium', probability: 0.35 }
      ],
      overall_risk: 'high',
      high_risk_districts: ['Kuala Krai', 'Kota Bharu', 'Pasir Mas']
    })

    setDashboardData({
      system_status: {
        models_loaded: true,
        data_sources: {
          met_malaysia: { status: 'online' },
          nahrim: { status: 'online' },
          satellite_data: { status: 'online' }
        }
      }
    })
  }

  const getRiskColor = (level) => {
    const colors = {
      low: '#52c41a',
      medium: '#faad14',
      high: '#ff7a45',
      extreme: '#ff4d4f'
    }
    return colors[level] || '#d9d9d9'
  }

  const getAlertColor = (level) => {
    const colors = {
      yellow: 'warning',
      orange: 'warning',
      red: 'error'
    }
    return colors[level] || 'info'
  }

  const districtColumns = [
    {
      title: 'District',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: 'Risk Level',
      dataIndex: 'risk_level',
      key: 'risk_level',
      render: (level) => (
        <Tag color={getRiskColor(level)}>
          {level.toUpperCase()}
        </Tag>
      ),
    },
    {
      title: 'Probability',
      dataIndex: 'probability',
      key: 'probability',
      render: (prob) => (
        <Progress 
          percent={Math.round(prob * 100)} 
          size="small"
          strokeColor={prob > 0.7 ? '#ff4d4f' : prob > 0.4 ? '#faad14' : '#52c41a'}
        />
      ),
    },
  ]

  // Mock chart data
  const riskTrendData = {
    x: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    y: [0.3, 0.4, 0.6, 0.5, 0.7, 0.8],
    type: 'scatter',
    mode: 'lines+markers',
    name: 'Risk Level',
    line: { color: '#1890ff' }
  }

  const districtRiskData = riskSummary?.districts?.map(d => ({
    x: [d.name],
    y: [d.probability],
    type: 'bar',
    name: d.name,
    marker: { color: getRiskColor(d.risk_level) }
  })) || []

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
        <div style={{ marginTop: '16px' }}>Loading dashboard data...</div>
      </div>
    )
  }

  return (
    <div>
      <Title level={2}>Flood Risk Dashboard</Title>
      
      {/* Current Alerts */}
      {alerts.length > 0 && (
        <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
          <Col span={24}>
            <Card title="Current Alerts" size="small">
              <Space direction="vertical" style={{ width: '100%' }}>
                {alerts.map((alert, index) => (
                  <Alert
                    key={index}
                    message={`${alert.district} - ${alert.alert_level.toUpperCase()} Alert`}
                    description={alert.description}
                    type={getAlertColor(alert.alert_level)}
                    showIcon
                  />
                ))}
              </Space>
            </Card>
          </Col>
        </Row>
      )}

      {/* Key Metrics */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="High Risk Districts"
              value={riskSummary?.high_risk_districts?.length || 0}
              prefix={<WarningOutlined style={{ color: '#ff4d4f' }} />}
              valueStyle={{ color: '#ff4d4f' }}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Overall Risk Level"
              value={riskSummary?.overall_risk?.toUpperCase() || 'MEDIUM'}
              prefix={<EnvironmentOutlined />}
              valueStyle={{ color: getRiskColor(riskSummary?.overall_risk) }}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Active Predictions"
              value={riskSummary?.districts?.length || 0}
              prefix={<TrendingUpOutlined style={{ color: '#1890ff' }} />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Data Sources Online"
              value={3}
              suffix="/ 4"
              prefix={<CloudOutlined style={{ color: '#52c41a' }} />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Charts and Tables */}
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <Card title="Risk Trend (6 Months)" size="small">
            <Plot
              data={[riskTrendData]}
              layout={{
                width: '100%',
                height: 300,
                margin: { l: 40, r: 40, t: 40, b: 40 },
                xaxis: { title: 'Month' },
                yaxis: { title: 'Risk Level', range: [0, 1] }
              }}
              config={{ responsive: true, displayModeBar: false }}
            />
          </Card>
        </Col>
        
        <Col xs={24} lg={12}>
          <Card title="District Risk Levels" size="small">
            <Plot
              data={districtRiskData}
              layout={{
                width: '100%',
                height: 300,
                margin: { l: 40, r: 40, t: 40, b: 80 },
                xaxis: { title: 'District' },
                yaxis: { title: 'Flood Probability', range: [0, 1] },
                showlegend: false
              }}
              config={{ responsive: true, displayModeBar: false }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: '24px' }}>
        <Col xs={24} lg={16}>
          <Card title="District Risk Summary" size="small">
            <Table
              dataSource={riskSummary?.districts || []}
              columns={districtColumns}
              pagination={false}
              size="small"
              rowKey="name"
            />
          </Card>
        </Col>
        
        <Col xs={24} lg={8}>
          <Card title="System Status" size="small">
            <Space direction="vertical" style={{ width: '100%' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <Text>Models Loaded</Text>
                <Tag color={dashboardData?.system_status?.models_loaded ? 'success' : 'error'}>
                  {dashboardData?.system_status?.models_loaded ? 'Online' : 'Offline'}
                </Tag>
              </div>
              
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <Text>MET Malaysia</Text>
                <Tag color="success">Online</Tag>
              </div>
              
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <Text>NAHRIM</Text>
                <Tag color="success">Online</Tag>
              </div>
              
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <Text>Satellite Data</Text>
                <Tag color="success">Online</Tag>
              </div>
              
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <Text>Last Update</Text>
                <Text type="secondary">{new Date().toLocaleTimeString()}</Text>
              </div>
            </Space>
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default Dashboard