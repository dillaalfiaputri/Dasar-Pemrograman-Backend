// import express
import express from "express";

// init express
const app = express();

// basic route
app.get('/', (req, res) => {
  res.send('Hello World');
});

// listen on port 3000
app.listen(3000, () => {
  console.log('Server Running at http://localhost:3000');
});