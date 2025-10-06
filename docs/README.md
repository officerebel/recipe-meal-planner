# Recipe Meal Planner

A comprehensive application for importing recipes from PDF files, organizing recipe collections, planning meals, and generating shopping lists.

## Project Structure

```
├── RecipeMealPlanner.Api/          # ASP.NET Core Web API Backend
│   ├── Controllers/                # API Controllers
│   ├── Data/                      # Entity Framework DbContext
│   ├── Models/                    # Entity Framework Models
│   ├── Repositories/              # Data Access Layer
│   ├── Services/                  # Business Logic Layer
│   └── Program.cs                 # Application entry point
│
├── recipe-meal-planner/           # Vue.js + Quasar Frontend
│   ├── src/
│   │   ├── components/           # Vue Components
│   │   ├── layouts/              # Page Layouts
│   │   ├── pages/                # Page Components
│   │   ├── router/               # Vue Router Configuration
│   │   └── css/                  # Stylesheets
│   ├── quasar.config.js          # Quasar Configuration
│   └── package.json              # Frontend Dependencies
│
└── .kiro/specs/recipe-meal-planner/  # Project Specification
    ├── requirements.md           # Feature Requirements
    ├── design.md                # System Design
    └── tasks.md                 # Implementation Tasks
```

## Technology Stack

### Backend
- **Framework**: ASP.NET Core 9.0
- **Database**: SQLite with Entity Framework Core
- **PDF Processing**: iTextSharp or PdfPig (to be implemented)

### Frontend
- **Framework**: Vue.js 3 with Composition API
- **UI Library**: Quasar Framework
- **HTTP Client**: Axios
- **State Management**: Pinia
- **Build Tool**: Vite

## Development Setup

### Prerequisites
- .NET 9.0 SDK
- Node.js (v18 or higher)
- npm

### Backend Setup
```bash
cd RecipeMealPlanner.Api
dotnet restore
dotnet build
dotnet run
```

### Frontend Setup
```bash
cd recipe-meal-planner
npm install
npm run dev
```

## Development Ports
- Backend API: https://localhost:5001 (or http://localhost:5000)
- Frontend App: http://localhost:9000

## Next Steps

Follow the implementation tasks in `.kiro/specs/recipe-meal-planner/tasks.md` to build out the application features:

1. Implement core data models and database setup
2. Add PDF processing and recipe parsing
3. Create recipe management APIs
4. Build meal planning functionality
5. Implement shopping list generation
6. Create Vue.js UI components
7. Connect frontend to backend APIs

## Features (Planned)

- 📄 Import recipes from PDF files
- 📚 Organize and search recipe collection
- 📅 Weekly meal planning calendar
- 🛒 Generate consolidated shopping lists
- 🏷️ Recipe categorization and tagging
- 🔍 Advanced recipe search and filtering