const { Sequelize } = require('sequelize');
require('dotenv').config();

const sequelize = new Sequelize(
  process.env.DB_NAME,
  process.env.DB_USER,
  process.env.DB_PASS,
  {
    host: process.env.DB_HOST,
    dialect: "mysql",
    logging: false,
  }
);

module.exports = sequelize;

const User = require('../models/User');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');

exports.register = async (req, res) => {
  const { email, password } = req.body;

  try {
    const userExists = await User.findOne({ where: { email } });
    if (userExists) {
      return res.status(400).json({ msg: 'User already exists' });
    }

    const hashedPassword = await bcrypt.hash(password, 10);

    await User.create({
      email,
      password: hashedPassword,
    });

    res.status(201).json({ msg: 'User registered successfully' });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

exports.login = async (req, res) => {
  const { email, password } = req.body;

  try {
    const user = await User.findOne({ where: { email } });

    if (!user) {
      return res.status(404).json({ msg: 'User not found' });
    }

    const isPasswordValid = await bcrypt.compare(password, user.password);

    if (!isPasswordValid) {
      return res.status(401).json({ msg: 'Invalid credentials' });
    }

    const token = jwt.sign({ id: user.id }, process.env.JWT_SECRET, {
      expiresIn: '2h',
    });

    res.status(200).json({ token });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

const Client = require('../models/Client');

exports.getClients = async (req, res) => {
  const clients = await Client.findAll();
  res.json(clients);
};

exports.addClient = async (req, res) => {
  const { name } = req.body;
  const client = await Client.create({ name });
  res.json(client);
};

exports.updateClient = async (req, res) => {
  const { id } = req.params;
  const { name } = req.body;
  const client = await Client.findByPk(id);
  if (client) {
    client.name = name;
    await client.save();
    res.json(client);
  } else {
    res.status(404).json({ msg: 'Client not found' });
  }
};

exports.deleteClient = async (req, res) => {
  const { id } = req.params;
  await Client.destroy({ where: { id } });
  res.json({ msg: 'Deleted' });
};

const Invoice = require('../models/Invoice');
const Client = require('../models/Client');

exports.getInvoices = async (req, res) => {
  const invoices = await Invoice.findAll({ include: Client });
  const formatted = invoices.map(i => ({
    id: i.id,
    amount: i.amount,
    date: i.date,
    clientId: i.clientId,
    clientName: i.Client.name
  }));
  res.json(formatted);
};

exports.addInvoice = async (req, res) => {
  const { amount, date, clientId } = req.body;
  const invoice = await Invoice.create({ amount, date, clientId });
  res.json(invoice);
};

exports.updateInvoice = async (req, res) => {
  const { id } = req.params;
  const { amount, date, clientId } = req.body;
  const invoice = await Invoice.findByPk(id);
  if (invoice) {
    invoice.amount = amount;
    invoice.date = date;
    invoice.clientId = clientId;
    await invoice.save();
    res.json(invoice);
  } else {
    res.status(404).json({ msg: 'Invoice not found' });
  }
};

exports.deleteInvoice = async (req, res) => {
  const { id } = req.params;
  await Invoice.destroy({ where: { id } });
  res.json({ msg: 'Deleted' });
};

const { OpenAI } = require('openai');
const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

exports.processVoiceInput = async (req, res) => {
  const { transcript } = req.body;

  try {
    const completion = await openai.chat.completions.create({
      messages: [
        {
          role: "system",
          content: "You are an assistant that extracts item names and quantities from user voice input. Return them as JSON with 'item' and 'quantity'. Example: [{ item: 'Ultrasonic Generator', quantity: 2 }]",
        },
        {
          role: "user",
          content: transcript,
        }
      ],
      model: "gpt-3.5-turbo"
    });

    const response = completion.choices[0].message.content;
    const parsed = JSON.parse(response);
    res.json(parsed);
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'Failed to process voice input' });
  }
};

const { DataTypes } = require('sequelize');
const sequelize = require('../config/db');

const Client = sequelize.define('Client', {
  name: {
    type: DataTypes.STRING,
    allowNull: false,
  }
});

module.exports = Client;

const { DataTypes } = require('sequelize');
const sequelize = require('../config/db');
const Client = require('./Client');

const Invoice = sequelize.define('Invoice', {
  amount: {
    type: DataTypes.FLOAT,
    allowNull: false,
  },
  date: {
    type: DataTypes.DATEONLY,
    allowNull: false,
  }
});

Invoice.belongsTo(Client, { foreignKey: 'clientId' });
Client.hasMany(Invoice, { foreignKey: 'clientId' });

module.exports = Invoice;

const { DataTypes } = require('sequelize');
const sequelize = require('../config/db');

const User = sequelize.define('User', {
  email: {
    type: DataTypes.STRING,
    allowNull: false,
    unique: true,
    validate: { isEmail: true }
  },
  password: {
    type: DataTypes.STRING,
    allowNull: false,
  }
});

module.exports = User;

const express = require('express');
const router = express.Router();
const { register, login } = require('../controllers/authController');

router.post('/register', register);
router.post('/login', login);

module.exports = router;

const express = require('express');
const router = express.Router();
const clientCtrl = require('../controllers/clientController');

router.get('/', clientCtrl.getClients);
router.post('/', clientCtrl.addClient);
router.put('/:id', clientCtrl.updateClient);
router.delete('/:id', clientCtrl.deleteClient);

module.exports = router;

const express = require('express');
const router = express.Router();
const invoiceCtrl = require('../controllers/invoiceController');

router.get('/', invoiceCtrl.getInvoices);
router.post('/', invoiceCtrl.addInvoice);
router.put('/:id', invoiceCtrl.updateInvoice);
router.delete('/:id', invoiceCtrl.deleteInvoice);

module.exports = router;

const express = require('express');
const router = express.Router();
const { processVoiceInput } = require('../controllers/voiceController');

router.post('/process', processVoiceInput);

module.exports = router;

const express = require('express');
const cors = require('cors');
const sequelize = require('./config/db');
const Client = require('./models/Client');
const Invoice = require('./models/Invoice');
const clientRoutes = require('./routes/clientRoutes');
const invoiceRoutes = require('./routes/invoiceRoutes');



require('dotenv').config();

const authRoutes = require('./routes/authRoutes');
const User = require('./models/User'); // Important to sync model
const app = express();


app.use(cors());
app.use(express.json());

app.use('/api/auth', authRoutes);
app.use('/api/clients', clientRoutes);
app.use('/api/invoices', invoiceRoutes);



app.get('/', (req, res) => res.send('Invoice App Backend Running'));

sequelize.sync().then(() => {
  console.log('✅ Database connected');
  app.listen(process.env.PORT, () =>
    console.log(`🚀 Server running on port ${process.env.PORT}`)
  );
});

<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <link rel="icon" href="%PUBLIC_URL%/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta
      name="description"
      content="Web site created using create-react-app"
    />
    <link rel="apple-touch-icon" href="%PUBLIC_URL%/logo192.png" />
    <!--
      manifest.json provides metadata used when your web app is installed on a
      user's mobile device or desktop. See https://developers.google.com/web/fundamentals/web-app-manifest/
    -->
    <link rel="manifest" href="%PUBLIC_URL%/manifest.json" />
    <!--
      Notice the use of %PUBLIC_URL% in the tags above.
      It will be replaced with the URL of the `public` folder during the build.
      Only files inside the `public` folder can be referenced from the HTML.

      Unlike "/favicon.ico" or "favicon.ico", "%PUBLIC_URL%/favicon.ico" will
      work correctly both with client-side routing and a non-root public URL.
      Learn how to configure a non-root public URL by running `npm run build`.
    -->
    <title>React App</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
    <!--
      This HTML file is a template.
      If you open it directly in the browser, you will see an empty page.

      You can add webfonts, meta tags, or analytics to this file.
      The build step will place the bundled scripts into the <body> tag.

      To begin the development, run `npm start` or `yarn start`.
      To create a production bundle, use `npm run build` or `yarn build`.
    -->
  </body>
</html>

{
  "short_name": "React App",
  "name": "Create React App Sample",
  "icons": [
    {
      "src": "favicon.ico",
      "sizes": "64x64 32x32 24x24 16x16",
      "type": "image/x-icon"
    },
    {
      "src": "logo192.png",
      "type": "image/png",
      "sizes": "192x192"
    },
    {
      "src": "logo512.png",
      "type": "image/png",
      "sizes": "512x512"
    }
  ],
  "start_url": ".",
  "display": "standalone",
  "theme_color": "#000000",
  "background_color": "#ffffff"
}

import axios from 'axios';

const API = axios.create({
  baseURL: 'http://localhost:5000/api', // this points to your backend
});

export default API;


import VoiceItemSelector from './components/VoiceItemSelector';

const itemList = ['Design Work', 'Web Development', 'Consultation', 'SEO', 'Logo Design'];

const InvoiceForm = () => {
  const [selectedItem, setSelectedItem] = useState("");

  return (
    <div>
      {/* Other invoice fields */}
      
      <VoiceItemSelector
        items={itemList}
        onItemSelect={(item) => setSelectedItem(item)}
      />

      <p>🔎 Selected by Voice: <strong>{selectedItem || "None"}</strong></p>
    </div>
  );
};

import React from 'react';
import { Link } from 'react-router-dom';

const Navbar = () => {
  return (
    <nav className="navbar navbar-expand-lg navbar-dark custom-navbar px-4">
      <Link className="navbar-brand" to="/dashboard">
        InvoiceApp
      </Link>

      <button
        className="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#navbarNav"
        aria-controls="navbarNav"
        aria-expanded="false"
        aria-label="Toggle navigation"
      >
        <span className="navbar-toggler-icon"></span>
      </button>

      <div className="collapse navbar-collapse" id="navbarNav">
        <ul className="navbar-nav ms-auto">
          <li className="nav-item">
            <Link className="nav-link" to="/">Dashboard</Link>
          </li>
          <li className="nav-item">
            <Link className="nav-link" to="/dashboard">Home Page</Link>
          </li>
          <li className="nav-item">
            <Link className="nav-link" to="/clients">Clients</Link>
          </li>
          <li className="nav-item">
            <Link className="nav-link" to="/invoices">Invoices</Link>
          </li>
        </ul>
      </div>
    </nav>
  );
};

export default Navbar;

import React from 'react';
import { Navigate } from 'react-router-dom';

const ProtectedRoute = ({ children }) => {
  const token = localStorage.getItem('authToken');

  if (!token) {
    return <Navigate to="/login" />;
  }

  return children;
};

export default ProtectedRoute;

import React, { useState, useRef } from 'react';

const VoiceItemSelector = () => {
  const [items, setItems] = useState([]);
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef(null);

  const initializeRecognition = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Speech Recognition API not supported in this browser.");
      return null;
    }
    const recognition = new SpeechRecognition();
    recognition.lang = 'en-US';
    recognition.continuous = true;
    recognition.interimResults = false;
    return recognition;
  };

  const startListening = () => {
    if (!recognitionRef.current) {
      recognitionRef.current = initializeRecognition();
      if (!recognitionRef.current) return;
    }

    recognitionRef.current.onresult = (event) => {
      const transcript = event.results[event.results.length - 1][0].transcript.trim();
      if (transcript && !items.includes(transcript)) {
        setItems(prevItems => [...prevItems, transcript]);
      }
    };

    recognitionRef.current.start();
    setIsListening(true);
  };

  const stopListening = () => {
    recognitionRef.current?.stop();
    setIsListening(false);
  };

  const resetItems = () => {
    stopListening();
    setItems([]);
  };

  return (
    <div style={{ padding: '1rem', border: '1px solid #ddd', borderRadius: '10px' }}>
      <h2>Voice Item Selector</h2>
      <div style={{ marginBottom: '1rem' }}>
        <button onClick={startListening} disabled={isListening} style={{ marginRight: '10px' }}>
          Start Listening
        </button>
        <button onClick={stopListening} disabled={!isListening} style={{ marginRight: '10px' }}>
          Stop Listening
        </button>
        <button onClick={resetItems}>
          Reset
        </button>
      </div>
      <ul>
        {items.map((item, index) => (
          <li key={index} style={{ fontWeight: 'bold' }}>{item}</li>
        ))}
      </ul>
    </div>
  );
};

