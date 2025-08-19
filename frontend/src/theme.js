import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: { main: '#2563eb', light: '#3b82f6', dark: '#1d4ed8' },
    secondary: { main: '#7c3aed', light: '#8b5cf6', dark: '#6d28d9' },
    success: { main: '#059669', light: '#10b981', dark: '#047857' },
    error: { main: '#dc2626', light: '#ef4444', dark: '#b91c1c' },
    warning: { main: '#d97706', light: '#f59e0b', dark: '#b45309' },
    background: { default: '#f8fafc', paper: '#ffffff' },
    text: { primary: '#1e293b', secondary: '#64748b' },
  },
  typography: {
    fontFamily:
      '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    h1: { fontWeight: 700, fontSize: '2.5rem', lineHeight: 1.2 },
    h3: { fontWeight: 600, fontSize: '1.875rem', lineHeight: 1.3 },
    h4: { fontWeight: 600, fontSize: '1.5rem', lineHeight: 1.4 },
    h6: { fontWeight: 500, fontSize: '1.125rem', lineHeight: 1.4 },
    body1: { fontSize: '1rem', lineHeight: 1.6 },
    body2: { fontSize: '0.875rem', lineHeight: 1.5 },
  },
  shape: { borderRadius: 16 },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 20,
          border: '1px solid #e2e8f0',
          boxShadow:
            '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          '&:hover': {
            boxShadow:
              '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
            transform: 'translateY(-2px)',
          },
        },
      },
    },
    MuiCardHeader: {
      styleOverrides: {
        root: {
          padding: '24px 24px 16px 24px',
          '& .MuiCardHeader-title': {
            fontSize: '1.125rem',
            fontWeight: 600,
            color: '#1e293b',
          },
          '& .MuiCardHeader-subheader': {
            fontSize: '0.875rem',
            color: '#64748b',
            marginTop: '4px',
          },
        },
        avatar: { marginRight: 16 },
      },
    },
    MuiCardContent: {
      styleOverrides: {
        root: { padding: '0 24px 24px 24px', '&:last-child': { paddingBottom: 24 } },
      },
    },
    MuiChip: { styleOverrides: { root: { borderRadius: 12, fontWeight: 500 } } },
    MuiLinearProgress: {
      styleOverrides: { root: { borderRadius: 8, height: 10 } },
    },
  },
});

export default theme;
