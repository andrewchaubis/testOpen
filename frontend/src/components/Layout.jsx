import React, { useState } from 'react'
import { Layout as AntLayout, Menu, Typography, Space, Badge } from 'antd'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  DashboardOutlined,
  EnvironmentOutlined,
  BarChartOutlined,
  ExperimentOutlined,
  HistoryOutlined,
  AlertOutlined
} from '@ant-design/icons'

const { Header, Sider, Content } = AntLayout
const { Title } = Typography

const Layout = ({ children }) => {
  const [collapsed, setCollapsed] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()

  const menuItems = [
    {
      key: '/',
      icon: <DashboardOutlined />,
      label: 'Dashboard',
    },
    {
      key: '/map',
      icon: <EnvironmentOutlined />,
      label: 'Flood Map',
    },
    {
      key: '/asset-analysis',
      icon: <BarChartOutlined />,
      label: 'Asset Analysis',
    },
    {
      key: '/stress-test',
      icon: <ExperimentOutlined />,
      label: 'Stress Test',
    },
    {
      key: '/historical',
      icon: <HistoryOutlined />,
      label: 'Historical Data',
    },
  ]

  const handleMenuClick = ({ key }) => {
    navigate(key)
  }

  return (
    <AntLayout style={{ minHeight: '100vh' }}>
      <Sider 
        collapsible 
        collapsed={collapsed} 
        onCollapse={setCollapsed}
        theme="dark"
        width={250}
      >
        <div style={{ 
          padding: '16px', 
          textAlign: 'center',
          borderBottom: '1px solid #303030'
        }}>
          <Title 
            level={collapsed ? 5 : 4} 
            style={{ 
              color: 'white', 
              margin: 0,
              fontSize: collapsed ? '14px' : '18px'
            }}
          >
            {collapsed ? 'KFP' : 'Kelantan Flood Predictor'}
          </Title>
        </div>
        
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={handleMenuClick}
          style={{ marginTop: '16px' }}
        />
      </Sider>
      
      <AntLayout>
        <Header style={{ 
          background: '#fff', 
          padding: '0 24px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
        }}>
          <Title level={3} style={{ margin: 0, color: '#1890ff' }}>
            Flood Risk Assessment - Kelantan, Malaysia
          </Title>
          
          <Space>
            <Badge count={2} size="small">
              <AlertOutlined style={{ fontSize: '20px', color: '#ff4d4f' }} />
            </Badge>
            <span style={{ color: '#666', fontSize: '14px' }}>
              Last Updated: {new Date().toLocaleTimeString()}
            </span>
          </Space>
        </Header>
        
        <Content style={{ 
          margin: '24px',
          padding: '24px',
          background: '#f0f2f5',
          minHeight: 'calc(100vh - 112px)'
        }}>
          {children}
        </Content>
      </AntLayout>
    </AntLayout>
  )
}

export default Layout