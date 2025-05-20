import React, { useEffect, useState, useRef } from 'react'
import '../../scss/_custom.scss'
import ReactDatePicker from 'react-datepicker'
import 'react-datepicker/dist/react-datepicker.css'
import { useNavigate } from 'react-router-dom'

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
  const navigate = useNavigate()
  const refreshIntervalRef = useRef(null)

  // Function to fetch trips data
  const fetchTrips = async () => {
    try {
      const response = await fetch('https://nasa-api-ennr.onrender.com/api/trips')
      const data = await response.json()
      console.log('refreshing')
      setTrips(data.trips)
      // Only update filtered trips if no search term is active
      if (!searchTerm) {
        setFilteredTrips(data.trips)
      } else {
        // Re-apply the search filter with the new data
        const filtered = data.trips.filter((trip) =>
          trip.vehicle_id?.toLowerCase().includes(searchTerm.toLowerCase()),
        )
        setFilteredTrips(filtered)
      }
    } catch (error) {
      console.error('Error fetching trips:', error)
    } finally {
      setLoading(false)
    }
  }

  // Initial data fetch and set up refresh interval
  useEffect(() => {
    fetchTrips()

    // Set up auto-refresh interval (every 3 seconds)
    refreshIntervalRef.current = setInterval(fetchTrips, 3000)

    // Clean up the interval when component unmounts
    return () => {
      if (refreshIntervalRef.current) {
        clearInterval(refreshIntervalRef.current)
      }
    }
  }, [])

  const handleViewClick = (tripId) => {
    navigate(`/trip/${tripId}`)
  }

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

  const formatDateTime = (dateTimeString) => {
    if (!dateTimeString) return { date: 'Processing', time: 'Processing' }

    const date = new Date(dateTimeString)

    // Format the date (YYYY-MM-DD)
    const formattedDate = date.toLocaleDateString('en-GB')

    // Local time formatting (browser/system timezone)
    let hours = date.getHours()
    const minutes = date.getMinutes().toString().padStart(2, '0')
    const seconds = date.getSeconds().toString().padStart(2, '0')
    const ampm = hours >= 12 ? 'PM' : 'AM'

    hours = hours % 12 || 12
    const formattedTime = `${hours}:${minutes}:${seconds} ${ampm}`

    return { date: formattedDate, time: formattedTime }
  }

  const formatDateTime2 = (dateTimeString) => {
    if (!dateTimeString) return { date: 'Processing', time: 'Processing' }

    const date = new Date(dateTimeString)

    // Format the date (YYYY-MM-DD)
    const formattedDate = date.toISOString().split('T')[0]

    // Use UTC methods to avoid timezone conversion
    let hours = date.getUTCHours()
    const minutes = date.getUTCMinutes().toString().padStart(2, '0')
    const seconds = date.getUTCSeconds().toString().padStart(2, '0')
    const ampm = hours >= 12 ? 'PM' : 'AM'

    // Convert hours to 12-hour format
    hours = hours % 12 || 12
    const formattedTime = `${hours}:${minutes}:${seconds} ${ampm}`

    return { date: formattedDate, time: formattedTime }
  }

  const getDriverName = (driverId) => {
    const driver = drivers.find((d) => String(d.driver_id) === String(driverId))
    return driver ? driver.name : 'Unknown Driver'
  }

  const getDriverAvatar = (driverId) => {
    const driver = drivers.find((d) => String(d.driver_id) === String(driverId))
    return driver && driver.avatar ? driver.avatar : avatarPlaceholder
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

      console.log('Filtered Trips:', filtered)
      setFilteredTrips(filtered)
    } else {
      setFilteredTrips(trips)
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

  const [searchTerm, setSearchTerm] = useState('')

  // Function to filter trips
  const filterTrips = (term) => {
    if (term.trim() === '') {
      setFilteredTrips(trips)
    } else {
      const filtered = trips.filter((trip) =>
        trip.vehicle_id?.toLowerCase().includes(term.toLowerCase()),
      )
      setFilteredTrips(filtered)
    }
  }

  // Handle input change
  const handleSearchChange = (event) => {
    const term = event.target.value
    setSearchTerm(term)
    filterTrips(term)
  }

  // Ensure trips update when data changes
  useEffect(() => {
    filterTrips(searchTerm)
  }, [trips])

  const endTrip = async (tripId) => {
    try {
      const response = await fetch(`https://nasa-api-ennr.onrender.com/end_trip/${tripId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (response.ok) {
        // Update the trip status in the frontend
        setTrips((prevTrips) =>
          prevTrips.map((trip) =>
            trip.trip_id === tripId ? { ...trip, status: 'completed' } : trip,
          ),
        )
        setFilteredTrips((prevTrips) =>
          prevTrips.map((trip) =>
            trip.trip_id === tripId ? { ...trip, status: 'completed' } : trip,
          ),
        )
        alert('Trip ended successfully')
        // Fetch fresh data instead of reloading the page
        fetchTrips()
      } else {
        console.error('Failed to end trip')
      }
    } catch (error) {
      console.error('Error ending trip:', error)
    }
  }

  const formatTripTime = (seconds) => {
    if (typeof seconds !== 'number' || isNaN(seconds)) {
      return 'N/A' // Return fallback if invalid
    }

    const totalSeconds = Math.floor(seconds) // Ensure it's an integer
    const hours = Math.floor(totalSeconds / 3600)
    const minutes = Math.floor((totalSeconds % 3600) / 60)
    const secs = totalSeconds % 60

    return `${hours}h ${minutes}m ${secs}s`
  }

  return (
    <>
      <CCard className="mb-4">
        <CCardBody>
          <CRow className="align-items-center">
            <CCol sm={9}>
              <h4 className="card-title mb-0">Traffic</h4>
              <div className="small text-body-secondary">Today</div>
            </CCol>

            <CCol sm={3}>
              <ReactDatePicker
                selected={selectedDate}
                onChange={handleDateChange}
                dateFormat="yyyy/MM/dd"
                className="form-control input-equal-height"
                placeholderText="Select a date"
              />
            </CCol>
          </CRow>
          <MainChart chartData={chartData} chartOptions={chartOptions} />
        </CCardBody>
      </CCard>
      <CRow>
        <CCol xs>
          <CCard className="mb-4">
            <CCardHeader>
              Traffic {' & '} Trips
              <span className="small text-body-secondary ms-2">
                (Auto-refreshing every 3 seconds)
              </span>
            </CCardHeader>
            <CCardBody>
              <CCol sm={4}>
                <input
                  type="text"
                  className="form-control input-equal-height"
                  placeholder="Search by Vehicle No"
                  value={searchTerm}
                  onChange={handleSearchChange}
                />
              </CCol>
              <br />
              <CTable align="middle" className="mb-0 border" hover responsive>
                <CTableHead>
                  <CTableRow>
                    <CTableHeaderCell>Avatar</CTableHeaderCell>
                    <CTableHeaderCell>Driver Name</CTableHeaderCell>
                    <CTableHeaderCell>Vehicle No</CTableHeaderCell>
                    <CTableHeaderCell>Trip Status</CTableHeaderCell>
                    <CTableHeaderCell>Start Time</CTableHeaderCell>
                    <CTableHeaderCell>End Time</CTableHeaderCell>
                    <CTableHeaderCell>Trip Time</CTableHeaderCell>
                    <CTableHeaderCell>Action</CTableHeaderCell>
                  </CTableRow>
                </CTableHead>
                <CTableBody>
                  {loading ? (
                    <CTableRow>
                      <CTableDataCell colSpan="8" className="text-center">
                        Loading...
                      </CTableDataCell>
                    </CTableRow>
                  ) : filteredTrips && filteredTrips.length > 0 ? (
                    filteredTrips.map((trip) => (
                      <CTableRow key={trip._id}>
                        <CTableDataCell>
                          <CAvatar
                            size="md"
                            src={getDriverAvatar(trip.driver_id)}
                            status={getStatusColor(trip.status)}
                          />
                        </CTableDataCell>
                        <CTableDataCell>{trip.driver_name || 'Unknown Driver'}</CTableDataCell>
                        <CTableDataCell>{trip.vehicle_id || 'N/A'}</CTableDataCell>
                        <CTableDataCell>
                          <span className={`badge bg-${getStatusColor(trip.status)}`}>
                            {trip.status
                              ? trip.status.charAt(0).toUpperCase() + trip.status.slice(1)
                              : 'Pending'}
                          </span>
                        </CTableDataCell>
                        <CTableDataCell>
                          {trip.entry_time ? formatDateTime(trip.entry_time).time : 'Processing'}
                        </CTableDataCell>
                        <CTableDataCell>
                          {trip.end_time ? formatDateTime2(trip.end_time).time : 'Processing'}
                        </CTableDataCell>
                        <CTableDataCell>{formatTripTime(trip.trip_time)}</CTableDataCell>
                        <CTableDataCell>
                          <CButton
                            color="info"
                            variant="outline"
                            onClick={() => handleViewClick(trip._id)}
                            style={{ marginRight: '5px' }}
                          >
                            👁️
                          </CButton>
                          <CButton
                            color="info"
                            variant="outline"
                            onClick={() => endTrip(trip._id)}
                            disabled={trip.status === 'completed'}
                          >
                            End Trip
                          </CButton>
                        </CTableDataCell>
                      </CTableRow>
                    ))
                  ) : (
                    <CTableRow>
                      <CTableDataCell colSpan="8" className="text-center">
                        No results found
                      </CTableDataCell>
                    </CTableRow>
                  )}
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
