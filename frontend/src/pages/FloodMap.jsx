import React, { useState, useEffect, useRef } from 'react'
import { 
  Card, 
  Row, 
  Col, 
  Select, 
  Button, 
  Space, 
  Typography, 
  Slider,
  Switch,
  Tooltip,
  Modal,
  Descriptions,
  Tag
} from 'antd'
import { 
  EnvironmentOutlined, 
  ReloadOutlined,
  InfoCircleOutlined,
  WarningOutlined
} from '@ant-design/icons'
import { MapContainer, TileLayer, Marker, Popup, Circle, useMapEvents } from 'react-leaflet'
import L from 'leaflet'
import { apiService } from '../services/apiService'

const { Title, Text } = Typography
const { Option } = Select

// Fix for default markers in react-leaflet
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
})

// Custom icons for different risk levels
const createRiskIcon = (riskLevel) => {
  const colors = {
    low: '#52c41a',
    medium: '#faad14', 
    high: '#ff7a45',
    extreme: '#ff4d4f'
  }
  
  return L.divIcon({
    className: 'custom-div-icon',
    html: `<div style="
      background-color: ${colors[riskLevel] || '#d9d9d9'};
      width: 20px;
      height: 20px;
      border-radius: 50%;
      border: 2px solid white;
      box-shadow: 0 2px 4px rgba(0,0,0,0.3);
    "></div>`,
    iconSize: [20, 20],
    iconAnchor: [10, 10]
  })
}

