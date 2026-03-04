# Invoice-App
The AI-Powered Voice Invoice App is a full-stack MERN application that automates invoice management. It features JWT authentication , MySQL storage via Sequelize , and a React frontend. Key highlights include Web Speech API for hands-free item selection and OpenAI GPT-3.5 to parse voice transcripts into structured JSON data.

🧾 AI-Powered Voice Invoice AppA modern full-stack application designed to automate and simplify invoice management through Artificial Intelligence and Voice Processing.

🚀 Key FeaturesVoice-to-Invoice: Utilize built-in speech recognition to select items and fill invoice details through voice commands.AI Intelligent Parsing: Integrated OpenAI GPT-3.5 Turbo to extract structured data from natural language voice transcripts.Automated Matching: Automatically matches voice input against a predefined item list to auto-populate amounts and descriptions.Secure Access: Protected routes and session management using JWT and LocalStorage.Responsive Dashboard: A sleek, amethyst-themed UI built with React and Bootstrap.

🏗️ Tech StackFrontend: React.js, React Router, Axios, Bootstrap 5.Backend: Node.js, Express.js.Database: MySQL with Sequelize ORM.AI/Voice: OpenAI API, Web Speech API (react-speech-recognition).🛠️ Installation & Setup1. Clone the repositoryBashgit clone https://github.com/yourusername/invoice-app.git
2. Backend SetupNavigate to the server folder and install dependencies: npm install.Create a .env file with your DB_NAME, DB_USER, DB_PASS, JWT_SECRET, and OPENAI_API_KEY.Start the server: npm start.3. Frontend SetupNavigate to the client folder and install dependencies: npm install.Verify the API base URL in api/axios.js points to your backend (default: http://localhost:5000/api).Launch the app: npm start.

📁 Project Structure/controllers: Handles business logic for Auth, Clients, Invoices, and Voice processing./models: Defines Sequelize schemas for MySQL tables./routes: API endpoint definitions./pages: React components for Login, Registration, and Dashboards.
