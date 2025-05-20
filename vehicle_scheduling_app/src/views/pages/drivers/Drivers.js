import React, { useEffect, useState } from 'react'

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

// Avatar placeholder in case driver image is not available
import avatarPlaceholder from 'src/assets/images/avatars/user.png'

const Drivers = () => {
  const [drivers, setDrivers] = useState([]) // State to store driver data
  const [loading, setLoading] = useState(true) // State to show loading spinner

  // Fetch driver data from the backend when the component mounts
  useEffect(() => {
    async function fetchDrivers() {
      try {
        const response = await fetch('https://nasa-api-ennr.onrender.com/get_drivers') // Replace with your actual API endpoint
        const data = await response.json()
        setDrivers(data.drivers) // Set the fetched drivers to state
      } catch (error) {
        console.error('Error fetching drivers:', error)
      } finally {
        setLoading(false) // Set loading to false after data is fetched
      }
    }

    fetchDrivers()
  }, [])

  const getStatusColor = (status) => {
    // Map status to badge color
    switch (status) {
      case 'active':
        return 'success'
      case 'inactive':
        return 'secondary'
      case 'suspended':
        return 'danger'
      default:
        return 'warning'
    }
  }

  const getDriverAvatar = (avatar) => {
    return avatar || avatarPlaceholder // Return avatar if available, otherwise placeholder
  }

  return (
    <>
      <CRow>
        <CCol xs>
          <CCard className="mb-4">
            <CCardHeader>Driver Details</CCardHeader>
            <CCardBody>
              {loading ? (
                <div>Loading...</div>
              ) : (
                <CTable align="middle" className="mb-0 border" hover responsive>
                  <CTableHead>
                    <CTableRow>
                      <CTableHeaderCell>Avatar</CTableHeaderCell>
                      <CTableHeaderCell>Name</CTableHeaderCell>
                      <CTableHeaderCell>Status</CTableHeaderCell>
                      <CTableHeaderCell>Email</CTableHeaderCell>
                      <CTableHeaderCell>Phone</CTableHeaderCell>
                      <CTableHeaderCell>QR</CTableHeaderCell>
                    </CTableRow>
                  </CTableHead>
                  <CTableBody>
                    {drivers.map((driver) => (
                      <CTableRow key={driver.driver_id}>
                        <CTableDataCell>
                          <CAvatar size="md" src={getDriverAvatar(driver.avatar)} />
                        </CTableDataCell>
                        <CTableDataCell>{driver.name}</CTableDataCell>
                        <CTableDataCell>
                          <span className={`badge bg-${getStatusColor(driver.status)}`}></span>
                        </CTableDataCell>
                        <CTableDataCell>{driver.email || 'Not Provided'}</CTableDataCell>
                        <CTableDataCell>{driver.phone || 'Not Provided'}</CTableDataCell>
                        <CTableDataCell>
                          <img
                            src={`data:image/png;base64,${driver.qr_code_image}`}
                            alt={`QR code for ${driver.name}`}
                            style={{ width: '150px', height: '150px' }}
                          />
                        </CTableDataCell>
                      </CTableRow>
                    ))}
                  </CTableBody>
                </CTable>
              )}
            </CCardBody>
          </CCard>
        </CCol>
      </CRow>
    </>
  )
}

export default Drivers
