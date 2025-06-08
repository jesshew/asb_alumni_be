// Import required modules
const express = require('express');

// Constants
const PORT = process.env.PORT || 3000; // Server port

// Initialize Express app
const app = express();

// Middleware to parse JSON requests
app.use(express.json());

// Health check endpoint
app.get('/health', (req, res) => {
  // Respond with a simple status message
  res.json({ status: 'ok' });
});

// Start the server
app.listen(PORT, () => {
  // Log server start
  console.log(`Server is running on port ${PORT}`);
}); 