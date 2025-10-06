# Implementation Plan

- [x] 1. Set up project structure and development environment

  - Create ASP.NET Core Web API project with proper folder structure
  - Set up Vue.js project with Quasar framework
  - Configure Entity Framework Core with SQLite
  - Set up development tools and build configuration
  - _Requirements: 5.1, 5.2_

- [ ] 2. Implement core data models and database setup

  - [x] 2.1 Create Entity Framework models for Recipe, Ingredient, and related entities

    - Define Recipe, Ingredient, SourceMetadata C# classes with EF annotations
    - Create enums for IngredientCategory, RecipeSource, and MealType
    - Write unit tests for model validation and relationships
    - _Requirements: 1.3, 2.2, 5.2_

  - [x] 2.2 Create Entity Framework models for meal planning

    - Define MealPlan, DailyMeals, ShoppingList C# classes
    - Set up proper relationships between recipes and meal plans
    - Write unit tests for meal planning model constraints
    - _Requirements: 3.2, 4.1_

  - [x] 2.3 Set up database context and initial migration
    - Create ApplicationDbContext with DbSets for all entities
    - Configure entity relationships and constraints
    - Generate and apply initial database migration
    - Write integration tests for database operations
    - _Requirements: 5.2, 5.3_

- [ ] 3. Implement PDF processing and recipe parsing

  - [x] 3.1 Create PDF text extraction service

    - Implement IPdfTextExtractor interface using iTextSharp or PdfPig
    - Handle PDF file validation and error cases
    - Write unit tests with sample PDF files
    - _Requirements: 1.1, 1.4_

  - [x] 3.2 Implement recipe parsing logic

    - Create IRecipeParser interface to extract recipe components from text
    - Implement parsing algorithms for title, ingredients, and instructions
    - Handle various recipe formats and edge cases
    - Write comprehensive unit tests with different recipe text formats
    - _Requirements: 1.2, 1.4_

  - [x] 3.3 Create recipe import service
    - Implement IRecipeService.ImportFromPdfAsync method
    - Integrate PDF extraction with recipe parsing
    - Add validation and error handling for import process
    - Write integration tests for complete PDF import workflow
    - _Requirements: 1.1, 1.2, 1.3, 1.5_

- [ ] 4. Implement recipe repository and CRUD operations

  - [x] 4.1 Create recipe repository with Entity Framework

    - Implement IRecipeRepository interface with CRUD operations
    - Add methods for searching and filtering recipes
    - Implement proper error handling and validation
    - Write unit tests for all repository methods
    - _Requirements: 2.1, 2.4, 5.4_

  - [x] 4.2 Implement recipe service layer
    - Create RecipeService class implementing IRecipeService
    - Add business logic for recipe management operations
    - Implement search functionality with filtering capabilities
    - Write unit tests for service layer methods
    - _Requirements: 2.1, 2.2, 2.4_

- [ ] 5. Create Web API controllers for recipe management

  - [x] 5.1 Implement recipe upload and import API endpoint

    - Create RecipeController with POST endpoint for PDF upload
    - Add file validation and size limits
    - Implement proper error responses and status codes
    - Write integration tests for upload endpoint
    - _Requirements: 1.1, 1.4, 1.5_

  - [x] 5.2 Implement recipe CRUD API endpoints
    - Add GET, PUT, DELETE endpoints for recipe management
    - Implement search endpoint with query parameters
    - Add proper request/response DTOs
    - Write integration tests for all CRUD endpoints
    - _Requirements: 2.1, 2.2, 2.4, 2.5_

- [ ] 6. Implement meal planning functionality

  - [x] 6.1 Create meal planning repository and service

    - Implement IMealPlanRepository with Entity Framework
    - Create MealPlanningService with business logic
    - Add methods for weekly meal plan management
    - Write unit tests for meal planning operations
    - _Requirements: 3.1, 3.2, 3.4_

  - [x] 6.2 Implement meal planning API endpoints
    - Create MealPlanController with endpoints for meal assignment
    - Add GET endpoint for retrieving weekly meal plans
    - Implement PUT/DELETE for modifying meal assignments
    - Write integration tests for meal planning API
    - _Requirements: 3.1, 3.2, 3.3, 3.5_

