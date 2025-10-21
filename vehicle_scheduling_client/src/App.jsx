// import { useState, useEffect } from 'react';
// import './App.css';

// function App() {
//   const [drivers, setDrivers] = useState([]);  // State to store driver data
//   const [loading, setLoading] = useState(true); // State to show loading spinner

//   // Fetch driver data from the backend when the component mounts
//   useEffect(() => {
//     async function fetchDrivers() {
//       try {
//         const response = await fetch('http://127.0.0.1:5001/get_drivers'); // Replace with your actual API endpoint
//         const data = await response.json();
//         setDrivers(data.drivers); // Set the fetched drivers to state
//       } catch (error) {
//         console.error('Error fetching drivers:', error);
//       } finally {
//         setLoading(false); // Set loading to false after data is fetched
//       }
//     }

//     fetchDrivers();
//   }, []);

//   return (
//     <div className="App">
//       <h1>Driver List</h1>

//       {loading ? (
//         <p>Loading drivers...</p> // Display loading message while waiting for data
//       ) : (
//         <div>
//           <h2>Registered Drivers</h2>
//           <ul>
//             {drivers.map((driver, index) => (
//               <li key={index}>
//                 <div>
//                   <h3>{driver.name}</h3>
//                   <p><strong>Email:</strong> {driver.email}</p>
//                   <p><strong>Phone:</strong> {driver.phone}</p>
//                   <p><strong>Vehicle ID:</strong> {driver.vehicle_id}</p>
//                   <p><strong>Driver ID:</strong> {driver.driver_id}</p>
//                   <div>
//                     <h4>QR Code:</h4>
//                     {/* Check if qr_image exists and is valid */}
//                     {driver.qr_code_image ? (
//                       <img 
//                         src={`data:image/png;base64,${driver.qr_code_image}`}  
//                         alt={`QR code for ${driver.name}`}
//                         style={{ width: '150px', height: '150px' }}
//                       />
//                     ) : (
//                       <p>No QR code available</p>
//                     )}
//                   </div>
//                 </div>
//                 <hr />
//               </li>
//             ))}
//           </ul>
//         </div>
//       )}
//     </div>
//   );
// }

// export default App;
import { useState, useEffect } from 'react';
import './App.css';

function App() {
  // States for schedule data and loading
  const [schedule, setSchedule] = useState([]);
  const [loading, setLoading] = useState(true);

  // States for driver registration form
  const [driverName, setDriverName] = useState('');
  const [driverEmail, setDriverEmail] = useState('');
  const [driverPhone, setDriverPhone] = useState('');
  const [vehicleId, setVehicleId] = useState('');

  // Fetch schedule data from the backend when the component mounts
  useEffect(() => {
    async function fetchSchedule() {
      try {
        const response = await fetch('http://127.0.0.1:5001/api/schedule'); // Replace with your actual API endpoint
        const data = await response.json();
        setSchedule(data.schedule); // Set the fetched schedule to state
      } catch (error) {
        console.error('Error fetching schedule:', error);
      } finally {
        setLoading(false); // Set loading to false after data is fetched
      }
    }

    fetchSchedule();
  }, []);

  // Handle driver registration form submission
  const handleRegisterDriver = async (e) => {
    e.preventDefault(); // Prevent the default form submission

    const driverData = {
      name: driverName,
      email: driverEmail,
      phone: driverPhone,
      vehicle_id: vehicleId,
    };

    try {
      const response = await fetch('http://127.0.0.1:5001/register_driver', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(driverData),
      });
      
      const result = await response.json();
      if (response.ok) {
        alert(`Driver registered successfully! Driver ID: ${result.driver_id}`);
      } else {
        alert(`Error: ${result.error}`);
      }
    } catch (error) {
      console.error('Error registering driver:', error);
    }
  };

  return (
    <div className="App">
      <h1>Vehicle Scheduling</h1>

      {loading ? (
        <p>Loading schedule...</p> // Display loading message while waiting for data
      ) : (
        <div>
          <h2>Scheduled Vehicles</h2>
          <ul>
            {schedule.map((vehicle, index) => (
              <li key={index}>
                <div>
                  <h3>Vehicle {index + 1}</h3>
                  <p><strong>Entry Time:</strong> {vehicle.entry_time} hours</p>
                  <p><strong>Trip Time:</strong> {vehicle.trip_time} hours</p>
                  <p><strong>Congestion Level:</strong> {vehicle.congestion}</p>
                  <p><strong>Speed:</strong> {vehicle.speed} km/h</p>
                </div>
                <hr />
              </li>
            ))}
          </ul>
        </div>
      )}

      <div>
        <h2>Register Driver</h2>
        <form onSubmit={handleRegisterDriver}>
          <div>
            <label htmlFor="driverName">Name:</label>
            <input
              type="text"
              id="driverName"
              value={driverName}
              onChange={(e) => setDriverName(e.target.value)}
              required
            />
          </div>

          <div>
            <label htmlFor="driverEmail">Email:</label>
            <input
              type="email"
              id="driverEmail"
              value={driverEmail}
              onChange={(e) => setDriverEmail(e.target.value)}
              required
            />
          </div>

          <div>
            <label htmlFor="driverPhone">Phone:</label>
            <input
              type="tel"
              id="driverPhone"
              value={driverPhone}
              onChange={(e) => setDriverPhone(e.target.value)}
              required
            />
          </div>

          <div>
            <label htmlFor="vehicleId">Vehicle ID:</label>
            <input
              type="text"
              id="vehicleId"
              value={vehicleId}
              onChange={(e) => setVehicleId(e.target.value)}
              required
            />
          </div>

          <button type="submit">Register Driver</button>
        </form>
      </div>
    </div>
  );
}

export default App;
