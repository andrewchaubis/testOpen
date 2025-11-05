import React, { useState } from 'react'
import {
  Card,
  Row,
  Col,
  Form,
  Input,
  Select,
  Button,
  InputNumber,
  Typography,
  Divider,
  Result,
  Descriptions,
  Progress,
  Tag,
  Space,
  Alert
} from 'antd'
import {
  DollarOutlined,
  HomeOutlined,
  CalculatorOutlined,
  WarningOutlined
} from '@ant-design/icons'
import { apiService } from '../services/apiService'

const { Title, Text } = Typography
const { Option } = Select

const AssetAnalysis = () => {
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)
  const [analysis, setAnalysis] = useState(null)

  const handleSubmit = async (values) => {
    setLoading(true)
    try {
      // Mock analysis for demo
      const mockAnalysis = {
        asset_type: values.asset_type,
        asset_value: values.asset_value,
        flood_risk_level: 'high',
        physical_damage: {
          estimated_flood_depth: 1.2,
          estimated_duration_days: 7,
          damage_ratio: 0.35,
          damage_amount: values.asset_value * 0.35,
          salvage_value: values.asset_value * 0.65
        },
        financial_impact: {
          gross_damage: values.asset_value * 0.35,
          insurance_payout: values.insurance_coverage || 0,
          net_loss: (values.asset_value * 0.35) - (values.insurance_coverage || 0),
          loss_ratio: 0.35,
          loan_impact: values.loan_amount ? {
            original_ltv: values.loan_amount / values.asset_value,
            ltv_after_damage: values.loan_amount / (values.asset_value * 0.65),
            underwater_amount: Math.max(0, values.loan_amount - (values.asset_value * 0.65)),
            equity_loss: Math.min(values.asset_value - values.loan_amount, values.asset_value * 0.35)
          } : null
        },
        default_probability: values.loan_amount ? {
          default_probability: 0.25,
          risk_category: 'high',
          base_rate: 0.02,
          damage_impact: 0.15,
          ltv_impact: 0.08,
          insurance_protection: -0.05,
          recovery_impact: 0.05
        } : null,
        recommendations: [
          'Consider increasing insurance coverage',
          'Implement flood mitigation measures',
          'Monitor loan performance closely',
          'Explore disaster relief programs'
        ]
      }

      setAnalysis(mockAnalysis)
    } catch (error) {
      console.error('Error analyzing asset:', error)
    } finally {
      setLoading(false)
    }
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

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-MY', {
      style: 'currency',
      currency: 'MYR'
    }).format(amount)
  }

  return (
    <div>
      <Title level={2}>Asset Impact Analysis</Title>
      <Text type="secondary">
        Assess the potential impact of flooding on your assets and loan portfolio
      </Text>

      <Row gutter={[24, 24]} style={{ marginTop: '24px' }}>
        <Col xs={24} lg={8}>
          <Card title="Asset Information" icon={<HomeOutlined />}>
            <Form
              form={form}
              layout="vertical"
              onFinish={handleSubmit}
            >
              <Form.Item
                name="asset_type"
                label="Asset Type"
                rules={[{ required: true, message: 'Please select asset type' }]}
              >
                <Select placeholder="Select asset type">
                  <Option value="residential">Residential Property</Option>
                  <Option value="commercial">Commercial Property</Option>
                  <Option value="industrial">Industrial Property</Option>
                </Select>
              </Form.Item>

              <Form.Item
                name="asset_value"
                label="Asset Value (MYR)"
                rules={[{ required: true, message: 'Please enter asset value' }]}
              >
                <InputNumber
                  style={{ width: '100%' }}
                  min={0}
                  formatter={value => `RM ${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                  parser={value => value.replace(/RM\s?|(,*)/g, '')}
                  placeholder="e.g., 500000"
                />
              </Form.Item>

              <Form.Item
                name="loan_amount"
                label="Loan Amount (MYR)"
              >
                <InputNumber
                  style={{ width: '100%' }}
                  min={0}
                  formatter={value => `RM ${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                  parser={value => value.replace(/RM\s?|(,*)/g, '')}
                  placeholder="Optional - if financed"
                />
              </Form.Item>

              <Form.Item
                name="insurance_coverage"
                label="Insurance Coverage (MYR)"
              >
                <InputNumber
                  style={{ width: '100%' }}
                  min={0}
                  formatter={value => `RM ${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                  parser={value => value.replace(/RM\s?|(,*)/g, '')}
                  placeholder="Optional - insurance amount"
                />
              </Form.Item>

              <Form.Item
                name="location"
                label="Location"
                rules={[{ required: true, message: 'Please enter location' }]}
              >
                <Input placeholder="e.g., Kota Bharu, Kelantan" />
              </Form.Item>

              <Button
                type="primary"
                htmlType="submit"
                loading={loading}
                block
                icon={<CalculatorOutlined />}
              >
                Analyze Impact
              </Button>
            </Form>
          </Card>
        </Col>

        <Col xs={24} lg={16}>
          {analysis ? (
            <Space direction="vertical" style={{ width: '100%' }} size="large">
              {/* Risk Assessment */}
              <Card title="Flood Risk Assessment">
                <Row gutter={[16, 16]}>
                  <Col xs={24} sm={8}>
                    <div style={{ textAlign: 'center' }}>
                      <Title level={3} style={{ color: getRiskColor(analysis.flood_risk_level) }}>
                        {analysis.flood_risk_level.toUpperCase()}
                      </Title>
                      <Text>Risk Level</Text>
                    </div>
                  </Col>
                  <Col xs={24} sm={8}>
                    <div style={{ textAlign: 'center' }}>
                      <Title level={3}>
                        {analysis.physical_damage.estimated_flood_depth.toFixed(1)}m
                      </Title>
                      <Text>Estimated Flood Depth</Text>
                    </div>
                  </Col>
                  <Col xs={24} sm={8}>
                    <div style={{ textAlign: 'center' }}>
                      <Title level={3}>
                        {analysis.physical_damage.estimated_duration_days} days
                      </Title>
                      <Text>Estimated Duration</Text>
                    </div>
                  </Col>
                </Row>
              </Card>

              {/* Physical Damage */}
              <Card title="Physical Damage Assessment">
                <Descriptions bordered column={2}>
                  <Descriptions.Item label="Damage Ratio">
                    <Progress 
                      percent={Math.round(analysis.physical_damage.damage_ratio * 100)}
                      strokeColor={analysis.physical_damage.damage_ratio > 0.5 ? '#ff4d4f' : '#faad14'}
                    />
                  </Descriptions.Item>
                  <Descriptions.Item label="Damage Amount">
                    <Text strong style={{ color: '#ff4d4f' }}>
                      {formatCurrency(analysis.physical_damage.damage_amount)}
                    </Text>
                  </Descriptions.Item>
                  <Descriptions.Item label="Salvage Value">
                    <Text strong style={{ color: '#52c41a' }}>
                      {formatCurrency(analysis.physical_damage.salvage_value)}
                    </Text>
                  </Descriptions.Item>
                  <Descriptions.Item label="Asset Type">
                    <Tag>{analysis.asset_type.toUpperCase()}</Tag>
                  </Descriptions.Item>
                </Descriptions>
              </Card>

              {/* Financial Impact */}
              <Card title="Financial Impact">
                <Row gutter={[16, 16]}>
                  <Col xs={24} md={12}>
                    <Descriptions bordered column={1} size="small">
                      <Descriptions.Item label="Gross Damage">
                        {formatCurrency(analysis.financial_impact.gross_damage)}
                      </Descriptions.Item>
                      <Descriptions.Item label="Insurance Payout">
                        {formatCurrency(analysis.financial_impact.insurance_payout)}
                      </Descriptions.Item>
                      <Descriptions.Item label="Net Loss">
                        <Text strong style={{ color: '#ff4d4f' }}>
                          {formatCurrency(analysis.financial_impact.net_loss)}
                        </Text>
                      </Descriptions.Item>
                      <Descriptions.Item label="Loss Ratio">
                        {(analysis.financial_impact.loss_ratio * 100).toFixed(1)}%
                      </Descriptions.Item>
                    </Descriptions>
                  </Col>

                  {analysis.financial_impact.loan_impact && (
                    <Col xs={24} md={12}>
                      <Title level={5}>Loan Impact</Title>
                      <Descriptions bordered column={1} size="small">
                        <Descriptions.Item label="Original LTV">
                          {(analysis.financial_impact.loan_impact.original_ltv * 100).toFixed(1)}%
                        </Descriptions.Item>
                        <Descriptions.Item label="LTV After Damage">
                          <Text style={{ 
                            color: analysis.financial_impact.loan_impact.ltv_after_damage > 1 ? '#ff4d4f' : '#666'
                          }}>
                            {(analysis.financial_impact.loan_impact.ltv_after_damage * 100).toFixed(1)}%
                          </Text>
                        </Descriptions.Item>
                        <Descriptions.Item label="Underwater Amount">
                          {formatCurrency(analysis.financial_impact.loan_impact.underwater_amount)}
                        </Descriptions.Item>
                        <Descriptions.Item label="Equity Loss">
                          {formatCurrency(analysis.financial_impact.loan_impact.equity_loss)}
                        </Descriptions.Item>
                      </Descriptions>
                    </Col>
                  )}
                </Row>
              </Card>

              {/* Default Risk */}
              {analysis.default_probability && (
                <Card title="Default Risk Assessment">
                  <Alert
                    message={`Default Risk: ${analysis.default_probability.risk_category.toUpperCase()}`}
                    description={`Probability of default: ${(analysis.default_probability.default_probability * 100).toFixed(1)}%`}
                    type={analysis.default_probability.risk_category === 'high' ? 'error' : 'warning'}
                    showIcon
                    style={{ marginBottom: '16px' }}
                  />

                  <Row gutter={[16, 16]}>
                    <Col xs={24} md={12}>
                      <Progress
                        type="circle"
                        percent={Math.round(analysis.default_probability.default_probability * 100)}
                        strokeColor={analysis.default_probability.default_probability > 0.3 ? '#ff4d4f' : '#faad14'}
                        format={percent => `${percent}%`}
                      />
                      <div style={{ textAlign: 'center', marginTop: '8px' }}>
                        <Text strong>Default Probability</Text>
                      </div>
                    </Col>

                    <Col xs={24} md={12}>
                      <Descriptions bordered column={1} size="small">
                        <Descriptions.Item label="Base Rate">
                          {(analysis.default_probability.base_rate * 100).toFixed(1)}%
                        </Descriptions.Item>
                        <Descriptions.Item label="Damage Impact">
                          +{(analysis.default_probability.damage_impact * 100).toFixed(1)}%
                        </Descriptions.Item>
                        <Descriptions.Item label="LTV Impact">
                          +{(analysis.default_probability.ltv_impact * 100).toFixed(1)}%
                        </Descriptions.Item>
                        <Descriptions.Item label="Insurance Protection">
                          {(analysis.default_probability.insurance_protection * 100).toFixed(1)}%
                        </Descriptions.Item>
                      </Descriptions>
                    </Col>
                  </Row>
                </Card>
              )}

              {/* Recommendations */}
              <Card title="Recommendations" icon={<WarningOutlined />}>
                <Space direction="vertical" style={{ width: '100%' }}>
                  {analysis.recommendations.map((rec, index) => (
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
                icon={<CalculatorOutlined />}
                title="Asset Impact Analysis"
                subTitle="Enter asset information on the left to analyze potential flood impact and financial risk."
              />
            </Card>
          )}
        </Col>
      </Row>
    </div>
  )
}

export default AssetAnalysis