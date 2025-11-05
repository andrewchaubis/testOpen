import React from 'react'
import { Routes, Route } from 'react-router-dom'
import { ConfigProvider } from 'antd'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import FloodMap from './pages/FloodMap'
import AssetAnalysis from './pages/AssetAnalysis'
import StressTest from './pages/StressTest'
import HistoricalData from './pages/HistoricalData'
import './styles/App.css'

const theme = {
  token: {
    colorPrimary: '#1890ff',
    colorSuccess: '#52c41a',
    colorWarning: '#faad14',
    colorError: '#ff4d4f',
    borderRadius: 6,
  },
}

function App() {
  return (
    <ConfigProvider theme={theme}>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/map" element={<FloodMap />} />
          <Route path="/asset-analysis" element={<AssetAnalysis />} />
          <Route path="/stress-test" element={<StressTest />} />
          <Route path="/historical" element={<HistoricalData />} />
        </Routes>
      </Layout>
    </ConfigProvider>
  )
}

export default App