import React from 'react'

const Dashboard = React.lazy(() => import('./views/dashboard/Dashboard'))
const Drivers = React.lazy(() => import('./views/pages/drivers/Drivers'))
const Schedules = React.lazy(() => import('./views/pages/schedules/Schedules'))
const Trip = React.lazy(() => import('./views/pages/trip/Trip'))
const RegisterDriver = React.lazy(() => import('./views/pages/register/Register'))

const routes = [
  { path: '/', exact: true, name: 'Home' },
  { path: '/dashboard', name: 'Dashboard', element: Dashboard },
  { path: '/drivers', name: 'Drivers', element: Drivers },
  { path: '/trip/:tripId', name: 'Trip', element: Trip },
  { path: '/schedules', name: 'Schedules', element: Schedules },
  { path: '/registerDriver', name: 'RegisterDriver', element: RegisterDriver },
]

export default routes
