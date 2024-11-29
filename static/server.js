const express = require('express');
const mongoose = require('mongoose');
const multer = require('multer');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 3000;

// Connect to MongoDB
mongoose.connect('mongodb://localhost:27017/imageDB', {
    useNewUrlParser: true,
    useUnifiedTopology: true,
}).then(() => console.log('Connected to MongoDB'))
  .catch(err => console.error('Could not connect to MongoDB:', err));

// Create a schema and model for storing images
const imageSchema = new mongoose.Schema({
    name: String,
    image: {
        data: Buffer,
        contentType: String,
    },
});

const Image = mongoose.model('Image', imageSchema);

// Set up multer for file uploads
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, 'uploads/');
    },
    filename: (req, file, cb) => {
        cb(null, file.fieldname + '-' + Date.now() + path.extname(file.originalname));
    },
});

const upload = multer({ storage: storage });

// Create an endpoint for image upload
app.post('/upload', upload.single('image'), async (req, res) => {
    const newImage = new Image({
        name: req.file.filename,
        image: {
            data: fs.readFileSync(path.join(__dirname, 'uploads', req.file.filename)),
            contentType: req.file.mimetype,
        },
    });

    try {
        await newImage.save();
        res.send('Image uploaded and saved to database successfully');
    } catch (err) {
        console.error('Error saving image:', err);
        res.status(500).send('Error saving image');
    }
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
});
