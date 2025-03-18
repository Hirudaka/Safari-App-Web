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

// Utility function to format decimal hours into AM/PM time
const formatTime = (decimalHours) => {
  if (decimalHours == null) return 'N/A'
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

  // Function to parse the entry_time string into decimal hours
  const parseEntryTime = (entryTimeString) => {
    const date = new Date(entryTimeString) // Convert string to Date object
    if (isNaN(date.getTime())) {
      return null // Invalid date
    }
    // Extract hours and minutes in UTC (GMT) to avoid timezone conversion
    const hours = date.getUTCHours()
    const minutes = date.getUTCMinutes()
    return hours + minutes / 60 // Convert to decimal hours
  }

  // Function to calculate the average of an array
  const calculateAverage = (arr) => {
    if (!Array.isArray(arr) || arr.length === 0) return 'N/A'
    const sum = arr.reduce((acc, val) => acc + val, 0)
    return (sum / arr.length).toFixed(2) // Round to 2 decimal places
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
                    <CTableHeaderCell>Avg Traffic Level</CTableHeaderCell>
                    <CTableHeaderCell>Trip Time</CTableHeaderCell>
                    <CTableHeaderCell>Avg Speed</CTableHeaderCell>
                    <CTableHeaderCell>Estimated Exit Time</CTableHeaderCell>
                    <CTableHeaderCell>Booked Driver</CTableHeaderCell>
                  </CTableRow>
                </CTableHead>
                <CTableBody>
                  {schedules.map((trip, index) => {
                    const entryTimeDecimal = parseEntryTime(trip.entry_time)
                    const entryTimeFormatted =
                      entryTimeDecimal !== null ? formatTime(entryTimeDecimal) : 'Invalid Time'

                    const tripTimeFormatted = trip.trip_time
                      ? `${Math.floor(trip.trip_time)}h ${Math.round((trip.trip_time % 1) * 60)}m`
                      : 'N/A'

                    const exitTimeDecimal =
                      entryTimeDecimal !== null && trip.trip_time
                        ? entryTimeDecimal + trip.trip_time
                        : null
                    const exitTimeFormatted =
                      exitTimeDecimal !== null ? formatTime(exitTimeDecimal) : 'N/A'

                    const avgCongestion = calculateAverage(trip.congestion)
                    const avgSpeed = calculateAverage(trip.speed)

                    return (
                      <CTableRow
                        key={index}
                        className="pop-in-row"
                        style={{ animationDelay: `${0.1 * index}s` }}
                      >
                        <CTableDataCell>
                          <CCard align="middle">{index + 1}</CCard>
                        </CTableDataCell>
                        <CTableDataCell>
                          <CCard align="middle">{entryTimeFormatted}</CCard>
                        </CTableDataCell>
                        <CTableDataCell>
                          <CCard align="middle">{avgCongestion}</CCard>
                        </CTableDataCell>
                        <CTableDataCell>
                          <CCard align="middle">{tripTimeFormatted}</CCard>
                        </CTableDataCell>
                        <CTableDataCell>
                          <CCard align="middle">{avgSpeed} km/h</CCard>
                        </CTableDataCell>
                        <CTableDataCell>
                          <CCard align="middle">{exitTimeFormatted}</CCard>
                        </CTableDataCell>
                        <CTableDataCell>
                          <CCard align="middle">{trip.driverName}</CCard>
                        </CTableDataCell>
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
