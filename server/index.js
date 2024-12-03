const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json());

// Connect to MongoDB
mongoose.connect('mongodb://localhost:27017/worldathletedataset', {
    useNewUrlParser: true,
    useUnifiedTopology: true,
});

// Athlete Schema
const athleteSchema = new mongoose.Schema({
    _id: String,
    url: String,
    details: {
        name: String,
    },
    events: [String],
    country: String,
    date_of_birth: String,
    athlete_code: String,
    highest_event_ranking: {
        ranking: String,
        event: String,
    },
    image_url: String,
    personal_bests: [Object],
    additional_events: [
        {
            title: String,
            result: String,
            date: String,
            score: String,
        },
    ],
});

const Athlete = mongoose.model('athletes_details', athleteSchema);

// Fetch all athletes or search by query
app.get('/api/athletes', async (req, res) => {
    const { query } = req.query; // Search query
    const filter = query
        ? { 'details.name': new RegExp(query, 'i') } // Case-insensitive name search
        : {};
    try {
        const athletes = await Athlete.find(filter);
        res.json(athletes);
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: 'Error fetching athletes' });
    }
});

// Add sample data to the database (only for testing)
app.post('/api/athletes', async (req, res) => {
    try {
        const newAthlete = new Athlete(req.body);
        await newAthlete.save();
        res.status(201).json(newAthlete);
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: 'Error saving athlete' });
    }
});

// Start server
const PORT = 5000;
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
