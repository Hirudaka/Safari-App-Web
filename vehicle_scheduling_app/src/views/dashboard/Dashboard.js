import React, { useEffect, useState, useRef } from 'react'
import '../../scss/_custom.scss'
import ReactDatePicker from 'react-datepicker'
import 'react-datepicker/dist/react-datepicker.css'

import {
  CAvatar,
  CButton,
  CCard,
  CCardBody,
  CCardHeader,
  CCol,
  CRow,
  CTable,
  CTableBody,
  CTableDataCell,
  CTableHead,
  CTableHeaderCell,
  CTableRow,
} from '@coreui/react'
import CIcon from '@coreui/icons-react'
import { cilCloudDownload } from '@coreui/icons'

import avatarPlaceholder from 'src/assets/images/avatars/user.png'
import MainChart from './MainChart'
import WidgetsDropdown from './../widgets/WidgetsDropdown'

const Dashboard = () => {
  const [trips, setTrips] = useState([])
  const [drivers, setDrivers] = useState([])
  const [filteredTrips, setFilteredTrips] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedDate, setSelectedDate] = useState(null)

  useEffect(() => {
    async function fetchTrips() {
      try {
        const response = await fetch('http://127.0.0.1:5001/api/trips')
        const data = await response.json()
        setTrips(data.trips)
        setFilteredTrips(data.trips) // Set initial state with all trips
      } catch (error) {
        console.error('Error fetching trips:', error)
      } finally {
        setLoading(false)
      }
    }

    async function fetchDrivers() {
      try {
        const response = await fetch('http://127.0.0.1:5001/get_drivers')
        const data = await response.json()
        setDrivers(data.drivers)
      } catch (error) {
        console.error('Error fetching drivers:', error)
      }
    }

    fetchTrips()
    fetchDrivers()
  }, [])

  const getStatusColor = (status) => {
    switch (status) {
      case 'ongoing':
        return 'success'
      case 'completed':
        return 'danger'
      case 'idle':
      default:
        return 'warning'
    }
  }

  const getDriverName = (driverId) => {
    const driver = drivers.find((d) => String(d.driver_id) === String(driverId))
    return driver ? driver.name : 'Unknown Driver'
  }

  const getDriverAvatar = (driverId) => {
    const driver = drivers.find((d) => String(d.driver_id) === String(driverId))
    return driver && driver.avatar ? driver.avatar : avatarPlaceholder
  }

  const formatDateTime = (dateTimeString) => {
    if (!dateTimeString) return { date: 'Processing', time: 'Processing' }
    const date = new Date(dateTimeString)

    // Format the date (YYYY-MM-DD)
    const formattedDate = date.toISOString().split('T')[0]

    // Format the time with AM/PM
    let hours = date.getHours()
    const minutes = date.getMinutes().toString().padStart(2, '0')
    const seconds = date.getSeconds().toString().padStart(2, '0')
    const ampm = hours >= 12 ? 'PM' : 'AM'

    // Convert hours to 12-hour format
    hours = hours % 12 || 12 // Adjust 0 to 12 for midnight
    const formattedTime = `${hours}:${minutes}:${seconds} ${ampm}`

    return { date: formattedDate, time: formattedTime }
  }

  const groupTripsByHourAndStatus = (trips) => {
    const grouped = { ongoing: [], completed: [], idle: [] }

    // Initialize data for each hour of the day
    for (let i = 0; i < 24; i++) {
      grouped.ongoing.push({ x: i, y: 0 })
      grouped.completed.push({ x: i, y: 0 })
      grouped.idle.push({ x: i, y: 0 })
    }

    trips.forEach((trip) => {
      if (trip.entry_time) {
        const hour = new Date(trip.entry_time).getHours()
        if (trip.status === 'ongoing') {
          grouped.ongoing[hour].y++
        } else if (trip.status === 'completed') {
          grouped.completed[hour].y++
        } else {
          grouped.idle[hour].y++
        }
      }
    })

    return grouped
  }

  const handleDateChange = (date) => {
    setSelectedDate(date)

    if (date) {
      // Get selected date in local time
      const selectedDate = new Date(date.getFullYear(), date.getMonth(), date.getDate()).getTime()

      // Filter trips based on local date comparison
      const filtered = trips.filter((trip) => {
        if (!trip.entry_time) return false

        const tripDate = new Date(trip.entry_time)
        const tripLocalDate = new Date(
          tripDate.getFullYear(),
          tripDate.getMonth(),
          tripDate.getDate(),
        ).getTime()

        return tripLocalDate === selectedDate
      })

      console.log('Filtered Trips:', filtered) // Debug filtered trips
      setFilteredTrips(filtered)
    } else {
      setFilteredTrips(trips) // Reset to all trips if no date is selected
    }
  }

  const groupedData = groupTripsByHourAndStatus(filteredTrips)

  const chartData = {
    datasets: [
      {
        label: 'Ongoing Trips',
        data: groupedData.ongoing,
        borderColor: 'rgb(75, 192, 75)',
        backgroundColor: 'rgba(75, 192, 75, 0.2)',
        tension: 0.4,
      },
      {
        label: 'Completed Trips',
        data: groupedData.completed,
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(255, 99, 132, 0.2)',
        tension: 0.4,
      },
      {
        label: 'Idle Trips',
        data: groupedData.idle,
        borderColor: 'rgb(255, 206, 86)',
        backgroundColor: 'rgba(255, 206, 86, 0.2)',
        tension: 0.4,
      },
    ],
  }

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
    },
    scales: {
      x: {
        type: 'linear',
        title: {
          display: true,
          text: 'Time (Hours)',
        },
        ticks: {
          stepSize: 1,
          callback: (value) => `${value}:00`,
        },
        min: 0,
        max: 23,
      },
      y: {
        title: {
          display: true,
          text: 'Trip Count',
        },
        beginAtZero: true,
      },
    },
  }

  return (
    <>
      <CCard className="mb-4">
        <CCardBody>
          <CRow>
            <CCol sm={5}>
              <h4 className="card-title mb-0">Traffic</h4>
              <div className="small text-body-secondary">Today</div>
            </CCol>
            <CCol sm={6} className="d-none d-md-block">
              <div className="d-flex justify-content-center">
                <ReactDatePicker
                  selected={selectedDate}
                  onChange={handleDateChange}
                  dateFormat="yyyy/MM/dd"
                  className="form-control custom-date-picker "
                  placeholderText="Select a date"
                />
              </div>
            </CCol>
          </CRow>
          <MainChart chartData={chartData} chartOptions={chartOptions} />
        </CCardBody>
      </CCard>
      <CRow>
        <CCol xs>
          <CCard className="mb-4">
            <CCardHeader>Traffic {' & '} Trips</CCardHeader>
            <CCardBody>
              <br />
              <CTable align="middle" className="mb-0 border" hover responsive>
                <CTableHead>
                  <CTableRow>
                    <CTableHeaderCell>Avatar</CTableHeaderCell>
                    <CTableHeaderCell>Driver Name</CTableHeaderCell>
                    <CTableHeaderCell>Trip Status</CTableHeaderCell>
                    <CTableHeaderCell>Start Time</CTableHeaderCell>
                    <CTableHeaderCell>End Time</CTableHeaderCell>
                    <CTableHeaderCell>Action</CTableHeaderCell>
                  </CTableRow>
                </CTableHead>
                <CTableBody>
                  {filteredTrips.map((trip) => (
                    <CTableRow key={trip._id}>
                      <CTableDataCell>
                        <CAvatar
                          size="md"
                          src={getDriverAvatar(trip.driver_id)}
                          status={getStatusColor(trip.status)}
                        />
                      </CTableDataCell>
                      <CTableDataCell>{getDriverName(trip.driver_id)}</CTableDataCell>
                      <CTableDataCell>
                        <span className={`badge bg-${getStatusColor(trip.status)}`}>
                          {trip.status.charAt(0).toUpperCase() + trip.status.slice(1)}
                        </span>
                      </CTableDataCell>
                      <CTableDataCell>
                        {formatDateTime(trip.entry_time).time || 'Processing'}
                      </CTableDataCell>
                      <CTableDataCell>
                        {formatDateTime(trip.end_time).time || 'Processing'}
                      </CTableDataCell>
                      <CTableDataCell>
                        <CButton color="info" variant="outline">
                          👁️
                        </CButton>
                      </CTableDataCell>
                    </CTableRow>
                  ))}
                </CTableBody>
              </CTable>
            </CCardBody>
          </CCard>
        </CCol>
      </CRow>
    </>
  )
}

export default Dashboard
