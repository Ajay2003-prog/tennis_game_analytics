# 🎾 Game Analytics – Unlocking Tennis Data with SportRadar API

## 🌐 Live Project
**Streamlit Dashboard:** https://tennis-performance-analytics.streamlit.app/

## 📌 About the Project

Game Analytics – Unlocking Tennis Data with SportRadar API is a collaborative team project developed to collect, process, analyze, and visualize tennis-related data.

The project uses the SportRadar API to retrieve tennis competition, category, venue, complex, competitor, and ranking information. Python is used for data extraction and transformation, SQL for database management and analysis, and Streamlit for developing an interactive analytics dashboard.

The primary goal is to transform raw tennis data into structured information and meaningful analytical insights through data visualization.

## 🎯 Project Objectives

- Collect tennis data using SportRadar API.
- Extract and process nested JSON responses using Python.
- Clean and transform raw data into structured datasets.
- Store and manage data using relational SQL tables.
- Perform data analysis using SQL queries.
- Develop an interactive Streamlit dashboard.
- Generate meaningful insights through charts, KPIs, and visualizations.

## 🛠️ Technologies Used

- **Python** – Data extraction, cleaning, and transformation.
- **SportRadar API** – Tennis data collection.
- **Pandas** – Data manipulation and analysis.
- **SQL** – Database creation, management, and querying.
- **Streamlit** – Interactive dashboard development.
- **Plotly** – Data visualization.
- **GitHub** – Version control and collaboration.

## 🔄 Project Workflow

1. **Data Collection:** Fetch tennis-related information from SportRadar API.
2. **Data Extraction:** Retrieve competitions, complexes, venues, and doubles competitor rankings.
3. **Data Cleaning & Transformation:** Process JSON responses, handle missing values, and structure the data using Python.
4. **Database Management:** Create relational tables and establish primary and foreign key relationships using SQL.
5. **Data Analysis:** Execute SQL queries to analyze competition categories, competitor rankings, and country-wise statistics.
6. **Dashboard Development:** Build an interactive Streamlit dashboard to present analytical findings.
7. **Insights & Visualization:** Represent important statistics and findings through interactive charts, filters, and KPIs.

## 📊 Dashboard Features

- Interactive tennis analytics dashboard.
- Competition and category exploration.
- Competitor ranking analysis.
- Country-wise competitor distribution.
- Complex and venue analysis.
- Ranking points and leaderboard analysis.
- Interactive filters and data visualizations.
- Data-driven insights and statistical summaries.

## 🗄️ Database Tables

The project database is designed around the following core tables:

| Table Name | Description |
|---|---|
| categories | Competition category information |
| competitions | Competition details and classifications |
| complexes | Sports complex information |
| venues | Venue, city, country, and timezone details |
| competitors | Competitor information |
| competitor_rankings | Competitor rankings, points, and ranking movement |

## 👥 Team Members

This project was collaboratively developed by four team members.

| Member | Name |
|---|---|
| Member 1 | Chinnam Ajay Sai Phaneendra Reddy |
| Member 2 | Shubham Samarpit |
| Member 3 | Jithendra |
| Member 4 | Sahil Khan |

### Team Responsibilities

- SportRadar API integration and data collection.
- Python-based data processing and transformation.
- SQL database design and analytical queries.
- Data analysis and visualization.
- Streamlit dashboard development and integration.
- Project testing and documentation.

## ⚙️ Installation & Execution

### Step 1: Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

### Step 2: Navigate to the Project Directory

```bash
cd tennis-game-analytics
```

### Step 3: Install Required Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure API Credentials

Create a `.env` file and configure your SportRadar API key:

```env
SPORTRADAR_API_KEY=your_api_key
```

### Step 5: Run the Streamlit Application

```bash
streamlit run app.py
```

## 🌐 Live Demo

Explore the deployed application:

**https://tennis-performance-analytics.streamlit.app/**

## 💡 Key Learning Outcomes

- Working with third-party REST APIs.
- Handling nested JSON data.
- Data cleaning and transformation using Python.
- Relational database design and SQL querying.
- Exploratory data analysis.
- Interactive dashboard development using Streamlit.
- Team collaboration and project integration using GitHub.

## 🏁 Conclusion

The Tennis Game Analytics project demonstrates an end-to-end data analytics workflow by integrating API data collection, Python programming, SQL database management, data analysis, and interactive visualization.

Through this collaborative project, we gained practical experience in transforming raw sports data into structured datasets and presenting meaningful insights through an interactive web application.

---

**Project:** Game Analytics – Unlocking Tennis Data with SportRadar API

**Project Type:** Team Project

**Domain:** Sports & Data Analytics

**Team Size:** 4 Members

**Live Dashboard:** https://tennis-performance-analytics.streamlit.app/