export default VoiceItemSelector;

import React, { useEffect, useState } from 'react';
import Navbar from '../components/Navbar';

import API from '../api/axios';

const ClientListPage = () => {
  const [clients, setClients] = useState([]);
  const [name, setName] = useState('');
  const [editingId, setEditingId] = useState(null);

  const fetchClients = async () => {
    const res = await API.get('/clients');
    setClients(res.data);
  };

  useEffect(() => {
    fetchClients();
  }, []);

  const handleAddOrUpdate = async () => {
    if (editingId) {
      await API.put(`/clients/${editingId}`, { name });
    } else {
      await API.post('/clients', { name });
    }
    setName('');
    setEditingId(null);
    fetchClients();
  };

  const handleDelete = async id => {
    await API.delete(`/clients/${id}`);
    fetchClients();
  };

  const startEdit = client => {
    setName(client.name);
    setEditingId(client.id);
  };

  return (
   <>

     <Navbar />
    <div className="container mt-5">
      <h2 className="mb-4">Clients</h2>

      <div className="mb-3 d-flex gap-2">
        <input
          type="text"
          placeholder="Client Name"
          className="form-control"
          value={name}
          onChange={e => setName(e.target.value)}
        />
        <button className="btn btn-primary" onClick={handleAddOrUpdate}>
          {editingId ? 'Update' : 'Add'}
        </button>
      </div>

      <table className="table table-bordered">
        <thead>
          <tr>
            <th>Client ID</th>
            <th>Name</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {clients.map(client => (
            <tr key={client.id}>
              <td>{client.id}</td>
              <td>{client.name}</td>
              <td>
                <button className="btn btn-sm btn-warning me-2" onClick={() => startEdit(client)}>Edit</button>
                <button className="btn btn-sm btn-danger" onClick={() => handleDelete(client.id)}>Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
   </>
  );
};

export default ClientListPage;

.amethyst-heading {
  color: #8e44ad;
  font-weight: 700;
  letter-spacing: 0.5px;
}

/* DashboardPage.css */

.soft-purple {
  background: #a066c9; /* Slightly darker purple */
  color: purple;
  font-weight: 500;
  border: none;
  border-radius: 8px;
  padding: 10px 0;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(160, 102, 201, 0.3);
  text-align: center;
}

.soft-purple:hover {
  background: #8a4ebf; /* Even darker on hover */
  box-shadow: 0 6px 15px rgba(160, 102, 201, 0.5);
  transform: translateY(-1px);
}



.fancy-card {
  border: none;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(142, 68, 173, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  background: linear-gradient(145deg, #efe8f0, #f3e8f9);
}

.fancy-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 24px rgba(142, 68, 173, 0.25);
}

.btn-register {
  background-color: #883ba8;
  color: rgb(160, 82, 171);
  font-weight: 500;
  border: none;
  border-radius: 6px;
  padding: 10px;
  transition: background-color 0.3s ease;
}

.btn-register:hover {
  background-color:   #915ba8;
}

.btn-login {
  background-color: #8e44ad;
  color: white;
  font-weight: 500;
  border: none;
  border-radius: 6px;
  padding: 10px;
  transition: background-color 0.3s ease;
}

.btn-login:hover {
  background-color: #732d91;
}
import React from 'react';
import { useNavigate } from 'react-router-dom';
import './DashboardPage.css'; 

const DashboardPage = () => {
  const navigate = useNavigate();

  return (
    <div className="container mt-5">
      <h2 className="text-center mb-3 amethyst-heading">Welcome to the Invoice App</h2>
      <p className="text-center text-muted">Please register if you're new or login if you already have an account.</p>

      <div className="row justify-content-center mt-5 gap-4">
        <div className="col-md-5">
          <div className="card fancy-card">
            <div className="card-body text-center">
              <h5 className="card-title fw-bold">New Here?</h5>
              <p className="card-text">Create a new account to get started with the invoice system.</p>
              <button className="btn soft-purple w-100 mt-3" onClick={() => navigate('/register')}>Register</button>

            </div>
          </div>
        </div>

        <div className="col-md-5">
          <div className="card fancy-card">
            <div className="card-body text-center">
              <h5 className="card-title fw-bold">Already Registered?</h5>
              <p className="card-text">Login to your account and manage invoices and clients.</p>
              <button className="btn soft-purple w-100 mt-3" onClick={() => navigate('/login')}>Login</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
import React, { useState } from 'react';
import { Modal, Button, Form } from 'react-bootstrap';

const InvoiceModal = ({ show, handleClose, handleSave }) => {
  const [client, setClient] = useState('');
  const [amount, setAmount] = useState('');
  const [date, setDate] = useState('');

  const onSave = () => {
    handleSave({ client, amount, date });
    setClient('');
    setAmount('');
    setDate('');
  };

  return (
    <Modal show={show} onHide={handleClose} backdrop="static" centered>
      <Modal.Header closeButton>
        <Modal.Title>Add New Invoice</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Form>
          <Form.Group className="mb-3">
            <Form.Label>Client</Form.Label>
            <Form.Control
              type="text"
              placeholder="Enter client name"
              value={client}
              onChange={(e) => setClient(e.target.value)}
              required
            />
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Amount</Form.Label>
            <Form.Control
              type="number"
              placeholder="Enter amount"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              required
            />
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Date</Form.Label>
            <Form.Control
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              required
            />
          </Form.Group>
        </Form>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={handleClose}>Cancel</Button>
        <Button variant="primary" onClick={onSave}>Save Invoice</Button>
      </Modal.Footer>
    </Modal>
  );
};

export default InvoiceModal;
import React, { useState } from 'react';
import InvoiceModal from './InvoiceModal'; // Adjust path as needed

const InvoiceListPage = () => {
  const [showModal, setShowModal] = useState(false);
  const [invoices, setInvoices] = useState([]);

  const handleSaveInvoice = (newInvoice) => {
    // For now, just add to local state
    setInvoices([...invoices, newInvoice]);
    setShowModal(false);
  };

  return (
    <div className="container mt-5">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h2>Invoices</h2>
        <button className="btn btn-primary" onClick={() => setShowModal(true)}>
          + Create Invoice
        </button>
      </div>

      <table className="table table-striped">
        <thead>
          <tr>
            <th>Invoice ID</th>
            <th>Client</th>
            <th>Amount</th>
            <th>Date</th>
          </tr>
        </thead>
        <tbody>
          {invoices.map((inv, idx) => (
            <tr key={idx}>
              <td>{idx + 1}</td>
              <td>{inv.client}</td>
              <td>₹ {inv.amount}</td>
              <td>{inv.date}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <InvoiceModal
        show={showModal}
        handleClose={() => setShowModal(false)}
        handleSave={handleSaveInvoice}
      />
    </div>
  );
};

export default InvoiceListPage;
import React, { useState, useEffect } from 'react';
import API from '../api/axios';
import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';

const InvoiceModal = ({ show, handleClose }) => {
  const [clientId, setClientId] = useState('');
  const [amount, setAmount] = useState('');
  const [item, setItem] = useState('');
  const [dueDate, setDueDate] = useState('');
  const [itemList, setItemList] = useState([]);

  const { transcript, listening, resetTranscript } = useSpeechRecognition();

  // Sample item list – replace with API call if available
  useEffect(() => {
    const fetchItems = async () => {
      // Uncomment below if using backend API
      // const res = await API.get('/items');
      // setItemList(res.data);
      
      setItemList([
        { name: 'Ultrasonic Generator', price: 15000 },
        { name: 'Face Mask Roller Die', price: 9000 },
        { name: 'Ultrasonic Welding SPM', price: 25000 },
        { name: 'Repairing and Maintenance Service', price: 5000 }
      ]);
    };
    fetchItems();
  }, []);

  // Match transcript with items
  useEffect(() => {
    const matchedItem = itemList.find(itemObj =>
      transcript.toLowerCase().includes(itemObj.name.toLowerCase().split(' ')[0])
    );

    if (matchedItem) {
      setItem(matchedItem.name);
      setAmount(matchedItem.price);
    }
  }, [transcript, itemList]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const newInvoice = {
      item,
      clientId,
      amount,
      dueDate
    };

    try {
      await API.post('/invoices', newInvoice);
      alert('Invoice created successfully!');
      handleClose();
    } catch (error) {
      console.error('Error creating invoice:', error);
    }
  };

  return (
    <div className={`modal ${show ? 'd-block' : 'd-none'}`} tabIndex="-1">
      <div className="modal-dialog">
        <form onSubmit={handleSubmit}>
          <div className="modal-content">
            <div className="modal-header bg-purple text-white">
              <h5 className="modal-title">Create Invoice</h5>
              <button type="button" className="btn-close" onClick={handleClose}></button>
            </div>

            <div className="modal-body">
              {/* Client ID */}
              <div className="mb-3">
                <label htmlFor="clientId">Client ID</label>
                <input
                  type="text"
                  className="form-control"
                  id="clientId"
                  value={clientId}
                  onChange={(e) => setClientId(e.target.value)}
                  required
                />
              </div>

              {/* Item Dropdown */}
              <div className="mb-3">
                <label htmlFor="item">Item</label>
                <select
                  className="form-select"
                  id="item"
                  value={item}
                  onChange={(e) => setItem(e.target.value)}
                  required
                >
                  <option value="">-- Select an Item --</option>
                  {itemList.map((option, index) => (
                    <option key={index} value={option.name}>
                      {option.name}
                    </option>
                  ))}
                </select>
              </div>

              {/* Amount */}
              <div className="mb-3">
                <label htmlFor="amount">Amount (₹)</label>
                <input
                  type="number"
                  className="form-control"
                  id="amount"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  required
                />
              </div>

              {/* Due Date */}
              <div className="mb-3">
                <label htmlFor="dueDate">Due Date</label>
                <input
                  type="date"
                  className="form-control"
                  id="dueDate"
                  value={dueDate}
                  onChange={(e) => setDueDate(e.target.value)}
                  required
                />
              </div>

              {/* Speech Input */}
  

              <div className="mb-3">
                <label>🎤 Voice Input for Item Name</label>
                <div className="d-flex flex-wrap gap-2">
                  <button type="button" className="btn btn-outline-primary" onClick={SpeechRecognition.startListening}>
                    Start Listening
                  </button>
                  <button type="button" className="btn btn-outline-danger" onClick={SpeechRecognition.stopListening}>
                    Stop
                  </button>
                  <button type="button" className="btn btn-outline-dark" onClick={resetTranscript}>
                    Reset
                  </button>
                  <span className={`ms-3 badge ${listening ? 'bg-success' : 'bg-secondary'}`}>
                    {listening ? 'Listening...' : 'Not Listening'}
                  </span>
                </div>
                <p className="mt-2"><strong>Transcript:</strong> {transcript}</p>
              </div>
            </div>

            <div className="modal-footer">
              <button type="submit" className="btn btn-purple">Save Invoice</button>
              <button type="button" className="btn btn-secondary" onClick={handleClose}>Cancel</button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};

export default InvoiceModal;
import React, { useState } from 'react';
import API from '../api/axios';
import { useNavigate } from 'react-router-dom';

const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async e => {
  e.preventDefault();
  setError('');
  try {
    const res = await API.post('/auth/login', { email, password });
    const { token } = res.data;

    // ✅ Store token in localStorage
    localStorage.setItem('authToken', token);

    // ✅ Redirect to dashboard
    navigate('/dashboard');
  } catch (err) {
    console.error(err);
    setError(err.response?.data?.msg || 'Login failed');
  }
};



  return (
    <div className="container mt-5" style={{ maxWidth: '400px' }}>
      <h2 className="text-center mb-4">Login</h2>
      {error && <div className="alert alert-danger">{error}</div>}
      <form onSubmit={handleSubmit}>
        <div className="mb-3">
          <label>Email:</label>
          <input type="email" className="form-control" required value={email} onChange={e => setEmail(e.target.value)} />
        </div>
        <div className="mb-3">
          <label>Password:</label>
          <input type="password" className="form-control" required value={password} onChange={e => setPassword(e.target.value)} />
        </div>
        
        <button className="btn soft-purple w-100 mt-3" onClick={() => navigate('/Login')}>Login</button>
      </form>
    </div>
  );
};

export default LoginPage;
import React from 'react';
import Navbar from '../components/Navbar';

const ProtectedDashboard = () => {
  return (
   <>

     <Navbar />
    <div className="container mt-5">
      <h2 className="text-success">Welcome! You are logged in.</h2>
      <p className="lead">Here you'll manage clients, invoices, and more.</p>
      <button
  className="btn btn-outline-danger mt-3"
  onClick={() => {
    localStorage.removeItem('authToken');
    window.location.href = '/login';
  }}
>
  Logout
</button>

    </div>
    </>
  );
};

export default ProtectedDashboard;
.btn-register {
  background-color: #bb8fce;
  color: white;
  font-weight: 500;
  border: none;
  border-radius: 6px;
  padding: 10px;
  transition: background-color 0.3s ease, transform 0.2s ease;
}

.btn-register:hover {
  background-color: #af7ac5;
  transform: translateY(-2px);
  color: white;
}
import React, { useState } from 'react';
import API from '../api/axios';
import { useNavigate } from 'react-router-dom';
import './RegisterPage.css';

const RegisterPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async e => {
    e.preventDefault();
    setError('');
    try {
      await API.post('/auth/register', { email, password });
      alert('Registered successfully!');
      navigate('/login');
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.msg || 'Registration failed');
    }
  };

  return (
    <div className="container mt-5" style={{ maxWidth: '400px' }}>
      <h2 className="text-center mb-4">Register</h2>
      {error && <div className="alert alert-danger">{error}</div>}
      <form onSubmit={handleSubmit}>
        <div className="mb-3">
          <label>Email:</label>
          <input type="email" className="form-control" required value={email} onChange={e => setEmail(e.target.value)} />
        </div>
        <div className="mb-3">
          <label>Password:</label>
          <input type="password" className="form-control" required value={password} onChange={e => setPassword(e.target.value)} />
        </div>
        <button className="btn soft-purple w-100 mt-3" onClick={() => navigate('/Register')}>Register</button>
      </form>
    </div>
  );
};

export default RegisterPage;
body {
  background-color: #fdf6ff;
}
 
.btn-register {
  background-color: #bb8fce;
  color: white;
  font-weight: 500;
  border: none;
  transition: 0.3s ease-in-out;
}

.btn-register:hover {
  background-color: #af7ac5;
  color: white;
}

.btn-login {
  background-color: #8e44ad;
  color: white;
  font-weight: 500;
  border: none;
  transition: 0.3s ease-in-out;
}

.btn-login:hover {
  background-color: #732d91;
  color: white;
}

.custom-navbar {
  background-color: #9b59b6 !important; /* light sky blue */
}

/* Optional: Hover color for nav links */
.navbar .nav-link:hover {
  color: #002244 !important;
}

/* Optional: Active link highlight */
.navbar .nav-link.active {
  font-weight: bold;
  color: #002244 !important;
}

.btn-purple {
  background-color: #7e57c2;
  border-color: #7e57c2;
  color: white;
}

.btn-purple:hover {
  background-color: #6a1b9a;
  border-color: #6a1b9a;
}

import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Login from './pages/Login';
import DashboardPage from './pages/DashboardPage';
import RegisterPage from './pages/RegisterPage'
import ProtectedDashboard from './pages/ProtectedDashboard';
import ProtectedRoute from './components/ProtectedRoute';
import ClientListPage from './pages/ClientListPage';
import InvoiceListPage from './pages/InvoiceListPage';






function App() {
  return (
    <Router>
      <div className="container mt-5">
        
      

        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/dashboard" element={<ProtectedRoute> <ProtectedDashboard /> </ProtectedRoute> } />
          <Route path="/clients" element={<ProtectedRoute><ClientListPage /></ProtectedRoute>} />
          <Route path="/invoices" element={<ProtectedRoute><InvoiceListPage /></ProtectedRoute>} />

        </Routes>
      </div>
    </Router>
  );
}

export default App;
 import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './App.css';
import 'bootstrap/dist/css/bootstrap.min.css';

import 'bootstrap-icons/font/bootstrap-icons.css';




const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
import React from 'react';
import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';

const Testmic = () => {
  const { transcript } = useSpeechRecognition();
  
  return (
    <div>
      <h2>Speech Input:</h2>
      <p2>{transcript}</p2>
      <button onClick={SpeechRecognition.startListening}>Start</button>
      <button onClick={SpeechRecognition.stopListening}>Stop</button>
    </div>
  );
};

export default Testmic;
