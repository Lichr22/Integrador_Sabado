import React from 'react'
import { createRoot } from 'react-dom/client'
import App from './modules/platform/components/PlatformApp.jsx'
import './modules/core/styles/styles.css'
import './modules/auth/styles/account.css'

createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
