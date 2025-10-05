# Design Document

## Overview

The Recipe Meal Planner is a web-based application that enables users to import recipes from PDF files, organize their recipe collection, plan meals on a weekly calendar, and generate shopping lists. The system is designed with a modular architecture to support future expansion to database-driven recipe sources.

## Architecture

The application follows a layered architecture with clear separation of concerns:

```
┌─────────────────────────────────────────┐
│      Frontend (React/Vue.js)           │
├─────────────────────────────────────────┤
│      Web API (ASP.NET Core)             │
├─────────────────────────────────────────┤
│        Business Logic Layer             │
│  ┌─────────────┐  ┌─────────────────┐   │
│  │   Recipe    │  │   Meal Planning │   │
│  │   Service   │  │    Service      │   │
│  └─────────────┘  └─────────────────┘   │
├─────────────────────────────────────────┤
│         Data Access Layer               │
│  ┌─────────────┐  ┌─────────────────┐   │
│  │   Recipe    │  │   Meal Plan     │   │
│  │ Repository  │  │   Repository    │   │
│  └─────────────┘  └─────────────────┘   │
├─────────────────────────────────────────┤
│   Storage Layer (SQLite + EF Core)      │
└─────────────────────────────────────────┘
```

### Technology Stack

- **Frontend**: React or Vue.js with TypeScript for type safety
- **Backend**: ASP.NET Core with C#
- **Database**: SQLite with Entity Framework Core (easily upgradeable to SQL Server/PostgreSQL)
- **PDF Processing**: iTextSharp or PdfPig library for text extraction
- **UI Components**: Material-UI (React) or Quasar (Vue.js)
- **State Management**: React Context API/Redux Toolkit (React) or Pinia (Vue.js)

## Components and Interfaces

### Core Components

#### 1. PDF Import Component
- **Purpose**: Handle PDF file upload and processing
- **Key Methods**:
  - `uploadPDF(file: File): Promise<Recipe>`
  - `extractText(pdfBuffer: Buffer): Promise<string>`
  - `parseRecipe(text: string): Promise<Recipe>`

#### 2. Recipe Parser
- **Purpose**: Extract structured recipe data from text
- **Key Methods**:
  - `parseTitle(text: string): string`
  - `parseIngredients(text: string): Ingredient[]`
  - `parseInstructions(text: string): string[]`
  - `parseMetadata(text: string): RecipeMetadata`

#### 3. Recipe Collection Component
- **Purpose**: Display and manage recipe library
- **Key Methods**:
  - `getRecipes(filters?: RecipeFilters): Promise<Recipe[]>`
  - `searchRecipes(query: string): Promise<Recipe[]>`
  - `categorizeRecipe(recipeId: string, category: string): Promise<void>`

#### 4. Meal Planning Calendar
- **Purpose**: Weekly meal planning interface
- **Key Methods**:
  - `getMealPlan(weekStart: Date): Promise<MealPlan>`
  - `assignRecipe(date: Date, mealType: MealType, recipeId: string): Promise<void>`
  - `removeRecipe(date: Date, mealType: MealType): Promise<void>`
- **UI Behavior**:
  - Add meal dialog should close immediately after successful meal assignment
  - Dialog state should be properly reset to prevent automatic reopening
  - Loading states should prevent duplicate submissions during meal assignment

#### 5. Shopping List Generator
- **Purpose**: Generate consolidated shopping lists
- **Key Methods**:
  - `generateShoppingList(dateRange: DateRange): Promise<ShoppingList>`
  - `consolidateIngredients(ingredients: Ingredient[]): ConsolidatedIngredient[]`
  - `categorizeIngredients(ingredients: ConsolidatedIngredient[]): CategorizedShoppingList`

### Service Layer Interfaces

```csharp
public interface IRecipeService
{
    Task<Recipe> ImportFromPdfAsync(IFormFile file);
    Task<string> SaveRecipeAsync(Recipe recipe);
    Task<Recipe> GetRecipeAsync(string id);
    Task<IEnumerable<Recipe>> SearchRecipesAsync(string query, RecipeFilters filters = null);
    Task UpdateRecipeAsync(string id, Recipe updates);
    Task DeleteRecipeAsync(string id);
}

public interface IMealPlanningService
{
    Task<MealPlan> GetMealPlanAsync(DateTime weekStart);
    Task AssignMealAsync(DateTime date, MealType mealType, string recipeId);
    Task RemoveMealAsync(DateTime date, MealType mealType);
    Task<ShoppingList> GenerateShoppingListAsync(DateRange dateRange);
}
```

## Data Models

