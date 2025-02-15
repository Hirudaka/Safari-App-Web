import React, { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { CCard, CCardBody, CCardHeader, CCol, CRow } from '@coreui/react'
import { MapContainer, TileLayer, CircleMarker, Polyline } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import 'leaflet-routing-machine'

let DefaultIcon = L.icon({
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
})
L.Marker.prototype.options.icon = DefaultIcon

const mapContainerStyle = {
  width: '100%',
  height: '450px',
}

const Trip = () => {
  const { tripId } = useParams()
  const [trip, setTrip] = useState(null)
  const [drivers, setDrivers] = useState([])
  const [loading, setLoading] = useState(true)
  const [driverLoading, setDriverLoading] = useState(true)

  useEffect(() => {
    async function fetchTripDetails() {
      try {
        const response = await fetch(`http://127.0.0.1:5001/api/trips/${tripId}`)
        const data = await response.json()
        if (response.ok) {
          setTrip(data)
        } else {
          console.error('Trip not found:', data.error)
        }
      } catch (error) {
        console.error('Error fetching trip details:', error)
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
      } finally {
        setDriverLoading(false)
      }
    }

    fetchTripDetails()
    fetchDrivers()
  }, [tripId])

  const getDriverName = (driverId) => {
    const driver = drivers.find((d) => String(d.driver_id) === String(driverId))
    return driver ? driver.name : 'Unknown Driver'
  }

  // Function to get the last location
  const getLastLocation = () => {
    if (trip && trip.locations && trip.locations.length > 0) {
      return trip.locations[trip.locations.length - 1]
    }
    return null
  }

  const getLastSpeed = (speedArray) => {
    if (Array.isArray(speedArray) && speedArray.length > 0) {
      return speedArray[speedArray.length - 1]
    }
    return 'N/A'
  }

  if (loading) {
    return <div>Loading trip details...</div>
  }

  // Function to calculate the route between locations and display the route only (in red)
  const displayRoute = (map, locations) => {
    if (locations.length < 2) return

    const waypoints = locations.map((location) => L.latLng(location[0], location[1]))

    // Create the route using leaflet-routing-machine
    L.Routing.control({
      waypoints: waypoints,
      routeWhileDragging: true,
      createMarker: () => null,
      lineOptions: {
        styles: [
          {
            color: 'red',
            weight: 5,
            opacity: 0.7,
          },
        ],
      },
    }).addTo(map)
  }

  const formatEntryTime = (entryTime) => {
    const date = new Date(entryTime)
    const formattedDate = date.toLocaleDateString()
    const formattedTime = date.toLocaleTimeString()
    return { formattedDate, formattedTime }
  }

  if (loading) {
    return <div>Loading trip details...</div>
  }

  const lastLocation = getLastLocation()
  const { formattedDate, formattedTime } = formatEntryTime(trip.entry_time)

  return (
    <CRow>
      <CCol lg={12} md={10} sm={12} className="mx-auto">
        <CCard className="mb-4">
          <CCardHeader>
            <h4>Trip Details</h4>
          </CCardHeader>
          <CCardBody>
            {trip ? (
              <div>
                <table className="table table-bordered">
                  <thead>
                    <tr>
                      <th>Attribute</th>
                      <th>Value</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>
                        <strong>Driver</strong>
                      </td>
                      <td>{driverLoading ? 'Loading driver...' : getDriverName(trip.driver_id)}</td>
                    </tr>
                    <tr>
                      <td>
                        <strong>Status</strong>
                      </td>
                      <td>{trip.status}</td>
                    </tr>
                    <tr>
                      <td>
                        <strong>Start Date</strong>
                      </td>
                      <td>{formattedDate}</td>
                    </tr>
                    <tr>
                      <td>
                        <strong>Start Time</strong>
                      </td>
                      <td>{formattedTime}</td>
                    </tr>
                    <tr>
                      <td>
                        <strong>Last Recorded Speed</strong>
                      </td>
                      <td>{getLastSpeed(trip.speed)} km/h</td>
                    </tr>
                  </tbody>
                </table>
                {trip.locations && trip.locations.length >= 2 ? (
                  <MapContainer
                    style={mapContainerStyle}
                    center={lastLocation ? lastLocation : trip.locations[0]} // Center map at the last location
                    zoom={12}
                    scrollWheelZoom={false}
                    whenCreated={(map) => {
                      // Ensure the route is created
                      displayRoute(map, trip.locations)
                    }}
                  >
                    <TileLayer
                      url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                      attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    />
                    {/* Display the locations as dots */}
                    {trip.locations.map((location, index) => {
                      // Check if the current location is the last location
                      const isLastLocation = trip.locations.length - 1 === index
                      return (
                        <CircleMarker
                          key={index}
                          center={[location[0], location[1]]}
                          radius={3}
                          color={isLastLocation ? 'green' : 'blue'}
                          fillOpacity={1}
                        />
                      )
                    })}
                    {/* Display the path by joining the locations with a polyline */}
                    <Polyline
                      positions={trip.locations.map((location) => [location[0], location[1]])}
                      color="red"
                      weight={5}
                      opacity={0.7}
                    />
                  </MapContainer>
                ) : (
                  <p>No location data available</p>
                )}
              </div>
            ) : (
              <p>Trip not found</p>
            )}
          </CCardBody>
        </CCard>
      </CCol>
    </CRow>
  )
}

export default Trip
