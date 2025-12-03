---
description: Executive Dashboard Development & Maintenance
---

# Executive Dashboard 2.0 - Development Workflow

This workflow documents the complete process for developing, testing, and maintaining the AI Command Center Executive Dashboard.

## Prerequisites

- Node.js 18+ installed
- Python 3.8+ installed
- Git for version control

## Initial Setup

// turbo-all
1. **Clone Repository**
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
   pip install -r requirements.txt
   ```

## Development Workflow

### Starting Development Servers

// turbo
1. **Start Backend Server**
   ```bash
   cd backend
   .\.venv\Scripts\python.exe -m uvicorn main:app --reload
   ```
   - Server runs on: http://localhost:8000
   - API docs: http://localhost:8000/docs

// turbo
2. **Start Frontend Server**
   ```bash
   cd frontend
   npm run dev
   ```
   - Dashboard runs on: http://localhost:3000

### Making Changes

1. **Component Development**
   - All components in `frontend/components/`
   - Use TypeScript for type safety
   - Add JSDoc documentation
   - Include ARIA labels for accessibility

2. **Utility Functions**
   - Place in `frontend/utils/`
   - Export with proper TypeScript types
   - Document with JSDoc

3. **Styling**
   - Use Tailwind CSS classes
   - Follow semantic color scheme:
     - Green (#10b981) - Revenue
     - Blue (#3b82f6) - Profit
     - Red (#f43f5e) - Expenses
     - Amber (#f59e0b) - Products
     - Purple (#8b5cf6) - Salesmen

### Testing Changes

1. **Visual Verification**
   - Open http://localhost:3000
   - Check all KPI cards display correctly
   - Verify charts render properly
   - Test responsive design (mobile, tablet, desktop)

2. **Console Check**
   - Open browser DevTools (F12)
   - Verify no errors in Console
   - Check Network tab for API calls

3. **Accessibility Check**
   - Use browser accessibility tools
   - Verify keyboard navigation works
   - Check screen reader compatibility

### Code Quality

1. **TypeScript**
   - No `any` types unless absolutely necessary
   - Proper interface definitions
   - Export types for reusability

2. **Documentation**
   - JSDoc for all functions and components
   - Inline comments for complex logic
   - README updates for major changes

3. **Performance**
   - Optimize images
   - Lazy load components when possible
   - Minimize re-renders

## Deployment

### Build Production

// turbo
1. **Build Frontend**
   ```bash
   cd frontend
   npm run build
   npm start
   ```

2. **Test Production Build**
   - Verify at http://localhost:3000
   - Check for build errors
   - Test all functionality

### Environment Variables

Create `.env.local` in frontend:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Create `.env` in backend:
```
GEMINI_API_KEY=your_api_key_here
DATABASE_URL=sqlite:///./command_center.db
```

## Troubleshooting

### Common Issues

1. **Hydration Errors**
   - Check for client/server rendering mismatches
   - Verify className consistency
   - Ensure proper Next.js app structure

2. **Chart Not Rendering**
   - Check data format matches interface
   - Verify ResponsiveContainer has height
   - Check console for Recharts warnings

3. **API Connection Failed**
   - Verify backend server is running
   - Check CORS settings in main.py
   - Verify API URL in frontend

### Debug Commands

```bash
# Check backend logs
cd backend
.\.venv\Scripts\python.exe -m uvicorn main:app --reload --log-level debug

# Check frontend build
cd frontend
npm run build -- --debug

# Clear Next.js cache
rm -rf .next
npm run dev
```

## Best Practices

1. **Always verify changes in browser before committing**
2. **Run TypeScript check before push**: `npm run type-check`
3. **Keep dependencies updated**: `npm outdated`
4. **Document breaking changes in CHANGELOG.md**
5. **Use semantic commit messages**
6. **Test on multiple browsers (Chrome, Firefox, Safari)**

## File Structure

```
ai-command-center/
├── frontend/
│   ├── app/
│   │   ├── page.tsx          # Main dashboard
│   │   ├── layout.tsx        # Root layout
│   │   └── globals.css       # Global styles
│   ├── components/
│   │   ├── KPICard.tsx       # KPI card component
│   │   └── ChatWidget.tsx    # AI chat widget
│   ├── utils/
│   │   └── format.ts         # Formatting utilities
│   └── public/
│       └── favicon.svg       # App icon
├── backend/
│   ├── main.py               # FastAPI server
│   ├── database.py           # Database models
│   └── requirements.txt      # Python dependencies
└── .agent/
    └── workflows/
        └── dashboard-workflow.md  # This file
```

## Maintenance Schedule

- **Daily**: Check error logs
- **Weekly**: Review performance metrics
- **Monthly**: Update dependencies
- **Quarterly**: Security audit

## Support

For issues or questions:
1. Check this workflow document
2. Review component documentation
3. Check browser console for errors
4. Contact development team

---
Last Updated: 2025-12-03
Version: 2.0.0
