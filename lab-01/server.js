// server.js
// Lab 1: Node.js and Express Server

const express = require('express');
const app = express();
const PORT = 3000;

// Route 1: GET / - Returns a welcome message
app.get('/', (req, res) => {
  res.status(200).send('Welcome to Lab 1 Node.js and Express Server');
});

// Route 2: GET /about - Returns student details as JSON
app.get('/about', (req, res) => {
  res.status(200).json({
    name: 'P. Pradeep Yadav',
    registrationNumber: '252U1R7083',
    section: 'CSE FSD 2B'
  });
});

// Route 3: GET /time - Returns current date and time using new Date()
app.get('/time', (req, res) => {
  const currentTime = new Date();
  res.status(200).send(`Current Date and Time: ${currentTime.toString()}`);
});

// Route 4: Catch-all 404 handler for unknown paths
app.use((req, res) => {
  res.status(404).send('404 - Route Not Found');
});

// Start Express server on port 3000
app.listen(PORT, () => {
  console.log(`Express server is running on http://localhost:${PORT}`);
});
