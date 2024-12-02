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
  const formattedHours = hours % 12 || 12 // Convert to 12-hour format
  const formattedMinutes = minutes.toString().padStart(2, '0') // Ensure two-digit minutes

  return `${formattedHours}:${formattedMinutes} ${period}`
}

const Schedules = () => {
  const [schedules, setSchedules] = useState([]) // State to store schedule data
  const [loading, setLoading] = useState(true) // Loading state

  // Fetch optimized schedule from API
  const fetchSchedules = async () => {
    setLoading(true) // Set loading to true while fetching data
    try {
      const response = await fetch('http://127.0.0.1:5001/api/optimized_schedule') // API endpoint
      const data = await response.json()
      setSchedules(data.optimized_schedule.schedule) // Set fetched schedules
    } catch (error) {
      console.error('Error fetching schedules:', error)
    } finally {
      setLoading(false) // Set loading to false after data is fetched
    }
  }

  useEffect(() => {
    fetchSchedules()
  }, [])

  // Generate schedules and refresh the table
  const generateSchedules = async () => {
    setLoading(true) // Set loading while generating schedules
    try {
      const response = await fetch('http://127.0.0.1:5001/api/schedule', { method: 'GET' }) // GET request to generate schedules
      if (response.ok) {
        await fetchSchedules() // Refresh the schedules after generating
      }
    } catch (error) {
      console.error('Error generating schedules:', error)
    } finally {
      setLoading(false) // Ensure loading is stopped
    }
  }

  // Calculate total schedules
  const totalSchedules = schedules.reduce((count, group) => count + group.length, 0)

  return (
    <CRow>
      <CCol lg={12} md={10} sm={12} className="mx-auto">
        <CCard className="mb-4">
          <CCardHeader>
            Trip Schedules
            <CButton color="primary" className="ms-3" onClick={generateSchedules}>
              Generate Schedules
            </CButton>
            <div className="mt-2">
              <strong>Total Schedules: {totalSchedules}</strong>
            </div>
          </CCardHeader>
          <CCardBody>
            {loading ? (
              <div>Loading...</div>
            ) : (
              <CTable align="middle" className="mb-0 border" hover responsive>
                <CTableHead>
                  <CTableRow>
                    <CTableHeaderCell>Schedule</CTableHeaderCell>
                    <CTableHeaderCell>Entry Time</CTableHeaderCell>
                    <CTableHeaderCell>Traffic Level</CTableHeaderCell>
                    <CTableHeaderCell>Trip Time</CTableHeaderCell>
                    <CTableHeaderCell>Speed (km/h)</CTableHeaderCell>
                    <CTableHeaderCell>Estimated Exit Time</CTableHeaderCell>
                  </CTableRow>
                </CTableHead>
                <CTableBody>
                  {schedules.map((scheduleGroup, groupIndex) =>
                    scheduleGroup.map((trip, index) => {
                      const entryTimeFormatted = formatTime(trip.entry_time)
                      const tripTimeFormatted = `${Math.floor(trip.trip_time)}h ${Math.round((trip.trip_time % 1) * 60)}m` // Keep trip time in hours and minutes
                      const exitTimeFormatted = formatTime(trip.entry_time + trip.trip_time)

                      return (
                        <CTableRow
                          key={`${groupIndex}-${index}`}
                          className="pop-in-row"
                          style={{ animationDelay: `${0.1 * index}s` }} // Stagger animation delay for each row
                        >
                          <CTableDataCell>
                            <CCard align="middle">Schedule {index + 1}</CCard>
                          </CTableDataCell>
                          <CTableDataCell>
                            {' '}
                            <CCard align="middle">{entryTimeFormatted}</CCard>
                          </CTableDataCell>
                          <CTableDataCell>
                            {' '}
                            <CCard align="middle">{trip.congestion}</CCard>
                          </CTableDataCell>
                          <CTableDataCell>
                            {' '}
                            <CCard align="middle">{tripTimeFormatted}</CCard>
                          </CTableDataCell>
                          <CTableDataCell>
                            {' '}
                            <CCard align="middle">{trip.speed.join(' - ')} km/h</CCard>
                          </CTableDataCell>
                          <CTableDataCell>
                            {' '}
                            <CCard align="middle">{exitTimeFormatted}</CCard>
                          </CTableDataCell>
                        </CTableRow>
                      )
                    }),
                  )}
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
