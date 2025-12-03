# AI Command Center - Executive Dashboard 2.0

A premium, real-time business intelligence dashboard featuring full number display, trend indicators, and AI-powered analytics.

![Dashboard Version](https://img.shields.io/badge/version-2.0.0-blue)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue)
![Next.js](https://img.shields.io/badge/Next.js-Latest-black)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green)

## ✨ Features

### 📊 Executive Dashboard
- **Full Number Display**: Shows complete currency values (e.g., 225.700.000.000 ₫) without truncation
- **Trend Indicators**: Visual growth badges with up/down arrows and percentage changes
- **Semantic Color Coding**: 
  - 🟢 Green for Revenue (positive income)
  - 🔵 Blue for Profit
  - 🔴 Red for Marketing Spend (expenses)
  - 🟡 Amber for Products
  - 🟣 Purple for Salesmen

### 📈 Interactive Charts
- **Monthly Revenue & Profit Trend**: Bar chart with full tooltips
- **Revenue by Channel**: Pie chart distribution
- **Top 5 Products**: Horizontal bar chart
- **Top 5 Salesmen**: Performance rankings

### 🤖 AI Analytics
- **Chat Widget**: AI-powered business intelligence assistant
- **Context-Aware**: Understands your data and provides insights
- **Natural Language**: Ask questions in plain language

### ♿ Accessibility
- ARIA labels for screen readers
- Keyboard navigation support
- Semantic HTML structure
- WCAG 2.1 compliant

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ 
- Python 3.8+
- npm or yarn

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-command-center
   ```

2. **Install Frontend Dependencies**
   ```bash
   cd frontend
   npm install
   ```

3. **Install Backend Dependencies**
   ```bash
   cd ../backend
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # or
   source .venv/bin/activate  # Mac/Linux
   pip install -r requirements.txt
   ```

### Running the Application

1. **Start Backend Server**
   ```bash
   cd backend
   .\.venv\Scripts\python.exe -m uvicorn main:app --reload
   ```
   Server runs on: http://localhost:8000

2. **Start Frontend Server** (in a new terminal)
   ```bash
   cd frontend
   npm run dev
   ```
   Dashboard runs on: http://localhost:3000

3. **Open Dashboard**
   Navigate to http://localhost:3000 in your browser

## 📁 Project Structure

```
ai-command-center/
├── frontend/                 # Next.js frontend application
│   ├── app/
│   │   ├── page.tsx         # Main dashboard page
│   │   ├── layout.tsx       # Root layout with metadata
│   │   └── globals.css      # Global styles
│   ├── components/
│   │   ├── KPICard.tsx      # Premium KPI card component
│   │   └── ChatWidget.tsx   # AI chat interface
│   ├── utils/
│   │   └── format.ts        # Currency formatting utilities
│   └── public/
│       └── favicon.svg      # Application icon
├── backend/                  # FastAPI backend server
│   ├── main.py              # API routes and business logic
│   ├── database.py          # SQLAlchemy models
│   ├── requirements.txt     # Python dependencies
│   └── command_center.db    # SQLite database
└── .agent/
    └── workflows/
        └── dashboard-workflow.md  # Development workflow
```

## 🎨 Design System

### Color Palette
```typescript
const CHART_COLORS = {
  revenue: '#10b981',    // Emerald - Revenue
  profit: '#3b82f6',     // Blue - Profit
  marketing: '#f43f5e',  // Rose - Marketing Spend
  products: '#f59e0b',   // Amber - Products
  salesmen: '#8b5cf6',   // Purple - Salesmen
  channels: ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d']
};
```

### Typography
- **Headings**: System font stack with gradient text effects
- **Body**: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto'
- **Numbers**: Tracking-tight for better readability

### Spacing
- **Grid Gap**: 1.5rem (24px)
- **Card Padding**: 1.5rem (24px)
- **Container**: Max-width 1280px (7xl)

## 🔧 Configuration

### Environment Variables

**Frontend** (`.env.local`):
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Backend** (`.env`):
```env
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=sqlite:///./command_center.db
```

## 📊 Data Upload

1. Click "Upload Excel Data" button in the dashboard
2. Select your Excel file (.xlsx or .xls)
3. Data will be processed and dashboard will update automatically

### Expected Excel Format
- **Year**: Fiscal year
- **Month number**: 1-12
- **Month**: Month name
- **Net Value**: Revenue amount
- **Dist**: Distribution channel
- **Branch**: Branch name
- **Salesman Name**: Sales representative
- **PH3**: Product group
- **Description**: Product description
- **Name of Bill to**: Customer name

## 🧪 Testing

### Manual Testing
```bash
# Open browser DevTools (F12)
# Check Console for errors
# Verify all charts render
# Test responsive design
```

### Type Checking
```bash
cd frontend
npm run type-check
```

### Build Test
```bash
cd frontend
npm run build
npm start
```

## 📚 API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

- `GET /api/dashboard` - Get dashboard data
- `POST /api/upload` - Upload Excel file
- `POST /api/chat` - Chat with AI analyst

## 🎯 Best Practices

### Code Quality
- ✅ TypeScript strict mode enabled
- ✅ JSDoc documentation for all functions
- ✅ ESLint configured
- ✅ Prettier for code formatting

### Performance
- ✅ Lazy loading for components
- ✅ Optimized images
- ✅ Minimal re-renders with React.memo
- ✅ Efficient data fetching

### Accessibility
- ✅ ARIA labels on all interactive elements
- ✅ Keyboard navigation support
- ✅ Screen reader compatible
- ✅ Color contrast WCAG AA compliant

## 🐛 Troubleshooting

### Common Issues

**Charts not rendering?**
- Check browser console for errors
- Verify data format matches interfaces
- Ensure ResponsiveContainer has height

**API connection failed?**
- Verify backend server is running on port 8000
- Check CORS settings in main.py
- Verify API URL in frontend config

**Hydration errors?**
- Clear Next.js cache: `rm -rf .next`
- Restart dev server
- Check for client/server rendering mismatches

### Debug Mode

```bash
# Backend with debug logging
cd backend
.\.venv\Scripts\python.exe -m uvicorn main:app --reload --log-level debug

# Frontend with debug
cd frontend
npm run dev -- --debug
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Commit Convention
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes
- `refactor:` Code refactoring
- `test:` Test updates
- `chore:` Build/tooling changes

## 📄 License

This project is licensed under the MIT License.

## 👥 Team

**AI Command Center Team**
- Executive Dashboard Development
- Business Intelligence Analytics
- AI Integration

## 📞 Support

For issues or questions:
1. Check the [Workflow Documentation](.agent/workflows/dashboard-workflow.md)
2. Review component JSDoc comments
3. Check browser console for errors
4. Contact the development team

---

**Version**: 2.0.0  
**Last Updated**: December 3, 2025  
**Status**: ✅ Production Ready

Built with ❤️ using Next.js, FastAPI, and Google Gemini AI