- [ ] 7. Implement shopping list generation

  - [x] 7.1 Create shopping list service

    - Implement ingredient consolidation logic
    - Add categorization of ingredients by type
    - Create methods for generating shopping lists from meal plans
    - Write unit tests for ingredient consolidation algorithms
    - _Requirements: 4.1, 4.2, 4.3, 4.5_

  - [x] 7.2 Implement shopping list API endpoint
    - Add GET endpoint for generating shopping lists by date range
    - Implement PUT endpoint for marking items as purchased
    - Add proper response formatting for categorized lists
    - Write integration tests for shopping list generation
    - _Requirements: 4.1, 4.3, 4.4_

- [ ] 8. Set up Vue.js frontend with Quasar

  - [x] 8.1 Create Vue.js project structure with Quasar

    - Initialize Vue 3 project with Quasar CLI
    - Set up TypeScript configuration and component structure
    - Configure routing with Vue Router
    - Set up state management with Pinia
    - _Requirements: 2.1, 3.1_

  - [x] 8.2 Create API service layer for frontend
    - Implement HTTP client service using Axios
    - Create typed API service classes for recipes and meal planning
    - Add error handling and response interceptors
    - Write unit tests for API service methods
    - _Requirements: 1.5, 2.5, 3.4_

- [ ] 9. Implement recipe management UI components

  - [x] 9.1 Create PDF upload component

    - Build file upload interface using Quasar components
    - Add drag-and-drop functionality and progress indicators
    - Implement upload validation and error display
    - Write component tests for upload functionality
    - _Requirements: 1.1, 1.4, 1.5_

  - [x] 9.2 Create recipe collection and search interface

    - Build recipe list component with search and filtering
    - Implement recipe card display with categories and tags
    - Add pagination for large recipe collections
    - Write component tests for recipe browsing functionality
    - _Requirements: 2.1, 2.2, 2.4, 2.5_

  - [x] 9.3 Create recipe detail view and editing
    - Build detailed recipe display component
    - Implement recipe editing form with validation
    - Add category and tag management interface
    - Write component tests for recipe detail functionality
    - _Requirements: 2.2, 2.5_

- [ ] 10. Implement meal planning UI components

  - [x] 10.1 Create weekly calendar component

    - Build calendar interface using Quasar date components
    - Implement drag-and-drop for recipe assignment
    - Add meal slot management (breakfast, lunch, dinner)
    - Write component tests for calendar functionality
    - _Requirements: 3.1, 3.2, 3.3_

  - [x] 10.2 Create recipe selection and assignment interface

    - Build recipe picker modal with search functionality
    - Implement meal assignment and removal actions
    - Add visual feedback for meal planning operations
    - Write component tests for meal assignment workflow
    - _Requirements: 3.2, 3.4, 3.5_

  - [x] 10.3 Fix Add Meal dialog behavior and state management
    - Ensure dialog closes properly after successful meal assignment
    - Prevent dialog from reopening automatically after adding a meal
    - Implement proper loading states to prevent duplicate submissions
    - Add proper dialog state reset when opening/closing
    - Write tests for dialog behavior edge cases
    - _Requirements: 3.6, 3.7_

- [ ] 11. Implement shopping list UI components

  - [x] 11.1 Create shopping list generation interface

    - Build date range picker for shopping list generation
    - Implement categorized shopping list display
    - Add checkboxes for marking items as purchased
    - Write component tests for shopping list functionality
    - _Requirements: 4.1, 4.3, 4.4_

  - [x] 11.2 Add shopping list management features
    - Implement meal-based shopping list layout (breakfast/lunch/dinner structure)
    - Add manual item addition to shopping lists
    - Create shopping list history and management
    - Add authentication support with test mode for empty states
    - _Requirements: 4.3, 4.4_

- [ ] 12. Integrate frontend and backend with end-to-end testing

  - [ ] 12.1 Connect all frontend components to API endpoints

    - Wire up recipe upload flow with backend processing
    - Connect meal planning interface to meal planning API
    - Integrate shopping list generation with backend service
    - Test complete user workflows end-to-end
    - _Requirements: 1.1, 1.2, 1.3, 1.5, 2.1, 2.2, 2.4, 2.5, 3.1, 3.2, 3.4, 3.5, 4.1, 4.3, 4.4_

  - [ ] 12.2 Add error handling and user feedback
    - Implement global error handling in Vue.js application
    - Add loading states and progress indicators
    - Create user-friendly error messages and notifications
    - Write tests for error scenarios and edge cases
    - _Requirements: 1.4, 1.5_