### Recipe Model
```csharp
public class Recipe
{
    public string Id { get; set; }
    public string Title { get; set; }
    public List<Ingredient> Ingredients { get; set; }
    public List<string> Instructions { get; set; }
    public int? Servings { get; set; }
    public int? PrepTime { get; set; }
    public int? CookTime { get; set; }
    public List<string> Categories { get; set; }
    public List<string> Tags { get; set; }
    public RecipeSource Source { get; set; }
    public SourceMetadata SourceMetadata { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime UpdatedAt { get; set; }
}

public class Ingredient
{
    public string Name { get; set; }
    public decimal? Quantity { get; set; }
    public string Unit { get; set; }
    public IngredientCategory? Category { get; set; }
}

public enum IngredientCategory
{
    Produce,
    Dairy,
    Meat,
    Pantry,
    Spices,
    Other
}

public enum RecipeSource
{
    Pdf,
    Database,
    Manual
}

public class SourceMetadata
{
    public string Filename { get; set; }
    public DateTime ImportDate { get; set; }
}
```

### Meal Planning Models
```csharp
public class MealPlan
{
    public DateTime WeekStart { get; set; }
    public List<DailyMeals> Meals { get; set; }
}

public class DailyMeals
{
    public DateTime Date { get; set; }
    public string Breakfast { get; set; } // Recipe ID
    public string Lunch { get; set; }
    public string Dinner { get; set; }
    public List<string> Snacks { get; set; }
}

public enum MealType
{
    Breakfast,
    Lunch,
    Dinner,
    Snack
}
```

### Shopping List Models
```csharp
public class ShoppingList
{
    public DateRange DateRange { get; set; }
    public Dictionary<string, List<ConsolidatedIngredient>> Items { get; set; }
    public DateTime GeneratedAt { get; set; }
}

public class ConsolidatedIngredient
{
    public string Name { get; set; }
    public decimal TotalQuantity { get; set; }
    public string Unit { get; set; }
    public List<string> Sources { get; set; } // Recipe names
    public bool Purchased { get; set; }
}

public class DateRange
{
    public DateTime StartDate { get; set; }
    public DateTime EndDate { get; set; }
}
```

## Error Handling

### PDF Processing Errors
- **Invalid PDF Format**: Display user-friendly error with suggestion to check file format
- **Text Extraction Failure**: Provide fallback option for manual recipe entry
- **Parsing Errors**: Allow users to review and edit parsed recipe before saving

### Data Validation
- **Recipe Validation**: Ensure required fields (title, ingredients) are present
- **Date Validation**: Validate meal planning dates and ranges
- **File Size Limits**: Implement reasonable PDF file size restrictions

### Error Recovery
- **Graceful Degradation**: If PDF parsing fails partially, save what was successfully parsed
- **Retry Mechanisms**: Allow users to retry failed operations
- **Data Backup**: Implement local storage backup for critical user data

## Testing Strategy

### Unit Testing
- **Recipe Parser**: Test with various PDF formats and recipe structures
- **Data Models**: Validate model constraints and relationships
- **Service Layer**: Mock dependencies and test business logic
- **Utility Functions**: Test ingredient consolidation and categorization

### Integration Testing
- **PDF Processing Pipeline**: End-to-end testing of PDF import workflow
- **Database Operations**: Test CRUD operations for recipes and meal plans
- **API Endpoints**: Test all REST API endpoints with various inputs

### User Acceptance Testing
- **Recipe Import Flow**: Test with real PDF recipes of different formats
- **Meal Planning Workflow**: Test complete meal planning and shopping list generation
- **Add Meal Dialog Behavior**: Verify dialog closes properly after meal assignment and doesn't reopen unexpectedly
- **Cross-browser Compatibility**: Ensure functionality across major browsers

### Performance Testing
- **PDF Processing**: Test with large PDF files and complex recipes
- **Search Performance**: Test recipe search with large collections
- **Calendar Rendering**: Test meal planning calendar with extensive data

## Future Extensibility

### Database Integration Preparation
- **Repository Pattern**: Abstract data access to support multiple storage backends
- **Recipe Source Abstraction**: Design interfaces to support multiple recipe sources
- **Data Migration**: Plan for migrating PDF-imported recipes to database format

### Scalability Considerations
- **Caching Strategy**: Implement caching for frequently accessed recipes
- **Pagination**: Design for handling large recipe collections
- **Search Optimization**: Prepare for full-text search capabilities

### Additional Features
- **Recipe Sharing**: Design user model to support recipe sharing between users
- **Nutritional Information**: Plan data model extensions for nutritional data
- **Recipe Scaling**: Design ingredient model to support automatic recipe scaling