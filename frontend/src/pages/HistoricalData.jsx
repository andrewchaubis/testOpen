import React, { useState, useEffect } from 'react'
import {
  Card,
  Row,
  Col,
  Table,
  DatePicker,
  Select,
  Button,
  Typography,
  Tag,
  Space,
  Statistic,
  Timeline,
  Descriptions
} from 'antd'
import {
  HistoryOutlined,
  EnvironmentOutlined,
  CalendarOutlined,
  BarChartOutlined
} from '@ant-design/icons'
import Plot from 'react-plotly.js'
import { apiService } from '../services/apiService'
import dayjs from 'dayjs'

const { Title, Text } = Typography
const { RangePicker } = DatePicker
const { Option } = Select

const HistoricalData = () => {
  const [loading, setLoading] = useState(false)
  const [historicalEvents, setHistoricalEvents] = useState([])
  const [selectedDistrict, setSelectedDistrict] = useState(null)
  const [dateRange, setDateRange] = useState([
    dayjs().subtract(10, 'year'),
    dayjs()
  ])
  const [districts] = useState([
    'Kota Bharu', 'Kuala Krai', 'Machang', 'Pasir Mas', 
    'Tanah Merah', 'Bachok', 'Tumpat', 'Pasir Puteh', 
    'Gua Musang', 'Jeli'
  ])

  useEffect(() => {
    loadHistoricalData()
  }, [])

  const loadHistoricalData = async () => {
    setLoading(true)
    try {
      // Mock historical data for demo
      const mockEvents = [
        {
          key: '1',
          date: '2014-12-15',
          district: 'Kuala Krai',
          severity: 'extreme',
          affected_area_km2: 500,
          displaced_people: 15000,
          economic_loss_myr: 500000000,
          max_depth_m: 3.5,
          duration_days: 14,
          description: 'Worst flooding in decades, entire district submerged'
        },
        {
          key: '2',
          date: '2014-12-20',
          district: 'Kota Bharu',
          severity: 'high',
          affected_area_km2: 200,
          displaced_people: 8000,
          economic_loss_myr: 200000000,
          max_depth_m: 2.1,
          duration_days: 10,
          description: 'Major flooding in urban areas'
        },
        {
          key: '3',
          date: '2017-01-03',
          district: 'Pasir Mas',
          severity: 'high',
          affected_area_km2: 150,
          displaced_people: 5000,
          economic_loss_myr: 150000000,
          max_depth_m: 1.8,
          duration_days: 7,
          description: 'Significant river overflow'
        },
        {
          key: '4',
          date: '2019-12-28',
          district: 'Machang',
          severity: 'medium',
          affected_area_km2: 80,
          displaced_people: 2000,
          economic_loss_myr: 50000000,
          max_depth_m: 1.2,
          duration_days: 5,
          description: 'Moderate flooding in rural areas'
        },
        {
          key: '5',
          date: '2021-01-15',
          district: 'Tanah Merah',
          severity: 'medium',
          affected_area_km2: 100,
          displaced_people: 3000,
          economic_loss_myr: 75000000,
          max_depth_m: 1.5,
          duration_days: 6,
          description: 'Flash flooding from heavy rainfall'
        },
        {
          key: '6',
          date: '2022-11-20',
          district: 'Kota Bharu',
          severity: 'low',
          affected_area_km2: 50,
          displaced_people: 500,
          economic_loss_myr: 10000000,
          max_depth_m: 0.8,
          duration_days: 3,
          description: 'Minor urban flooding'
        }
      ]

      setHistoricalEvents(mockEvents)
    } catch (error) {
      console.error('Error loading historical data:', error)
    } finally {
      setLoading(false)
    }
  }

  const getSeverityColor = (severity) => {
    const colors = {
      low: 'green',
      medium: 'orange',
      high: 'red',
      extreme: 'purple'
    }
    return colors[severity] || 'default'
  }

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-MY', {
      style: 'currency',
      currency: 'MYR',
      notation: 'compact',
      maximumFractionDigits: 1
    }).format(amount)
  }

  const columns = [
    {
      title: 'Date',
      dataIndex: 'date',
      key: 'date',
      render: (date) => dayjs(date).format('DD/MM/YYYY'),
      sorter: (a, b) => dayjs(a.date).unix() - dayjs(b.date).unix(),
    },
    {
      title: 'District',
      dataIndex: 'district',
      key: 'district',
      filters: districts.map(d => ({ text: d, value: d })),
      onFilter: (value, record) => record.district === value,
    },
    {
      title: 'Severity',
      dataIndex: 'severity',
      key: 'severity',
      render: (severity) => (
        <Tag color={getSeverityColor(severity)}>
          {severity.toUpperCase()}
        </Tag>
      ),
      filters: [
        { text: 'Low', value: 'low' },
        { text: 'Medium', value: 'medium' },
        { text: 'High', value: 'high' },
        { text: 'Extreme', value: 'extreme' },
      ],
      onFilter: (value, record) => record.severity === value,
    },
    {
      title: 'Max Depth',
      dataIndex: 'max_depth_m',
      key: 'max_depth_m',
      render: (depth) => `${depth}m`,
      sorter: (a, b) => a.max_depth_m - b.max_depth_m,
    },
    {
      title: 'Duration',
      dataIndex: 'duration_days',
      key: 'duration_days',
      render: (days) => `${days} days`,
      sorter: (a, b) => a.duration_days - b.duration_days,
    },
    {
      title: 'Displaced People',
      dataIndex: 'displaced_people',
      key: 'displaced_people',
      render: (people) => people.toLocaleString(),
      sorter: (a, b) => a.displaced_people - b.displaced_people,
    },
    {
      title: 'Economic Loss',
      dataIndex: 'economic_loss_myr',
      key: 'economic_loss_myr',
      render: (loss) => formatCurrency(loss),
      sorter: (a, b) => a.economic_loss_myr - b.economic_loss_myr,
    },
  ]

  // Filter data based on selections
  const filteredEvents = historicalEvents.filter(event => {
    const eventDate = dayjs(event.date)
    const inDateRange = eventDate.isAfter(dateRange[0]) && eventDate.isBefore(dateRange[1])
    const inDistrict = !selectedDistrict || event.district === selectedDistrict
    return inDateRange && inDistrict
  })

  // Calculate statistics
  const totalEvents = filteredEvents.length
  const totalDisplaced = filteredEvents.reduce((sum, event) => sum + event.displaced_people, 0)
  const totalLoss = filteredEvents.reduce((sum, event) => sum + event.economic_loss_myr, 0)
  const avgDepth = filteredEvents.length > 0 
    ? filteredEvents.reduce((sum, event) => sum + event.max_depth_m, 0) / filteredEvents.length 
    : 0

  // Chart data
  const timelineData = {
    x: filteredEvents.map(event => event.date),
    y: filteredEvents.map(event => event.max_depth_m),
    type: 'scatter',
    mode: 'markers+lines',
    name: 'Flood Depth',
    marker: {
      size: filteredEvents.map(event => event.displaced_people / 1000),
      color: filteredEvents.map(event => {
        const colors = { low: '#52c41a', medium: '#faad14', high: '#ff7a45', extreme: '#ff4d4f' }
        return colors[event.severity]
      }),
      sizemode: 'diameter',
      sizeref: 2
    }
  }

  const severityDistribution = {
    labels: ['Low', 'Medium', 'High', 'Extreme'],
    values: [
      filteredEvents.filter(e => e.severity === 'low').length,
      filteredEvents.filter(e => e.severity === 'medium').length,
      filteredEvents.filter(e => e.severity === 'high').length,
      filteredEvents.filter(e => e.severity === 'extreme').length,
    ],
    type: 'pie',
    marker: {
      colors: ['#52c41a', '#faad14', '#ff7a45', '#ff4d4f']
    }
  }

  return (
    <div>
      <Title level={2}>Historical Flood Data</Title>
      <Text type="secondary">
        Analysis of past flood events in Kelantan to understand patterns and trends
      </Text>

      {/* Filters */}
      <Card style={{ marginTop: '24px', marginBottom: '24px' }}>
        <Row gutter={[16, 16]} align="middle">
          <Col xs={24} sm={8}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <Text strong>Date Range:</Text>
              <RangePicker
                value={dateRange}
                onChange={setDateRange}
                style={{ width: '100%' }}
              />
            </Space>
          </Col>
          
          <Col xs={24} sm={8}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <Text strong>District:</Text>
              <Select
                style={{ width: '100%' }}
                placeholder="All Districts"
                allowClear
                value={selectedDistrict}
                onChange={setSelectedDistrict}
              >
                {districts.map(district => (
                  <Option key={district} value={district}>
                    {district}
                  </Option>
                ))}
              </Select>
            </Space>
          </Col>
          
          <Col xs={24} sm={8}>
            <Button
              type="primary"
              icon={<HistoryOutlined />}
              onClick={loadHistoricalData}
              loading={loading}
              style={{ marginTop: '24px' }}
            >
              Refresh Data
            </Button>
          </Col>
        </Row>
      </Card>

      {/* Summary Statistics */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={12} sm={6}>
          <Card>
            <Statistic
              title="Total Events"
              value={totalEvents}
              prefix={<CalendarOutlined />}
            />
          </Card>
        </Col>
        
        <Col xs={12} sm={6}>
          <Card>
            <Statistic
              title="People Displaced"
              value={totalDisplaced}
              formatter={(value) => value.toLocaleString()}
              prefix={<EnvironmentOutlined />}
            />
          </Card>
        </Col>
        
        <Col xs={12} sm={6}>
          <Card>
            <Statistic
              title="Economic Loss"
              value={formatCurrency(totalLoss)}
              prefix={<BarChartOutlined />}
            />
          </Card>
        </Col>
        
        <Col xs={12} sm={6}>
          <Card>
            <Statistic
              title="Avg. Depth"
              value={avgDepth.toFixed(1)}
              suffix="m"
            />
          </Card>
        </Col>
      </Row>

      {/* Charts */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} lg={16}>
          <Card title="Flood Events Timeline" size="small">
            <Plot
              data={[timelineData]}
              layout={{
                width: '100%',
                height: 400,
                margin: { l: 50, r: 50, t: 50, b: 50 },
                xaxis: { title: 'Date' },
                yaxis: { title: 'Max Flood Depth (m)' },
                hovermode: 'closest'
              }}
              config={{ responsive: true, displayModeBar: false }}
            />
            <Text type="secondary" style={{ fontSize: '12px' }}>
              * Bubble size represents number of displaced people
            </Text>
          </Card>
        </Col>
        
        <Col xs={24} lg={8}>
          <Card title="Severity Distribution" size="small">
            <Plot
              data={[severityDistribution]}
              layout={{
                width: '100%',
                height: 400,
                margin: { l: 50, r: 50, t: 50, b: 50 }
              }}
              config={{ responsive: true, displayModeBar: false }}
            />
          </Card>
        </Col>
      </Row>

      {/* Historical Events Table */}
      <Card title="Historical Flood Events" size="small">
        <Table
          columns={columns}
          dataSource={filteredEvents}
          loading={loading}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => 
              `${range[0]}-${range[1]} of ${total} events`
          }}
          expandable={{
            expandedRowRender: (record) => (
              <Descriptions bordered column={2} size="small">
                <Descriptions.Item label="Description" span={2}>
                  {record.description}
                </Descriptions.Item>
                <Descriptions.Item label="Affected Area">
                  {record.affected_area_km2} km²
                </Descriptions.Item>
                <Descriptions.Item label="Duration">
                  {record.duration_days} days
                </Descriptions.Item>
                <Descriptions.Item label="Max Depth">
                  {record.max_depth_m}m
                </Descriptions.Item>
                <Descriptions.Item label="People Displaced">
                  {record.displaced_people.toLocaleString()}
                </Descriptions.Item>
              </Descriptions>
            ),
          }}
        />
      </Card>

      {/* Major Events Timeline */}
      <Card title="Major Flood Events Timeline" style={{ marginTop: '24px' }}>
        <Timeline
          items={filteredEvents
            .filter(event => event.severity === 'high' || event.severity === 'extreme')
            .sort((a, b) => dayjs(b.date).unix() - dayjs(a.date).unix())
            .map(event => ({
              color: getSeverityColor(event.severity),
              children: (
                <div>
                  <Title level={5}>
                    {dayjs(event.date).format('MMMM DD, YYYY')} - {event.district}
                  </Title>
                  <Tag color={getSeverityColor(event.severity)}>
                    {event.severity.toUpperCase()}
                  </Tag>
                  <p>{event.description}</p>
                  <Space>
                    <Text type="secondary">Depth: {event.max_depth_m}m</Text>
                    <Text type="secondary">Duration: {event.duration_days} days</Text>
                    <Text type="secondary">Displaced: {event.displaced_people.toLocaleString()}</Text>
                  </Space>
                </div>
              )
            }))}
        />
      </Card>
    </div>
  )
}

export default HistoricalData