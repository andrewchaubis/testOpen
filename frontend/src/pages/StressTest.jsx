import React, { useState } from 'react'
import {
  Card,
  Row,
  Col,
  Form,
  Select,
  Button,
  InputNumber,
  Typography,
  Result,
  Descriptions,
  Progress,
  Table,
  Tag,
  Space,
  Alert,
  Statistic
} from 'antd'
import {
  ExperimentOutlined,
  BankOutlined,
  WarningOutlined,
  TrendingUpOutlined
} from '@ant-design/icons'
import Plot from 'react-plotly.js'
import { apiService } from '../services/apiService'

const { Title, Text } = Typography
const { Option } = Select

const StressTest = () => {
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState(null)

  const scenarios = [
    {
      value: '100_year_flood',
      label: '100-Year Flood Event',
      description: 'Extreme flooding with 1% annual probability'
    },
    {
      value: 'river_overflow',
      label: 'Major River Overflow',
      description: 'Significant river flooding affecting multiple districts'
    },
    {
      value: 'coastal_surge',
      label: 'Coastal Storm Surge',
      description: 'Storm surge affecting coastal areas'
    },
    {
      value: 'prolonged_monsoon',
      label: 'Extended Monsoon Season',
      description: 'Prolonged heavy rainfall over multiple weeks'
    }
  ]

  const handleSubmit = async (values) => {
    setLoading(true)
    try {
      // Mock stress test results for demo
      const mockResults = {
        scenario: values.scenario,
        severity: values.severity || 'moderate',
        portfolio_size: values.portfolio_size,
        results: {
          portfolio_summary: {
            total_loans: values.portfolio_size,
            total_exposure: values.portfolio_size * 400000, // Average loan size
            total_asset_value: values.portfolio_size * 600000 // Average asset value
          },
          impact_metrics: {
            total_defaults: Math.floor(values.portfolio_size * 0.15),
            default_rate: 0.15,
            default_exposure: values.portfolio_size * 400000 * 0.15,
            loss_rate: 0.12,
            total_damage: values.portfolio_size * 600000 * 0.25,
            damage_rate: 0.25
          },
          risk_distribution: {
            low: Math.floor(values.portfolio_size * 0.3),
            medium: Math.floor(values.portfolio_size * 0.4),
            high: Math.floor(values.portfolio_size * 0.2),
            extreme: Math.floor(values.portfolio_size * 0.1)
          },
          capital_impact: {
            expected_loss: values.portfolio_size * 400000 * 0.12,
            capital_requirement: values.portfolio_size * 400000 * 0.12 * 8,
            capital_ratio_impact: 0.096
          },
          recommendations: [
            'Increase capital reserves by 15%',
            'Implement enhanced flood risk monitoring',
            'Consider geographic diversification',
            'Review insurance requirements for high-risk areas',
            'Develop early warning systems'
          ]
        }
      }

      setResults(mockResults)
    } catch (error) {
      console.error('Error running stress test:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-MY', {
      style: 'currency',
      currency: 'MYR',
      notation: 'compact',
      maximumFractionDigits: 1
    }).format(amount)
  }

  const riskDistributionData = results ? [
    {
      x: ['Low', 'Medium', 'High', 'Extreme'],
      y: [
        results.results.risk_distribution.low,
        results.results.risk_distribution.medium,
        results.results.risk_distribution.high,
        results.results.risk_distribution.extreme
      ],
      type: 'bar',
      marker: {
        color: ['#52c41a', '#faad14', '#ff7a45', '#ff4d4f']
      }
    }
  ] : []

  const impactMetricsData = results ? [
    {
      labels: ['Performing Loans', 'Defaulted Loans'],
      values: [
        results.results.portfolio_summary.total_loans - results.results.impact_metrics.total_defaults,
        results.results.impact_metrics.total_defaults
      ],
      type: 'pie',
      marker: {
        colors: ['#52c41a', '#ff4d4f']
      }
    }
  ] : []

  return (
    <div>
      <Title level={2}>Climate Stress Testing</Title>
      <Text type="secondary">
        Assess systemic impact of extreme flood scenarios on loan portfolios
      </Text>

      <Row gutter={[24, 24]} style={{ marginTop: '24px' }}>
        <Col xs={24} lg={8}>
          <Card title="Stress Test Configuration" icon={<ExperimentOutlined />}>
            <Form
              form={form}
              layout="vertical"
              onFinish={handleSubmit}
              initialValues={{
                portfolio_size: 1000,
                severity: 'moderate'
              }}
            >
              <Form.Item
                name="scenario"
                label="Stress Scenario"
                rules={[{ required: true, message: 'Please select a scenario' }]}
              >
                <Select placeholder="Select stress scenario">
                  {scenarios.map(scenario => (
                    <Option key={scenario.value} value={scenario.value}>
                      <div>
                        <div>{scenario.label}</div>
                        <Text type="secondary" style={{ fontSize: '12px' }}>
                          {scenario.description}
                        </Text>
                      </div>
                    </Option>
                  ))}
                </Select>
              </Form.Item>

              <Form.Item
                name="severity"
                label="Severity Level"
              >
                <Select>
                  <Option value="mild">Mild</Option>
                  <Option value="moderate">Moderate</Option>
                  <Option value="severe">Severe</Option>
                  <Option value="extreme">Extreme</Option>
                </Select>
              </Form.Item>

              <Form.Item
                name="portfolio_size"
                label="Portfolio Size (Number of Loans)"
                rules={[{ required: true, message: 'Please enter portfolio size' }]}
              >
                <InputNumber
                  style={{ width: '100%' }}
                  min={100}
                  max={100000}
                  step={100}
                  formatter={value => `${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                  parser={value => value.replace(/,/g, '')}
                />
              </Form.Item>

              <Form.Item
                name="region"
                label="Region"
                initialValue="kelantan"
              >
                <Select disabled>
                  <Option value="kelantan">Kelantan</Option>
                </Select>
              </Form.Item>

              <Button
                type="primary"
                htmlType="submit"
                loading={loading}
                block
                icon={<ExperimentOutlined />}
              >
                Run Stress Test
              </Button>
            </Form>
          </Card>
        </Col>

        <Col xs={24} lg={16}>
          {results ? (
            <Space direction="vertical" style={{ width: '100%' }} size="large">
              {/* Summary Metrics */}
              <Card title="Stress Test Results Summary">
                <Row gutter={[16, 16]}>
                  <Col xs={12} sm={6}>
                    <Statistic
                      title="Total Defaults"
                      value={results.results.impact_metrics.total_defaults}
                      suffix={`/ ${results.results.portfolio_summary.total_loans}`}
                      valueStyle={{ color: '#ff4d4f' }}
                    />
                  </Col>
                  <Col xs={12} sm={6}>
                    <Statistic
                      title="Default Rate"
                      value={results.results.impact_metrics.default_rate * 100}
                      suffix="%"
                      precision={1}
                      valueStyle={{ color: '#ff4d4f' }}
                    />
                  </Col>
                  <Col xs={12} sm={6}>
                    <Statistic
                      title="Expected Loss"
                      value={formatCurrency(results.results.capital_impact.expected_loss)}
                      valueStyle={{ color: '#ff4d4f' }}
                    />
                  </Col>
                  <Col xs={12} sm={6}>
                    <Statistic
                      title="Capital Impact"
                      value={results.results.capital_impact.capital_ratio_impact * 100}
                      suffix="%"
                      precision={1}
                      valueStyle={{ color: '#ff4d4f' }}
                    />
                  </Col>
                </Row>
              </Card>

              {/* Portfolio Impact */}
              <Row gutter={[16, 16]}>
                <Col xs={24} md={12}>
                  <Card title="Risk Distribution" size="small">
                    <Plot
                      data={riskDistributionData}
                      layout={{
                        width: '100%',
                        height: 300,
                        margin: { l: 40, r: 40, t: 40, b: 40 },
                        xaxis: { title: 'Risk Level' },
                        yaxis: { title: 'Number of Loans' }
                      }}
                      config={{ responsive: true, displayModeBar: false }}
                    />
                  </Card>
                </Col>

                <Col xs={24} md={12}>
                  <Card title="Portfolio Performance" size="small">
                    <Plot
                      data={impactMetricsData}
                      layout={{
                        width: '100%',
                        height: 300,
                        margin: { l: 40, r: 40, t: 40, b: 40 }
                      }}
                      config={{ responsive: true, displayModeBar: false }}
                    />
                  </Card>
                </Col>
              </Row>

              {/* Detailed Impact */}
              <Card title="Detailed Impact Assessment">
                <Row gutter={[16, 16]}>
                  <Col xs={24} md={12}>
                    <Title level={5}>Portfolio Summary</Title>
                    <Descriptions bordered column={1} size="small">
                      <Descriptions.Item label="Total Loans">
                        {results.results.portfolio_summary.total_loans.toLocaleString()}
                      </Descriptions.Item>
                      <Descriptions.Item label="Total Exposure">
                        {formatCurrency(results.results.portfolio_summary.total_exposure)}
                      </Descriptions.Item>
                      <Descriptions.Item label="Total Asset Value">
                        {formatCurrency(results.results.portfolio_summary.total_asset_value)}
                      </Descriptions.Item>
                    </Descriptions>
                  </Col>

                  <Col xs={24} md={12}>
                    <Title level={5}>Impact Metrics</Title>
                    <Descriptions bordered column={1} size="small">
                      <Descriptions.Item label="Default Exposure">
                        {formatCurrency(results.results.impact_metrics.default_exposure)}
                      </Descriptions.Item>
                      <Descriptions.Item label="Loss Rate">
                        {(results.results.impact_metrics.loss_rate * 100).toFixed(1)}%
                      </Descriptions.Item>
                      <Descriptions.Item label="Total Damage">
                        {formatCurrency(results.results.impact_metrics.total_damage)}
                      </Descriptions.Item>
                      <Descriptions.Item label="Damage Rate">
                        {(results.results.impact_metrics.damage_rate * 100).toFixed(1)}%
                      </Descriptions.Item>
                    </Descriptions>
                  </Col>
                </Row>
              </Card>

              {/* Capital Impact */}
              <Card title="Capital Impact Analysis" icon={<BankOutlined />}>
                <Alert
                  message="Capital Adequacy Impact"
                  description={`The stress scenario would require additional capital of ${formatCurrency(results.results.capital_impact.capital_requirement)} to maintain regulatory ratios.`}
                  type="warning"
                  showIcon
                  style={{ marginBottom: '16px' }}
                />

                <Row gutter={[16, 16]}>
                  <Col xs={24} sm={8}>
                    <div style={{ textAlign: 'center' }}>
                      <Progress
                        type="circle"
                        percent={Math.round(results.results.capital_impact.capital_ratio_impact * 100)}
                        strokeColor="#ff4d4f"
                        format={percent => `${percent}%`}
                      />
                      <div style={{ marginTop: '8px' }}>
                        <Text strong>Capital Ratio Impact</Text>
                      </div>
                    </div>
                  </Col>

                  <Col xs={24} sm={16}>
                    <Descriptions bordered column={1} size="small">
                      <Descriptions.Item label="Expected Loss">
                        {formatCurrency(results.results.capital_impact.expected_loss)}
                      </Descriptions.Item>
                      <Descriptions.Item label="Additional Capital Required">
                        {formatCurrency(results.results.capital_impact.capital_requirement)}
                      </Descriptions.Item>
                      <Descriptions.Item label="Impact on Capital Ratio">
                        -{(results.results.capital_impact.capital_ratio_impact * 100).toFixed(2)}%
                      </Descriptions.Item>
                    </Descriptions>
                  </Col>
                </Row>
              </Card>

              {/* Recommendations */}
              <Card title="Risk Management Recommendations" icon={<WarningOutlined />}>
                <Space direction="vertical" style={{ width: '100%' }}>
                  {results.results.recommendations.map((rec, index) => (
                    <Alert
                      key={index}
                      message={rec}
                      type="info"
                      showIcon
                    />
                  ))}
                </Space>
              </Card>
            </Space>
          ) : (
            <Card>
              <Result
                icon={<ExperimentOutlined />}
                title="Climate Stress Testing"
                subTitle="Configure and run stress test scenarios to assess portfolio resilience to extreme flood events."
              />
            </Card>
          )}
        </Col>
      </Row>
    </div>
  )
}

export default StressTest