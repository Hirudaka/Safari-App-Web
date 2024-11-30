import React from 'react'

const Dashboard = React.lazy(() => import('./views/dashboard/Dashboard'))
const Drivers = React.lazy(() => import('./views/pages/drivers/Drivers'))
const Schedules = React.lazy(() => import('./views/pages/schedules/Schedules'))

const routes = [
  { path: '/', exact: true, name: 'Home' },
  { path: '/dashboard', name: 'Dashboard', element: Dashboard },
  { path: '/drivers', name: 'Drivers', element: Drivers },
  { path: '/schedules', name: 'Schedules', element: Schedules },
]

export default routes