const FloodMap = () => {
  const [districts, setDistricts] = useState([])
  const [selectedDistrict, setSelectedDistrict] = useState(null)
  const [mapCenter, setMapCenter] = useState([5.4141, 102.0882]) // Kelantan center
  const [mapZoom, setMapZoom] = useState(9)
  const [showRiskCircles, setShowRiskCircles] = useState(true)
  const [riskThreshold, setRiskThreshold] = useState(0.3)
  const [loading, setLoading] = useState(false)
  const [clickedLocation, setClickedLocation] = useState(null)
  const [locationRisk, setLocationRisk] = useState(null)
  const [modalVisible, setModalVisible] = useState(false)
  const mapRef = useRef()

  useEffect(() => {
    loadDistricts()
  }, [])

  const loadDistricts = async () => {
    try {
      setLoading(true)
      const response = await apiService.getKelantanDistricts()
      setDistricts(response.districts || mockDistricts)
    } catch (error) {
      console.error('Error loading districts:', error)
      setDistricts(mockDistricts)
    } finally {
      setLoading(false)
    }
  }

  const mockDistricts = [
    {
      name: 'Kota Bharu',
      center: { lat: 6.1254, lng: 102.2386 },
      flood_risk: 'high',
      risk_probability: 0.7,
      population: 491237
    },
    {
      name: 'Kuala Krai',
      center: { lat: 5.5333, lng: 102.2000 },
      flood_risk: 'extreme',
      risk_probability: 0.85,
      population: 103404
    },
    {
      name: 'Machang',
      center: { lat: 5.7667, lng: 102.2167 },
      flood_risk: 'medium',
      risk_probability: 0.4,
      population: 95639
    },
    {
      name: 'Pasir Mas',
      center: { lat: 6.0500, lng: 102.1333 },
      flood_risk: 'high',
      risk_probability: 0.65,
      population: 188741
    },
    {
      name: 'Tanah Merah',
      center: { lat: 5.8000, lng: 102.1500 },
      flood_risk: 'medium',
      risk_probability: 0.35,
      population: 121319
    }
  ]

  const handleDistrictChange = (districtName) => {
    const district = districts.find(d => d.name === districtName)
    if (district) {
      setSelectedDistrict(district)
      setMapCenter([district.center.lat, district.center.lng])
      setMapZoom(11)
    }
  }

  const handleMapClick = async (lat, lng) => {
    setClickedLocation({ lat, lng })
    setLoading(true)
    
    try {
      const risk = await apiService.getLocationRisk(lat, lng)
      setLocationRisk(risk)
      setModalVisible(true)
    } catch (error) {
      console.error('Error getting location risk:', error)
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

  const MapClickHandler = () => {
    useMapEvents({
      click: (e) => {
        handleMapClick(e.latlng.lat, e.latlng.lng)
      }
    })
    return null
  }

  const filteredDistricts = districts.filter(d => 
    d.risk_probability >= riskThreshold
  )

  return (
    <div>
      <Title level={2}>Flood Risk Map - Kelantan</Title>
      
      <Row gutter={[16, 16]} style={{ marginBottom: '16px' }}>
        <Col xs={24} md={8}>
          <Card size="small">
            <Space direction="vertical" style={{ width: '100%' }}>
              <div>
                <Text strong>Select District:</Text>
                <Select
                  style={{ width: '100%', marginTop: '8px' }}
                  placeholder="Choose a district"
                  onChange={handleDistrictChange}
                  allowClear
                >
                  {districts.map(district => (
                    <Option key={district.name} value={district.name}>
                      {district.name}
                    </Option>
                  ))}
                </Select>
              </div>
              
              <div>
                <Text strong>Risk Threshold:</Text>
                <Slider
                  min={0}
                  max={1}
                  step={0.1}
                  value={riskThreshold}
                  onChange={setRiskThreshold}
                  marks={{
                    0: '0%',
                    0.5: '50%',
                    1: '100%'
                  }}
                />
              </div>
              
              <div>
                <Space>
                  <Text strong>Show Risk Circles:</Text>
                  <Switch 
                    checked={showRiskCircles}
                    onChange={setShowRiskCircles}
                  />
                </Space>
              </div>
            </Space>
          </Card>
        </Col>
        
        <Col xs={24} md={8}>
          <Card size="small">
            <Space direction="vertical">
              <Text strong>Legend:</Text>
              <Space>
                <div style={{ 
                  width: '12px', 
                  height: '12px', 
                  backgroundColor: '#52c41a',
                  borderRadius: '50%'
                }}></div>
                <Text>Low Risk (0-30%)</Text>
              </Space>
              <Space>
                <div style={{ 
                  width: '12px', 
                  height: '12px', 
                  backgroundColor: '#faad14',
                  borderRadius: '50%'
                }}></div>
                <Text>Medium Risk (30-60%)</Text>
              </Space>
              <Space>
                <div style={{ 
                  width: '12px', 
                  height: '12px', 
                  backgroundColor: '#ff7a45',
                  borderRadius: '50%'
                }}></div>
                <Text>High Risk (60-80%)</Text>
              </Space>
              <Space>
                <div style={{ 
                  width: '12px', 
                  height: '12px', 
                  backgroundColor: '#ff4d4f',
                  borderRadius: '50%'
                }}></div>
                <Text>Extreme Risk (80%+)</Text>
              </Space>
            </Space>
          </Card>
        </Col>
        
        <Col xs={24} md={8}>
          <Card size="small">
            <Space direction="vertical">
              <Text strong>Instructions:</Text>
              <Text type="secondary">• Click on any location to get flood risk assessment</Text>
              <Text type="secondary">• Use district selector to zoom to specific areas</Text>
              <Text type="secondary">• Adjust risk threshold to filter districts</Text>
              <Button 
                icon={<ReloadOutlined />}
                onClick={loadDistricts}
                loading={loading}
                size="small"
              >
                Refresh Data
              </Button>
            </Space>
          </Card>
        </Col>
      </Row>

      <Card>
        <div style={{ height: '600px', width: '100%' }}>
          <MapContainer
            center={mapCenter}
            zoom={mapZoom}
            style={{ height: '100%', width: '100%' }}
            ref={mapRef}
          >
            <TileLayer
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            />
            
            <MapClickHandler />
            
            {filteredDistricts.map((district, index) => (
              <React.Fragment key={index}>
                <Marker
                  position={[district.center.lat, district.center.lng]}
                  icon={createRiskIcon(district.flood_risk)}
                >
                  <Popup>
                    <div>
                      <Title level={5}>{district.name}</Title>
                      <p><strong>Risk Level:</strong> 
                        <Tag color={getRiskColor(district.flood_risk)} style={{ marginLeft: '8px' }}>
                          {district.flood_risk.toUpperCase()}
                        </Tag>
                      </p>
                      <p><strong>Probability:</strong> {(district.risk_probability * 100).toFixed(1)}%</p>
                      <p><strong>Population:</strong> {district.population?.toLocaleString()}</p>
                    </div>
                  </Popup>
                </Marker>
                
                {showRiskCircles && (
                  <Circle
                    center={[district.center.lat, district.center.lng]}
                    radius={district.risk_probability * 10000} // Scale radius by risk
                    pathOptions={{
                      color: getRiskColor(district.flood_risk),
                      fillColor: getRiskColor(district.flood_risk),
                      fillOpacity: 0.2,
                      weight: 2
                    }}
                  />
                )}
              </React.Fragment>
            ))}
            
            {clickedLocation && (
              <Marker position={[clickedLocation.lat, clickedLocation.lng]}>
                <Popup>
                  <div>
                    <Title level={5}>Selected Location</Title>
                    <p>Lat: {clickedLocation.lat.toFixed(4)}</p>
                    <p>Lng: {clickedLocation.lng.toFixed(4)}</p>
                    <Button 
                      size="small" 
                      onClick={() => setModalVisible(true)}
                      disabled={!locationRisk}
                    >
                      View Risk Details
                    </Button>
                  </div>
                </Popup>
              </Marker>
            )}
          </MapContainer>
        </div>
      </Card>

      <Modal
        title="Location Risk Assessment"
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setModalVisible(false)}>
            Close
          </Button>
        ]}
        width={600}
      >
        {locationRisk && (
          <Descriptions bordered column={1}>
            <Descriptions.Item label="Coordinates">
              {locationRisk.location.latitude.toFixed(4)}, {locationRisk.location.longitude.toFixed(4)}
            </Descriptions.Item>
            <Descriptions.Item label="Flood Probability">
              <Space>
                {(locationRisk.flood_probability * 100).toFixed(1)}%
                <Tag color={getRiskColor(locationRisk.risk_level)}>
                  {locationRisk.risk_level.toUpperCase()}
                </Tag>
              </Space>
            </Descriptions.Item>
            <Descriptions.Item label="Confidence">
              {(locationRisk.confidence * 100).toFixed(1)}%
            </Descriptions.Item>
            <Descriptions.Item label="Elevation">
              {locationRisk.factors?.elevation?.toFixed(1)}m above sea level
            </Descriptions.Item>
            <Descriptions.Item label="Distance to River">
              {(locationRisk.factors?.distance_to_river / 1000)?.toFixed(1)}km
            </Descriptions.Item>
            <Descriptions.Item label="Historical Frequency">
              {(locationRisk.factors?.historical_frequency * 100)?.toFixed(1)}% annual probability
            </Descriptions.Item>
          </Descriptions>
        )}
      </Modal>
    </div>
  )
}

export default FloodMap