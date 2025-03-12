import React, { useState, useEffect } from 'react'
import {
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

// Utility function to format time in AM/PM
const formatTime = (decimalHours) => {
  const totalMinutes = Math.round(decimalHours * 60)
  const hours = Math.floor(totalMinutes / 60)
  const minutes = totalMinutes % 60

  const period = hours >= 12 ? 'PM' : 'AM'
  const formattedHours = hours % 12 || 12
  const formattedMinutes = minutes.toString().padStart(2, '0')

  return `${formattedHours}:${formattedMinutes} ${period}`
}

const Schedules = () => {
  const [schedules, setSchedules] = useState([])
  const [loading, setLoading] = useState(true)

  // Fetch optimized schedules from API
  const fetchSchedules = async () => {
    setLoading(true)
    try {
      const response = await fetch('http://127.0.0.1:5001/api/optimized_schedule')
      const data = await response.json()
      if (data.optimized_schedule && Array.isArray(data.optimized_schedule)) {
        setSchedules(data.optimized_schedule)
      } else {
        setSchedules([])
      }
    } catch (error) {
      console.error('Error fetching schedules:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchSchedules()
  }, [])

  // Generate schedules and refresh the table
  const generateSchedules = async () => {
    setLoading(true)
    try {
      const response = await fetch('http://127.0.0.1:5001/api/schedule', { method: 'GET' })
      if (response.ok) {
        await fetchSchedules()
      }
    } catch (error) {
      console.error('Error generating schedules:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <CRow>
      <CCol lg={12} md={10} sm={12} className="mx-auto">
        <CCard className="mb-4">
          <CCardHeader>
            <strong>Trip Schedules</strong>
            <CButton color="primary" className="ms-3" onClick={generateSchedules}>
              Generate Schedules
            </CButton>
            <div className="mt-2">
              <strong>Total Schedules: {schedules.length}</strong>
            </div>
          </CCardHeader>
          <CCardBody>
            {loading ? (
              <div>Loading...</div>
            ) : schedules.length === 0 ? (
              <div>No schedules available.</div>
            ) : (
              <CTable align="middle" className="mb-0 border" hover responsive>
                <CTableHead>
                  <CTableRow>
                    <CTableHeaderCell>#</CTableHeaderCell>
                    <CTableHeaderCell>Entry Time</CTableHeaderCell>
                    <CTableHeaderCell>Traffic Level</CTableHeaderCell>
                    <CTableHeaderCell>Trip Time</CTableHeaderCell>
                    <CTableHeaderCell>Speed (km/h)</CTableHeaderCell>
                    <CTableHeaderCell>Estimated Exit Time</CTableHeaderCell>
                    <CTableHeaderCell>Booked Driver</CTableHeaderCell>
                  </CTableRow>
                </CTableHead>
                <CTableBody>
                  {schedules.map((trip, index) => {
                    const entryTimeFormatted = formatTime(trip.entry_time)
                    const tripTimeFormatted = `${Math.floor(trip.trip_time)}h ${Math.round(
                      (trip.trip_time % 1) * 60,
                    )}m`
                    const exitTimeFormatted = formatTime(trip.entry_time + trip.trip_time)

                    return (
                      <CTableRow key={index}>
                        <CTableDataCell>{index + 1}</CTableDataCell>
                        <CTableDataCell>{entryTimeFormatted}</CTableDataCell>
                        <CTableDataCell>{trip.congestion}</CTableDataCell>
                        <CTableDataCell>{tripTimeFormatted}</CTableDataCell>
                        <CTableDataCell>{trip.speed.join(' - ')} km/h</CTableDataCell>
                        <CTableDataCell>{exitTimeFormatted}</CTableDataCell>
                        <CTableDataCell>{trip.driverName}</CTableDataCell>
                      </CTableRow>
                    )
                  })}
                </CTableBody>
              </CTable>
            )}
          </CCardBody>
        </CCard>
      </CCol>
    </CRow>
  )
}

export default Schedules
